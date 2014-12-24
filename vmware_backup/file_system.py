"""
Collection of functions that help perform file system tasks such as moving, copying, removing files and folders.
"""

__author__ = 'Kirill V. Belyayev'

__copyright__ = "Copyright 2014, CIMA Systems"
__license__ = "GPL"


### INCLUDES ###
import os
import sys
import ctypes
import platform
import time
import glob
import shutil
import cPickle
import codecs
import logging


### CONSTANTS ###
LOGGER = logging.getLogger(__name__)
# LOGGER.setLevel(logging.DEBUG)


### FUNCTIONS ###
## Folder Functions ##
def make_dir(dir_path):
    """ Creating directory """
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)


def remove_dir(dir_path):
    if os.path.isdir(dir_path):
        shutil.rmtree(dir_path)


# TODO: Modify to work under Windows!
def copy_dir(source_path, destination_path):
    if os.path.isdir(source_path):
        make_dir(destination_path)
        sub_items = glob.glob(source_path + '/*')
        for sub_item in sub_items:
            copy_dir(sub_item, destination_path + '/' + sub_item.split('/')[-1])
    else:
        shutil.copy(source_path, destination_path)


## File Functions ##
def make_file(file_path):
    """ Creating empty file """
    if not os.path.isfile(file_path):
        open(file_path, 'a').close()


def remove_file(file_path):
    if os.path.isfile(file_path):
        os.remove(file_path)


def copy_file(source_file, destination_file, permissions=None):
    """ Permissions won't work on windows os. Only linux based systems """
    if os.path.isfile(destination_file):
        os.remove(destination_file)
    shutil.copy(source_file, destination_file)
    if os.name == 'posix':
        os.system('dos2unix ' + destination_file)
        if permissions is not None:
            os.system('chmod ' + str(permissions) + ' ' + destination_file)


## File/Folder Size Functions ##
def get_size(path):
    """
    Taken from here
    http://stackoverflow.com/questions/1392413/calculating-a-directory-size-using-python
    """
    total_size = 0
    seen = set()

    for directory_path, directory_names, file_names in os.walk(path):
        for f in file_names:
            fp = os.path.join(directory_path, f)

            try:
                stat = os.stat(fp)
            except OSError:
                continue

            if stat.st_ino in seen:
                continue

            seen.add(stat.st_ino)

            total_size += stat.st_size

    return total_size  # size in bytes


def get_free_space(path):
    """
    Return free space in bytes
    Taken from here, slightly modified:
    http://stackoverflow.com/questions/51658/cross-platform-space-remaining-on-volume-using-python
    """
    if platform.system() == 'Windows':
        free_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(path), None, None, ctypes.pointer(free_bytes))
        return free_bytes.value
    else:
        st = os.statvfs(path)
        return st.f_bavail * st.f_frsize


def print_memory_size(size):
    """
    Taken from here
    http://stackoverflow.com/questions/1392413/calculating-a-directory-size-using-python
    """
    _bytes = 'B'
    _kilo_bytes = 'KB'
    _mega_bytes = 'MB'
    _giga_bytes = 'GB'
    _tera_bytes = 'TB'
    memory_units = [_bytes, _kilo_bytes, _mega_bytes, _giga_bytes, _tera_bytes]
    memory_format = '%f %s'
    memory_radix = 1024.

    for u in memory_units[:-1]:
        if size < memory_radix:
            return memory_format % (size, u)
        size /= memory_radix

    return memory_format % (size,  memory_units[-1])


## Time Stamp Functions ##
def create_time_stamp(time_stamp_format):
    return time.strftime(time_stamp_format, time.localtime(time.time()))


## Pickle/Unpickle Functions ##
def _file_name(file_path):
    """ Extracts file name from file path """
    return file_path.split('/')[-1]


def pickle_file(file_path, data_to_pickle):
    """ Pickle file """
    success = False

    file_instance = codecs.open(file_path, 'w+')
    file_name = _file_name(file_path)
    if file_instance:
        try:
            pickled_data = cPickle.dumps(data_to_pickle)
        except TypeError as error:
            LOGGER.error("Could not pickle " + file_name + "!")
            LOGGER.error("Type Error Details: " + str(error))
        except:
            LOGGER.error("Could not pickle " + file_name + "!")
            LOGGER.error("Pickler error:" + str(sys.exc_info()[0]))
        else:
            file_instance.write(pickled_data)
            success = True
        file_instance.close()

    # LOGGER.debug(file_name + ": " + str(data_to_pickle))

    return success


def unpickle_file(file_path):
    """ Unpickle file """
    output = None

    if os.path.isfile(file_path):
        file_instance = codecs.open(file_path, 'r')
        file_name = _file_name(file_path)
        if file_instance:
            pickled_data = file_instance.read()
            try:
                un_pickled_data = cPickle.loads(pickled_data)
            except:
                LOGGER.error("Could not unpickle " + file_name + "!")
                LOGGER.error("Unpickler error:" + str(sys.exc_info()[0]))
            else:
                output = un_pickled_data
            file_instance.close()

    return output
