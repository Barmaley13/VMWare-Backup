# !/usr/bin/env python
"""
VMWare Backup Setup Scripts
"""


### INCLUDES ###
import sys
import shutil

from distutils.core import setup
from distutils.command.install import install

from py_knife.py_setup import find_packages, non_python_files, package_data_files, generate_docs

from vmware_backup import __version__


### CONSTANTS ###
## Meta Data ##
__author__ = 'Kirill V. Belyayev'
__license__ = 'GPL'


### FUNCTIONS ###
## Install Functions ##
def _pre_install():
    """ Pre install procedures """
    pass


def _post_install():
    """ Post install procedures """
    pass
    # print "*** Creating folders and generating files for user data ***"
    # user_script_path = os.path.join(os.path.expanduser('~'), 'VMWare-Backup')
    # file_system.make_dir(user_script_path)
    # shutil.copy('run_backup.py', user_script_path)


### CLASSES ###
class MyInstall(install):
    def run(self):
        """ Modified install procedure """
        _pre_install()
        print "*** Installing Package ***"
        install.run(self)
        _post_install()


### SETUP PROCEDURES ###
packages = find_packages(".", "")
# print "packages = ", str(packages), "\n"

if len(sys.argv):
    if 'sdist' in sys.argv:
        print "*** Generating Documentation ***"
        generate_docs(packages)

        print "*** Generation Distribution ***"
    elif 'install' in sys.argv:
        # Enable force to overwrite existing files and create folders
        if '--force' not in sys.argv:
            sys.argv.append('--force')
        if '--single-version-externally-managed' in sys.argv:
            sys.argv.remove('--single-version-externally-managed')

# Probably none, kept for future reference
data_files = (non_python_files('vmware_backup'))
# print "data_files = ", str(data_files), "\n"

package_data_content = package_data_files('docs')
package_data = {'': package_data_content}
# print "package_data = ", str(package_data), "\n"

setup(
    name='vmware_backup',
    version=__version__,
    description='VMWare Backup',
    long_description='Python based vmware backup script',
    author='Kirill V. Belyayev',
    author_email='kbelyayev@gmail.com',
    url='https://github.com/Barmaley13/VMWare-Backup',
    # download_url='https://github.com/Barmaley13/VMWare-Backup/tarball/' + __version__,
    packages=packages.keys(),
    package_dir=packages,
    package_data=package_data,
    data_files=data_files,
    scripts=['run_backup.py'],
    cmdclass={'install': MyInstall},
    requires=[
        # Anything else?
        'crontab',
        'py_knife'
    ]
)
