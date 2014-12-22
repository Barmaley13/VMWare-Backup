"""
Cron related functions
"""

__author__ = 'Kirill V. Belyayev'

__copyright__ = "Copyright 2014, CIMA Systems"
__license__ = "GPL"


### INCLUDES ###
import os

from crontab import CronTab


### CONSTANTS ###
# TODO: Rewrite crontab so it works on Windows as well!
if os.name == 'posix':
    CRON = CronTab()
else:
    CRON = None


### FUNCTIONS ###
def enable_backup(settings, backup_command):
    """ Enable cron job """
    if CRON is not None:
        disable_backup(CRON)
        job = CRON.new(command=backup_command)
        job.setall(settings['crone_schedule'])
        job.enable()
        CRON.write()


def disable_backup(backup_command):
    """ Disable cron job """
    if CRON is not None:
        for job in CRON.find_command(backup_command):
            CRON.remove(job)
        CRON.write()
