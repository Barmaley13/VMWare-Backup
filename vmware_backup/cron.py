"""
Cron related functions
"""

__author__ = 'Kirill V. Belyayev'

__copyright__ = "Copyright 2014, CIMA Systems"
__license__ = "GPL"


### INCLUDES ###
from crontab import CronTab


### CONSTANTS ###
CRON = CronTab()


### FUNCTIONS ###
# TODO: Rewrite crontab so it works on Windows as well!
def enable_backup(settings, backup_command):
    """ Enable cron job """
    disable_backup(CRON)
    job = CRON.new(command=backup_command)
    job.setall(settings['crone_schedule'])
    job.enable()
    CRON.write()


def disable_backup(backup_command):
    """ Disable cron job """
    for job in CRON.find_command(backup_command):
        CRON.remove(job)
    CRON.write()
