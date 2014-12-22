"""
VMWare Backup Internals

Some References that might of been used (or not)
VMWare Command Line
https://www.vmware.com/support/ws5/doc/ws_learning_cli_vmrun.html

Linux Scheduler:
http://stackoverflow.com/questions/1603109/how-to-make-a-python-script-run-like-a-service-or-daemon-in-linux
http://unix.stackexchange.com/questions/69098/how-can-i-schedule-a-python-program-to-run-from-another-python-program

Windows Scheduler (not supported):
http://stackoverflow.com/questions/2725754/schedule-python-script-windows-7

Linux Daemon (not needed?):
http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/
"""

__author__ = 'Kirill V. Belyayev'
__version__ = '1.01'

__copyright__ = "Copyright 2014, CIMA Systems"
__license__ = "GPL"


### EXTERNAL INCLUDES ###
from .default_settings import DEFAULT_SETTINGS, FOLDER_TS_FORMAT
from .file_system import create_time_stamp, make_dir
from .ordered_dict import OrderedDict
from .database import DatabaseOrderedDict
from .logger import Logger
from .virtual_machine import VirtualMachine, execute_backup
from .cron import enable_backup, disable_backup
