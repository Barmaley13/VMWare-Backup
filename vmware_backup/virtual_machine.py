"""
Virtual Machine Class
"""

__author__ = 'Kirill V. Belyayev'

__copyright__ = "Copyright 2014, CIMA Systems"
__license__ = "GPL"


### INCLUDES ###
import os
import sys
import commands
import glob
import time

from . import file_system as fs
from .default_settings import LOG_TS_FORMAT


### CONSTANTS ###
WHILE_LOOP_ATTEMPTS = 10
WHILE_LOOP_WAIT_TIME = 10       # seconds


### FUNCTIONS ###
def execute_backup(settings):
    """ Backup Machines """
    vm_list = []
    vm_path_list = glob.glob(settings['vms_path'] + '/*')
    for vm_path in vm_path_list:
        vm_list.append(VirtualMachine(settings, vm_path))

    for virtual_machine in vm_list:
        virtual_machine.backup()


### CLASSES ###
class VirtualMachine(object):
    """ Virtual Machine class """
    def __init__(self, settings, vm_path):
        self.settings = settings
        self.path = vm_path
        self.name = vm_path.split('/')[-1]
        self.vmware = None
        self.base_backup_path = None
        self.vm_backup_path = None

    def _print(self, message):
        # Time Stamp Options 1 and 2
        if 'log_ts_format' in self.settings:
            print fs.create_time_stamp(self.settings['log_ts_format']), str(message)
        else:
            print fs.create_time_stamp(LOG_TS_FORMAT), str(message)

    def _exit(self, message):
        self._print(message)
        self._resume()
        sys.exit()

    def _fetch_vmware(self):
        vm_list = commands.getoutput(self.settings['vmrun_path'] + ' list').split('\n')
        if 'Total running VMs:' in vm_list[0]:
            self._print(vm_list.pop(0))
        else:
            self._exit('VMWare vmrun location is incorrect, please provide it manually via command prompt. '
                       'Use -h option for help!')

        vm_dict = {}
        for vm_path in vm_list:
            vm_name = vm_path.split('/')[-2]
            vm_dict[vm_name] = vm_path

        vmware_path = None
        if self.name in vm_dict.keys():
            vmware_path = vm_dict[self.name]

        return vmware_path

    def _suspend(self):
        if self.vmware:
            total_attempts = 0
            while self._fetch_vmware() is not None and total_attempts < WHILE_LOOP_ATTEMPTS:
                total_attempts += 1
                self._print('Suspending virtual machine... (attempt #' + str(total_attempts) + ')')
                os.system(self.settings['vmrun_path'] + ' suspend "' + self.vmware + '" soft')
                self._print('Suspend of virtual machine is completed! (attempt #' + str(total_attempts) + ')')
                time.sleep(WHILE_LOOP_WAIT_TIME)

    def _resume(self):
        if self.vmware:
            total_attempts = 0
            while self._fetch_vmware() is None and total_attempts < WHILE_LOOP_ATTEMPTS:
                total_attempts += 1
                self._print('Resuming virtual machine... (attempt #' + str(total_attempts) + ')')
                os.system(self.settings['vmrun_path'] + ' start "' + self.vmware + '" nogui')
                self._print('Resume of virtual machine is completed! (attempt #' + str(total_attempts) + ')')
                time.sleep(WHILE_LOOP_WAIT_TIME)

    def _fetch_base_path(self, space_needed):
        tape_to_use = None
        # TODO: Add support for single tape system
        tape_list = glob.glob(self.settings['tape_path'] + '/*')
        for tape in tape_list:
            # Figure out how much space we have on this tape
            total_attempts = 0
            space_available = 0
            while space_available == 0 and total_attempts < WHILE_LOOP_ATTEMPTS:
                total_attempts += 1
                space_available = fs.get_free_space(tape)
                tape_name = str(tape.split('/')[-1])
                self._print("Space available on tape '" + tape_name + "': " + fs.print_memory_size(space_available)
                            + ' (attempt #' + str(total_attempts) + ')')
                time.sleep(WHILE_LOOP_WAIT_TIME)

            # Is it enough space?
            if space_available >= space_needed:
                self._print('Space available: ' + fs.print_memory_size(space_available))
                tape_to_use = tape
                break
        else:
            self._exit('Tapes are full or inaccessible! Please unmount tape drive, reload tapes,'
                       ' format all of them and remount tape drive!')

        vm_base_name = self.settings['vms_path'].split('/')[-1]
        vm_backup_name = vm_base_name + self.settings['_backup_ts']

        return tape_to_use + '/' + vm_backup_name

    def backup(self):
        # Print some basic info about this Virtual Machine
        self._print('VM Name: ' + self.name)
        self._print('VM Path: ' + self.path)

        # Figure out if Virtual Machine is currently running
        self.vmware = self._fetch_vmware()
        self._print('VM Running: ' + str(bool(self.vmware)))

        # Suspend Virtual Machine (if needed)
        self._suspend()

        # Figure out how much space this Virtual Machine is taking up
        total_attempts = 0
        space_needed = 0
        while space_needed == 0 and total_attempts < WHILE_LOOP_ATTEMPTS:
            total_attempts += 1
            space_needed = fs.get_size(self.path)
            self._print('Space needed: ' + fs.print_memory_size(space_needed)
                        + ' (attempt #' + str(total_attempts) + ')')
            time.sleep(WHILE_LOOP_WAIT_TIME)

        # Figure out what tape we will use to back up this Virtual Machine
        self.base_backup_path = self._fetch_base_path(space_needed)
        self.vm_backup_path = self.base_backup_path + '/' + self.name
        self._print('BackUp Location: ' + str(self.vm_backup_path))

        # Backup this Virtual Machine
        self._print('Starting Backup...')
        try:
            total_attempts = 0
            while not os.path.isdir(self.vm_backup_path) and total_attempts < WHILE_LOOP_ATTEMPTS:
                total_attempts += 1
                self._print('Creating backup folder... (attempt #' + str(total_attempts) + ')')
                fs.make_dir(self.vm_backup_path)
                time.sleep(WHILE_LOOP_WAIT_TIME)

            fs.copy_dir(self.path, self.vm_backup_path)
        except OSError as e:
            self._print('Could not backup "' + self.name + '" virtual machine due to an OS error'
                                                           '({0}): {1}'.format(e.errno, e.strerror))
        except IOError as e:
            self._print('Could not backup "' + self.name + '" virtual machine due to an IO error'
                                                           '({0}): {1}'.format(e.errno, e.strerror))
        except:
            self._print('Could not backup "' + self.name + '" virtual machine due to an error: '
                        + str(sys.exc_info()[0]))
        else:
            self._print('Backup Completed!')

        # Resume Virtual Machine (if needed)
        self._resume()
