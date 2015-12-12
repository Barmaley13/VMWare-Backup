"""
Virtual Machine Class
"""


### INCLUDES ###
import os
import sys
import commands
import glob

from py_knife import file_system
from py_knife.decorators import multiple_attempts

from default_settings import LOG_TS_FORMAT, MUTLIPLE_TAPE_SYSTEM


### CONSTANTS ###
## Meta Data ##
__author__ = 'Kirill V. Belyayev'
__license__ = 'GPL'


### FUNCTIONS ###
def execute_backup(settings):
    """ Backup Machines """
    vm_list = []
    vm_path_list = glob.glob(os.path.join(settings['vms_path'], '*'))
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
        self.name = os.path.basename(vm_path)
        self.vmware = None
        self.base_backup_path = None
        self.vm_backup_path = None

    ## Some generic internal methods ##
    def _print(self, message):
        # Time Stamp Options 1 and 2
        if 'log_ts_format' in self.settings:
            print file_system.create_time_stamp(self.settings['log_ts_format']), str(message)
        else:
            print file_system.create_time_stamp(LOG_TS_FORMAT), str(message)

    def _exit(self, message):
        self._print(message)
        self.resume()
        sys.exit()

    ## VMWare Communication Methods ##
    # Internal #
    def _fetch_vmware(self):
        """ Fetches vmware path if machine is currently running """
        vm_list = commands.getoutput(self.settings['vmrun_path'] + ' list').split('\n')
        if 'Total running VMs:' in vm_list[0]:
            self._print(vm_list.pop(0))
        else:
            self._exit('VMWare vmrun location is incorrect, please provide it manually via command prompt. '
                       'Use -h option for help!')

        vm_dict = {}
        for vm_path in vm_list:
            vm_name = os.path.basename(os.path.dirname(vm_path))
            vm_dict[vm_name] = vm_path

        vmware_path = None
        if self.name in vm_dict.keys():
            vmware_path = vm_dict[self.name]

        return vmware_path

    @multiple_attempts
    def _suspend(self, **kwargs):
        """ Suspending Virtual Machine (inner function) """
        kwargs['success'] = bool(self._fetch_vmware() is None)

        if not kwargs['success']:
            total_attempts = str(kwargs['total_attempts'])
            self._print('Suspending virtual machine... (attempt #' + total_attempts + ')')
            os.system(self.settings['vmrun_path'] + ' suspend "' + self.vmware + '" soft')
            self._print('Suspend of virtual machine is completed! (attempt #' + total_attempts + ')')

            kwargs['success'] = bool(self._fetch_vmware() is None)

        return kwargs

    @multiple_attempts
    def _resume(self, **kwargs):
        """ Resuming Virtual Machine (inner function) """
        kwargs['success'] = bool(self._fetch_vmware() is not None)

        if not kwargs['success']:
            total_attempts = str(kwargs['total_attempts'])
            self._print('Resuming virtual machine... (attempt #' + total_attempts + ')')
            os.system(self.settings['vmrun_path'] + ' start "' + self.vmware + '" nogui')
            self._print('Resume of virtual machine is completed! (attempt #' + total_attempts + ')')

            kwargs['success'] = bool(self._fetch_vmware() is not None)

        return kwargs

    # External #
    # Note: User has to fetch state of the machine before using suspend or resume
    def state(self):
        """ Tells if Virtual Machine is currently running """
        self.vmware = self._fetch_vmware()

        return bool(self.vmware)

    def suspend(self):
        """ Suspending Virtual Machine """
        if self.vmware:
            self._suspend()

    def resume(self):
        """ Resuming Virtual Machine """
        if self.vmware:
            self._resume()

    ## Tape Methods ##
    def _space_available(self, tape):
        """ Reads available space on particular tape """
        space_available = file_system.get_free_space(tape)
        tape_name = str(os.path.basename(tape))
        self._print("Space available on tape '" + tape_name + "': " + file_system.print_memory_size(space_available))

        return space_available

    def _fetch_base_path(self, space_needed):
        """ Figuring out what tape to use and generating path for the future backup location """
        tape_to_use = None
        if MUTLIPLE_TAPE_SYSTEM:
            tape_list = glob.glob(os.path.join(self.settings['tape_path'], '*'))
        else:
            tape_list = [self.settings['tape_path']]

        for tape in tape_list:
            # Figure out how much space we have on this tape
            space_available = self._space_available(tape)

            # Is it enough space?
            if space_available >= space_needed:
                self._print('Space available: ' + file_system.print_memory_size(space_available))
                tape_to_use = tape
                break
        else:
            self._exit('Tapes are full or inaccessible! Please unmount tape drive, reload tapes,'
                       ' format all of them and remount tape drive!')

        vm_base_name = os.path.basename(self.settings['vms_path'])
        vm_backup_name = vm_base_name + self.settings['_backup_ts']

        return os.path.join(tape_to_use, vm_backup_name)

    @multiple_attempts
    def _creating_backup_folder(self, **kwargs):
        """ Creating backup folder on tape """
        kwargs['success'] = kwargs['output'] = os.path.isdir(self.vm_backup_path)

        if not kwargs['success']:
            total_attempts = str(kwargs['total_attempts'])
            try:
                self._print('Creating backup folder... (attempt #' + total_attempts + ')')
                file_system.make_dir(self.vm_backup_path)

            except OSError as e:
                self._print('Could not create folder "' + self.vm_backup_path +
                            '" due to an OS error ({0}): {1}'.format(e.errno, e.strerror))
            except IOError as e:
                self._print('Could not create folder "' + self.vm_backup_path +
                            '" due to an IO error ({0}): {1}'.format(e.errno, e.strerror))
            except:
                self._print('Could not create folder "' + self.vm_backup_path + '" due to an error: ' +
                            str(sys.exc_info()[0]))
            else:
                self._print('Backup folder is successfully created!')

            kwargs['success'] = kwargs['output'] = os.path.isdir(self.vm_backup_path)

        return kwargs

    @multiple_attempts
    def _backup(self, **kwargs):
        """ Backup (internal function)"""
        kwargs['success'] = False
        total_attempts = str(kwargs['total_attempts'])

        try:
            self._print('Starting Backup... (attempt #' + total_attempts + ')')
            file_system.copy_dir(self.path, self.vm_backup_path)

        except OSError as e:
            self._print('Could not backup "' + self.name +
                        '" virtual machine due to an OS error ({0}): {1}'.format(e.errno, e.strerror))
        except IOError as e:
            self._print('Could not backup "' + self.name +
                        '" virtual machine due to an IO error ({0}): {1}'.format(e.errno, e.strerror))
        except:
            self._print('Could not backup "' + self.name + '" virtual machine due to an error: ' +
                        str(sys.exc_info()[0]))
        else:
            self._print('Backup Completed!')
            kwargs['success'] = True

        return kwargs

    def backup_needed(self):
        """ Determine if backup needed or not """
        vmx_match = False
        vmx_file = os.path.join(self.path, self.name + '.vmx')
        for dir_path, dir_names, file_names in os.walk(self.settings['tape_path']):
            for dir_name in dir_names:
                if self.name in dir_name:
                    # Compare *.vmx files (size and access date)
                    vmx_files = glob.glob(os.path.join(dir_path, dir_name, self.name + '.vmx'))
                    for _vmx_file in vmx_files:
                        # Compare modified time stamps
                        vmx_match = bool(os.path.getmtime(_vmx_file) == os.path.getmtime(vmx_file))
                        # Compare file sizes
                        vmx_match &= bool(file_system.get_size(_vmx_file) == file_system.get_size(vmx_files))

                        if vmx_match:
                            self._print("Virtual Machine '" + self.name + "' have been backed up already!")
                            self._print('Backup Path: ' + str(_vmx_file))
                            break

                    else:
                        continue
                    break
            else:
                continue
            break
        else:
            self._print("Virtual Machine '" + self.name + "' have not been backed up yet!")

        return not vmx_match

    ## VMWare Backup Method ##
    def backup(self):
        """ Execute backup of this virtual machine """

        # Print some basic info about this Virtual Machine
        self._print('VM Name: ' + self.name)
        self._print('VM Path: ' + self.path)

        # Figure out if Virtual Machine is currently running
        vm_state = self.state()
        self._print('VM Running: ' + str(vm_state))

        if self.backup_needed():
            # Suspend Virtual Machine (if needed)
            self.suspend()

            # Figure out how much space this Virtual Machine is taking up
            space_needed = file_system.get_size(self.path)
            self._print('Space needed: ' + file_system.print_memory_size(space_needed))

            # Figure out what tape we will use to back up this Virtual Machine
            self.base_backup_path = self._fetch_base_path(space_needed)
            self.vm_backup_path = os.path.join(self.base_backup_path, self.name)
            self._print('BackUp Location: ' + str(self.vm_backup_path))

            # Creating backup folder
            backup_folder_created = self._creating_backup_folder()

            if backup_folder_created:
                # Backup this Virtual Machine
                # TODO: Add some compression options and functions
                self._backup()

            # Resume Virtual Machine (if needed)
            self.resume()
