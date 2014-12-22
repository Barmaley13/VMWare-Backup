"""
Database classes that facilitate in storing/restoring python content in a form of
dictionaries or lists on/from the hard drive.
Make sure to provide plain data, no objects, classes or anything that might be hard to convert to a string
"""

__author__ = 'Kirill V. Belyayev'

__copyright__ = "Copyright 2014, CIMA Systems"
__license__ = "GPL"


### INCLUDES ###
import copy

from . import file_system as fs
from .ordered_dict import OrderedDict


### CLASSES ###
class _DatabaseEntry(object):
    """ Database Entry Base Class """
    def __init__(self, main, db_file=None, defaults=None):
        self._main = main
        self._db_file = db_file
        self._defaults = defaults
        self.load()

    ## Load Methods ##
    def load(self):
        """ External Load """
        db_main = self._load()
        if db_main is not None:
            self._main = db_main

    def _load(self):
        """ Internal Load - loads main from a file if it exists """
        db_main = None
        if self._db_file:
            database_data = fs.unpickle_file(self._db_file)
            if database_data:
                db_main = database_data

        if self._defaults and db_main is None:
            db_main = self._load_default()

        return db_main

    def _load_default(self):
        """ Loads main with defaults """
        if type(self._defaults) is type(self._main):
            defaults = copy.deepcopy(self._defaults)
        else:
            defaults = None

        return defaults

    ## Save Methods ##
    def save(self, db_content=None):
        """ Saves main to a file """
        if db_content is None:
            db_content = self._main

        if self._db_file:
            if '/' in self._db_file:
                db_list = self._db_file.split('/')
                db_name = db_list.pop(-1)
                db_path = '/'.join(db_list)
                fs.make_dir(db_path)

            fs.pickle_file(self._db_file, db_content)

    ## Delete Methods ##
    def delete(self):
        """ Deletes database file """
        fs.remove_file(self._db_file)

    ## Generic Macros ##
    def __iter__(self):
        return iter(self._main)

    def __getitem__(self, key):
        """ Allows using self[key] method """
        return self._main[key]

    def __setitem__(self, key, value):
        """ Allows using self[key] = value method """
        self._main[key] = value

    def __delitem__(self, key):
        """ Allows using del self[key] method """
        del self._main[key]

    def __len__(self):
        """ Allows using len(self) method """
        return len(self._main)

    def __repr__(self):
        """ Allows using self method. Returns list of dictionaries """
        return repr(self._main)

    def __str__(self):
        """ Allows using print self method """
        return str(self.__repr__())

    def pop(self, index):
        """ Allows using pop method """
        return self._main.pop(index)


class _DatabaseListBase(_DatabaseEntry):
    """ Some List Specific Methods """
    def append(self, value):
        """ Allows using append method """
        self._main.append(value)

    def extend(self, value):
        """ Allows using extend method """
        self._main.extend(value)

    def insert(self, index, value):
        """ Allows using insert method """
        self._main.insert(index, value)


class _DatabaseDictBase(_DatabaseEntry):
    """ Some Dictionary Specific Methods """
    def update(self, value):
        """ Allows using update method """
        self._main.update(value)

    def items(self):
        """ Allows using items method """
        return self._main.items()
    
    def values(self):
        """ Allows using values method """
        return self._main.values()
    
    def keys(self):
        """ Allows using keys method """
        return self._main.keys()


class DatabaseList(_DatabaseListBase):
    """ DatabaseList class """

    def __init__(self, **kwargs):
        """ Load database entry """
        super(DatabaseList, self).__init__([], **kwargs)


class DatabaseDict(_DatabaseDictBase):
    """ DatabaseDict class """
    def __init__(self, **kwargs):
        """ Load database entry """
        super(DatabaseDict, self).__init__({}, **kwargs)


class DatabaseOrderedDict(_DatabaseDictBase):
    """ DatabaseOrderedDict class """
    def __init__(self, **kwargs):
        """ Load database entry """
        super(DatabaseOrderedDict, self).__init__(OrderedDict(), **kwargs)
