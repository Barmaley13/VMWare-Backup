# !/usr/bin/env python
"""
Distribution package utilities
Used quite a few recipes from here:
https://wiki.python.org/moin/Distutils/Cookbook
Some hints on how to extend commands
http://stackoverflow.com/questions/1321270/how-to-extend-distutils-with-a-simple-post-install-script/1321345#1321345
"""

__author__ = 'Kirill V. Belyayev'

__copyright__ = "Copyright 2014, CIMA Systems"
__license__ = "GPL"


### INCLUDES ###
import os
import sys
import imp
import shutil
import glob

from distutils.core import setup
from distutils.sysconfig import get_python_lib
from distutils.command.install_data import install_data
from distutils.command.install import install

from vmware_backup import __version__
import vmware_backup.file_system as fs


### CONSTANTS ###
CWD = sys.path[0]
# print "CWD = ", str(CWD)

# Change Installation Directory (if needed)
HOME = os.path.expanduser('~')

# SITE_PACKAGES = get_python_lib()


### FUNCTIONS ###
## Setup Functions ##
def is_package(path):
    return os.path.isfile(os.path.join(path, '__init__.py'))


def find_packages(path, base=""):
    """ Find all packages in path """
    py_packages = {}
    for item in os.listdir(path):
        py_dir = os.path.join(path, item)
        if os.path.isdir(py_dir) and is_package(py_dir):
            # print "item = ", item
            if base:
                module_name = "%(base)s.%(item)s" % vars()
            else:
                module_name = item
            py_packages[module_name] = py_dir
            py_packages.update(find_packages(py_dir, module_name))
    return py_packages


def non_python_files(path):
    """ Return all non-python-file file names in path """
    result = []
    all_results = []
    module_suffixes = [info[0] for info in imp.get_suffixes()]
    ignore_dirs = ['cvs']
    for item in os.listdir(path):
        name = os.path.join(path, item)
        if os.path.isfile(name) and os.path.splitext(item)[1] not in module_suffixes:
            result.append(name)
        elif os.path.isdir(name) and item.lower() not in ignore_dirs:
            all_results.extend(non_python_files(name))
    if result:
        all_results.append((path, result))
    return all_results


def package_data_files(path):
    """ Returns all file names in path in package data format """
    result = []
    for item in non_python_files(path):
        result += item[1]

    return result


## Dist Functions ##
def _generate_docs(doc_packages):
    """
    Generates documentation. Performed before generating distribution on host (Windows) system.
    """
    print "*** Generating Documentation ***"
    # Rebuilding package module interconnections and package classes images.
    for package_name, package_path in doc_packages.items():
        package_path = package_path.split('vmware_backup')
        package_path[0] = ''
        package_path = 'vmware_backup'.join(package_path)
        pyreverse_command = 'pyreverse -o png -p ' + package_name + ' ' + package_path
        print pyreverse_command
        os.system(pyreverse_command)

    # Moving images to appropriate folder
    images = glob.glob('*.png')
    fs.make_dir('_docs/images/')
    for image in images:
        shutil.move(image, '_docs/images/' + image.split('/')[-1])
    # Updating automatically generated rst files
    print 'sphinx-apidoc -f -o _docs vmware_backup'
    os.system('sphinx-apidoc -f -o _docs vmware_backup')
    # Rebuilding documentation in html format
    fs.remove_dir('docs')
    print 'sphinx-build -b html _docs docs'
    os.system('sphinx-build -b html _docs docs')


## Install Functions ##
def _pre_install():
    """ Pre install procedures """
    pass


def _post_install():
    """ Post install procedures """
    print "*** Creating folders and generating files for user data ***"
    shutil.copy('run_backup.py', HOME)
    fs.copy_dir('docs', HOME + '/docs')


### CLASSES ###
class MyInstallData(install_data):
    def run(self):
        # need to change self.install_dir to the library dir
        install_cmd = self.get_finalized_command('install')
        self.install_dir = getattr(install_cmd, 'install_lib')
        return install_data.run(self)


class MyInstall(install):
    def run(self):
        """ Modified install procedure """
        _pre_install()
        print "*** Installing Package ***"
        install.run(self)
        _post_install()


### SETUP PROCEDURES ###
# Set current working directory
os.chdir(CWD)

packages = find_packages(".", "")
# print "packages = ", str(packages), "\n"

if len(sys.argv):
    if 'sdist' in sys.argv:
        _generate_docs(packages)
        print "*** Generation Distribution ***"
    elif 'install' in sys.argv:
        # Enable force to overwrite existing files and create folders
        sys.argv.append('--force')

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
    download_url='https://github.com/Barmaley13/VMWare-Backup/tarball/' + __version__,
    packages=packages.keys(),
    package_dir=packages,
    package_data=package_data,
    data_files=data_files,
    cmdclass={'install_data': MyInstallData, 'install': MyInstall},
    requires=[
        # Anything else?
        'crontab'
    ]
)
