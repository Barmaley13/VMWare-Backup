VMWare-Backup
*************

Python based VMWare backup script.

Introduction and some general assumptions
=========================================

What this Script Does
_____________________

Basically, using this script it is possible to set certain time to perform backups. All, it needs to know location of
your ``VMWare`` machines, location of backup media and location of ``vmrun`` interface.

Once, backup script is executed it goes through the folder with your virtual machines. Matches those to currently
running machines using ``vmrun``. Goes through the list of the machines, suspending, backing up and resuming those
individually. If machine is powered off, script backs it up without performing suspend and resume steps.

Script keeps on logging what have been done, creating log file with a time stamp at the end.

Also each backup is stored under time stamped folder. During backup, script goes through all the backup volumes and
determines which volume to use to backup particular machine. Therefore, it is possible you might end up with
same date backup spread out on different backup volumes to conserve space.

One more feature that is worth mentioning. During backup setup stage, script saves your backup settings
to a file so those settings are saved to the hard drive. (or a solid state drive, I don't know what you might have...)

Operating System Considerations
_______________________________

Was written and tested on Linux-based ``Red Hat 6`` Operating System.
It should work on ``Windows`` and ``Mac OS``. However, I am pretty sure it will need some slight code additions
for the ``Windows``. I am not familiar enough with ``Mac OS`` to tell if it will work right of the bet or not.

VMWare Product Support
______________________

Currently, we are using ``VMWare Workstation`` to run our virtual machines. If you are using any other ``VMWare``
product this backup script might require ``vmrun`` modification. Which is command prompt utility that we've used to
talk to ``VMWare Workstation``. My knoweledge of VMWare products is quite limited so suggestions, additions,
modifications are welcome!

Backup Media
____________

Furthermore, we've been using this script to back up virtual machines to tape. Our tape drive consist of 8 tapes, which
shows up in Linux as a drive with 8 volumes. It is possible to modify script to work with single tape or any other
backup configurations.


Installation
============

Make sure latest python-crontab package is installed::

    pip install python-crontab

Install vmware-backup package. Either download latest code from Github and execute::

    python setup.py install

Alternatively, install package using pip::

    pip install vmware-backup

During installation, vmware backup module will be added to your python site-packages. Also, installation script will
copy ``run_backup.py`` script along with docs to you current user directory. Under linux that would be ``~``, under
Windows should be ``C:/Users/Your_Name/``, under Mac OS who knows...


.. note::

    Let us know if you stumble upon missing python modules that we forgot to include.

How to use this script to backup your VMWare Virtual Machines
=============================================================

Once again, current limitations are:

    * This script has been tested on Linux-based ``Red Hat 6`` only!
    * Has been tested only with ``VMWare Workstation``!
    * Script assumes that you have a multi-volume backup drive. In my case, I point script to the ``/media/lto6``,
      which is a drive. And I have multiple volumes (displayed as folders) under that location.


First and foremost, find where installation procedure placed ``run_backup.py`` file. Once, the file is located, you
can execute following to fetch all the possible options::

    python run_backup -h

The options should be self explanatory. Set backup settings first, such crone schedule, vmrun path, virtual machines
path and tape path. Next - enable backup.

Please refer to https://pypi.python.org/pypi/python-crontab that will explain
how to format crontab string to set proper backup intervals.

Also, it is possible to change time stamp format. Please refer to
https://docs.python.org/2/library/time.html#time.strftime. That will explain how to format such a string. I would
recommend not to mess with it to much since there is no validation performed on those strings. But this might be handy
for friends from Europe and other parts of the world if you want to change month and date inside of the time stamp.

Notes for Code Developers
=========================

The vmware_backup module comes with some documentation. It is mostly self generated from the code itself.
There are also images giving basic overview as far as package modules and classes. Please let me know, if you end up
digging through code and willing to extend documentation.

Additional Info and Questions
=============================

Shoot me email at ``kirill at kbelyayev.com`` if you have any questions, suggestions, improvements, additions and etc.
I would love to help you get this script going on your system if you hire me as a contractor. I might help you free of
charge if you contribute to this distribution or ask politely. Beer donations are welcome too!

**Good luck! Happy coding! And happy vmware backups!**
