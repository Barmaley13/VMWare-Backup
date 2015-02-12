"""
Default Backup Settings
"""

__author__ = 'Kirill V. Belyayev'

__copyright__ = "Copyright 2014, CIMA Systems"
__license__ = "GPL"


### INCLUDES ###
from ordered_dict import OrderedDict


### CONSTANTS ###
## Default Backup Settings ##
# TODO: Add different settings for different Operating Systems
DEFAULT_SETTINGS = OrderedDict()
DEFAULT_SETTINGS['crone_schedule'] = '0 22 * * 1-5'
DEFAULT_SETTINGS['vmrun_path'] = 'vmrun'
DEFAULT_SETTINGS['vms_path'] = '~/vmware'
DEFAULT_SETTINGS['tape_path'] = '/media/lto6'
DEFAULT_SETTINGS['_backup_ts'] = ''

# Time Stamp Option 1: Allow user to change time stamps (Comment those out for Option 2)
DEFAULT_SETTINGS['folder_ts_format'] = '-%Y%m%d'
DEFAULT_SETTINGS['log_ts_format'] = '%Y-%m-%d %H:%M:%S'

# Time Stamp Option 2: Do not allow user to change time stamps
FOLDER_TS_FORMAT = '-%Y%m%d'
LOG_TS_FORMAT = '%Y-%m-%d %H:%M:%S'

## Multiple Attempt Settings ##
ATTEMPT_NUMBER = 10
ATTEMPT_TIMEOUT = 10        # seconds
