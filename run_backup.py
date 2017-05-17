#!/usr/bin/env python
"""
Main Backup Script
"""


### INCLUDES ###
import os
import sys
import commands
# import platform
import optparse
import glob

from py_knife import file_system
from py_knife.ordered_dict import OrderedDict
from py_knife.database import DatabaseOrderedDict
from py_knife.logger import Logger

from vmware_backup import DEFAULT_SETTINGS, FOLDER_TS_FORMAT, MUTLIPLE_TAPE_SYSTEM
from vmware_backup import execute_backup, enable_backup, disable_backup


### CONSTANTS ###
## Module Constants ##
CWD = sys.path[0]
BACKUP_COMMAND = 'python ' + os.path.join(CWD, 'run_backup.py') + ' -b'


### FUNCTIONS ###
## OPTION PARSER ##
def parse_input_options(allow_time_stamp_mods=True):
    """ Parse input options """
    parser = optparse.OptionParser()

    parser.add_option('-e', '--enable', dest='enable_backup', action='store_true', default=False,
                      help='Enable backup. Make sure all of the backup '
                            'settings are correct before executing this!')

    parser.add_option('-d', '--disable', dest='disable_backup', action='store_true', default=False,
                      help='Disable backup')

    parser.add_option('-p', '--print_settings', dest='print_settings', action='store_true', default=False,
                      help='Print current backup settings')

    backup_group = optparse.OptionGroup(parser, 'Backup Settings')
    backup_group.add_option('-s', '--schedule', dest='crone_schedule', type='str', default=None,
                            help='Set backup schedule. Use crontab format. '
                                 'Refer to "man 5 crontab" for more information')
    backup_group.add_option('-r', '--vmrun', dest='vmrun_path', type='str', default=None,
                            help='Change path to vmrun')
    backup_group.add_option('-v', '--vms', dest='vms_path', type='str', default=None,
                            help='Change path to target virtual machines')
    backup_group.add_option('-t', '--tape', dest='tape_path', type='str', default=None,
                            help='Change path to backup tapes')

    if allow_time_stamp_mods:
        backup_group.add_option('-f', '--folder_ts', dest='folder_ts_format', type='str', default=None,
                                help='Change folder time stamp format (Not recommended). Refer to '
                                     '"https://docs.python.org/2/library/time.html#time.strftime"')
        backup_group.add_option('-l', '--log_ts', dest='log_ts_format', type='str', default=None,
                                help='Change log time stamp format (Not recommended). Refer to '
                                     '"https://docs.python.org/2/library/time.html#time.strftime"')
    parser.add_option_group(backup_group)

    debug_group = optparse.OptionGroup(parser, 'Debug Options', 'This options are meant to be used internally. '
                                                                'Please, use those for testing purposes only!')
    debug_group.add_option('-b', '--backup', dest='back_up', action='store_true', default=False,
                           help='Run backup manually, here and now!')
    parser.add_option_group(debug_group)

    (options, args) = parser.parse_args()

    return options


## SETTINGS VALIDATOR ##
# Validation Script #
def validate_settings(current_settings, new_settings=None):
    """ Validate Backup Settings Routine """
    key_error_pairs = {
        'crone_schedule': ('Schedule string "', '" is in incompatible format!'),
        'vmrun_path': ('Can not reach VMWare vmrun command under "', '" location!'),
        'vms_path': ('No virtual machines under "', '" location!'),
        'tape_path': ('No backup tapes under "', '" location!'),
        'folder_ts_format': ('', ''),
        'log_ts_format': ('', '')
    }

    if new_settings is None:
        # Do not save results
        # print '*** Validating Saved Settings ***'
        _settings = current_settings
    else:
        # Save results
        # print '*** Validating Input Settings***'
        _settings = new_settings

    error_message = None
    output = None
    for _settings_key, _settings_error in key_error_pairs.items():
        if _hasattr(_settings, _settings_key):
            # Get input value
            _settings_value = str(_getattr(_settings, _settings_key))
            # print 'settings_key = ', _settings_key
            # print 'settings_value = ', _settings_value

            if '_path' in _settings_key:
                # Validate path options, strip forward slashes if needed
                _settings_value = _settings_value.rstrip(os.sep)
                if _settings_key == 'vmrun_path':
                    vmrun_test_list = commands.getoutput(_settings_value).split('\n')
                    for vmrun_test_line in vmrun_test_list:
                        if 'vmrun version' in vmrun_test_line:
                            current_settings[_settings_key] = _settings_value
                            output = True
                            break
                    else:
                        output = False

                else:
                    validate = os.path.isdir(_settings_value)
                    if _settings_key != 'tape_path' or MUTLIPLE_TAPE_SYSTEM:
                        validate &= bool(len(glob.glob(os.path.join(_settings_value, '*'))) > 0)

                    if validate:
                        current_settings[_settings_key] = _settings_value

                    output = validate

            elif '_ts_format' in _settings_key:
                if new_settings is not None:
                    # Save format options
                    current_settings[_settings_key] = _settings_value
                    output = True

            elif _settings_key == 'crone_schedule':
                crone_limits = [(0, 59), (0, 23), (1, 31), (1, 12), (0, 6)]
                crone_input_list = _settings_value.split()
                if len(crone_input_list) == len(crone_limits):
                    for crone_index, crone_digit in enumerate(crone_input_list):
                        crone_min = crone_limits[crone_index][0]
                        cron_max = crone_limits[crone_index][1]

                        if crone_digit == '*':
                            continue

                        if crone_digit.isdigit():
                            if crone_min <= int(crone_digit) <= cron_max:
                                continue

                        if '-' in crone_digit:
                            crone_range = crone_digit.split('-')
                            if len(crone_range) == 2 and crone_range[0].isdigit() and crone_range[1].isdigit():
                                if crone_min <= int(crone_range[0]) < int(crone_range[1]) <= cron_max:
                                    continue

                        output = False
                        break

                    else:
                        current_settings[_settings_key] = _settings_value
                        output = True

                else:
                    output = False

            if output is False:
                error_message = _settings_error[0] + _settings_value + _settings_error[1]
                break

    if error_message is not None:
        if new_settings is None:
            print 'Saved(or Default) settings are invalid due to an error: ',
        else:
            print 'Provided input will be discarded due to an error: ',

        print error_message
        if new_settings is None:
            sys.exit()

    return bool(output)


# Some Helpful Adapters #
def _hasattr(test_object, attr_name):
    """ Slightly modified hasattr to include dict """
    if type(test_object) in (dict, OrderedDict, DatabaseOrderedDict):
        return attr_name in test_object.keys()
    else:
        return getattr(test_object, attr_name)


def _getattr(test_object, attr_name):
    """ Slightly modified getattr to include dict """
    if type(test_object) in (dict, OrderedDict, DatabaseOrderedDict):
        return test_object[attr_name]
    else:
        return getattr(test_object, attr_name)


### MAIN ###
if __name__ == '__main__':
    # Load/Create Settings
    # print '*** Loading Backup Settings ***'
    settings_path = os.path.join(CWD, 'backup_settings.db')
    backup_settings = DatabaseOrderedDict(db_file=settings_path, defaults=DEFAULT_SETTINGS)

    # Fetch User Options
    allow_ts_mods = bool('folder_ts_format' in backup_settings)
    input_options = parse_input_options(allow_ts_mods)

    # Enable logging to a file (if we backing up)
    if input_options.back_up:
        # Create current backup time stamp
        if allow_ts_mods:
            backup_settings['_backup_ts'] = file_system.create_time_stamp(backup_settings['folder_ts_format'])
        else:
            backup_settings['_backup_ts'] = file_system.create_time_stamp(FOLDER_TS_FORMAT)

        # Create Logs
        logs_folder_path = os.path.join(CWD, 'logs')
        file_system.make_dir(logs_folder_path)
        log_file_path = os.path.join(logs_folder_path, 'backup' + backup_settings['_backup_ts'])
        sys.stdout = Logger(log_file_path)

    # Check operating system
    # TODO: Test on Windows and/or MAC, make sure its working properly!
    # if os.name != 'posix':
    #     os_type = platform.system()
    #     print 'Operating System "' + str(os_type) + '" is not supported!'
    #     sys.exit()

    if validate_settings(backup_settings, input_options):
        print '*** Saving New Backup Settings ***'
        backup_settings.save()

    if input_options.print_settings:
        print '*** Printing Backup Settings ***'
        for settings_key in backup_settings:
            settings_value = backup_settings[settings_key]
            print '{0:<3} {1:<25} {2:<25}'.format('', settings_key, str(settings_value))

    if validate_settings(backup_settings):
        if input_options.enable_backup:
            print '*** Enable Backup ***'
            # Enable crone job
            enable_backup(backup_settings, BACKUP_COMMAND)

        if input_options.disable_backup:
            print '*** Disable Backup ***'
            # Disable crone job
            disable_backup(BACKUP_COMMAND)

        if input_options.back_up:
            print '*** Executing Backup ***'
            execute_backup(backup_settings)
