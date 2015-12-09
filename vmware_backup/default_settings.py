"""
Default Backup Settings
"""


### INCLUDES ###
import os
import string

from py_knife.ordered_dict import OrderedDict


### CONSTANTS ###
## Meta Data ##
__author__ = 'Kirill V. Belyayev'
__license__ = 'GPL'

## Default Backup Settings ##
# TODO: Add 'MUTLIPLE_TAPE_SYSTEM' to parser
DEFAULT_SETTINGS = OrderedDict()
DEFAULT_SETTINGS['crone_schedule'] = '0 22 * * 1-5'
DEFAULT_SETTINGS['vmrun_path'] = 'vmrun'
DEFAULT_SETTINGS['vms_path'] = os.path.join(os.path.expanduser('~'), 'vmware')

if os.name == 'nt':
    # Guessing backup media
    available_drives = ['%s:' % d for d in string.ascii_uppercase if os.path.exists('%s:' % d)]
    DEFAULT_SETTINGS['tape_path'] = os.path.abspath(available_drives[-1])
    MUTLIPLE_TAPE_SYSTEM = False
else:
    # FIXME: Would this work on MAC?
    DEFAULT_SETTINGS['tape_path'] = os.path.join(os.path.abspath(os.sep), 'media', 'lto6')
    MUTLIPLE_TAPE_SYSTEM = True

DEFAULT_SETTINGS['_backup_ts'] = ''

# Time Stamp Option 1: Allow user to change time stamps (Comment those out for Option 2)
DEFAULT_SETTINGS['folder_ts_format'] = '-%Y%m%d'
DEFAULT_SETTINGS['log_ts_format'] = '%Y-%m-%d %H:%M:%S'

# Time Stamp Option 2: Do not allow user to change time stamps
FOLDER_TS_FORMAT = '-%Y%m%d'
LOG_TS_FORMAT = '%Y-%m-%d %H:%M:%S'
