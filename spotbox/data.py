"""SPOTBOX data backend"""

import itertools
import os
import operator
import random


class Spot(object):

    def __init__(self, path, config):
        components = split_file_name(path)
        prefix = components[0]
        try:
            config_components = split_file_name(config[prefix], keep_slash=True)
        except KeyError:
            raise ValueError(path)
        self.info = dict(zip(config_components[1:], components[1:]))
        self.type = prefix
        self.path = path


class Datasheet(object):
    """list of lists (dicts?), basically. Searchable, sortable.

    Each has a list of spots (original datasheet) which is full
    and a public datasheet : whatever should be displayed (searched, sorted).
    """

    def __init__(self):
        self._datasheet = []
        self._publicdatasheet = []

    def _blippy(self):
        # Figure out what this means
        self._sortedkey = None
        self._sortedbackwards = False

    def add_spot(self, spot):
        self._datasheet.append(spot)

    def search(self, searchterm):
        self.freshen()
        self._publicdatasheet = [spot for spot in self._publicdatasheet if
                                 any(searchterm.lower() in header.lower()
                                     for header in spot.info.values())]
    def __getitem__(self, index):
        return self._datasheet[index]

    def __iter__(self):
        # allows to iterate through all spots in the datasheet
        return iter(self._publicdatasheet)

    def fillable(self):
        """return the public contents in a form useable for the menu GUI"""
        return self._publicdatasheet

    def sort_by_key(self, key):
        """sort the public datasheet by the selected column header"""
        sortbackwards = (True if self._sortedkey == key and not
                         self._sortedbackwards else False)
        self._publicdatasheet = sorted(self._publicdatasheet,
                key=lambda x: x.info[key], reverse=sortbackwards)
        self._sortedkey = key
        self._sortedbackwards = sortbackwards

    def freshen(self):
        # when datasheet is brought to top, it resets its filter and randomizes
        self._publicdatasheet = self._datasheet
        self._blippy()
        random.shuffle(self._publicdatasheet)


class DatasheetNotebook(object):
    """An object that holds all information about the spotbox files"""
    """From media folder , pull out all files and create dict by header."""

    def __init__(self, media_directory, file_config):
        #self._currentdatasheet = None
        #self._lastdatasheet = None
        print file_config
        self._datasheets = {spottype: Datasheet() for spottype in file_config}
        for path in all_spotbox_files(media_directory):
            try:
                spot = Spot(path, file_config)
            except ValueError:
                pass
            self._datasheets[spot.type].add_spot(spot)
        for datasheet in self._datasheets.values():
            datasheet.freshen()

    def __iter__(self):
        """allows iteration through the datasheets in the notebook"""
        return iter(self._datasheets.values())

    def get_fresh_sheet_by_key(self, key):
        """simply give the datasheet for the key because it's freshened
        when the currentdatasheet is set, you don't have to freshen
        it here; saves on computation; the sheet can be served quicker
        """
        return self._datasheets[key]

    #@property
    #def currentdatasheet(self):
        #return self._currentdatasheet
    #@currentdatasheet.setter
    #def currentdatasheet(self, datasheet):
        ## set the currentsheet, and then freshen the old sheet.
        ## so it's re-randomized, etc, before you get to it again
        #oldsheet = self._currentdatasheet
        #self._currentdatasheet = datasheet
        #if oldsheet is not None:
            #oldsheet.freshen()

    def subject_from_filepath(self, filepath):
        raise NotImplementedError
        try:
            justthefilename = filepath.split('/')[-1]
            key = justthefilename.split('_')[0]
            subject = justthefilename.split('_')[self._config[key]['index subject'] - 1]
            # the minus one is getting around a bug. TODO fix.
        except:
            # return first part of the filename:
            justthefilename = filepath.split('/')[-1]
            filenamewithoutsuffix = justthefilename.rsplit('.', 1)[0]
            subject = filenamewithoutsuffix.split('_')[0]
        return subject

    def time_from_filepath(self, filepath):
        # returns integer
        raise NotImplementedError
        try:
            justthefilename = os.path.basename(filepath)
            key = justthefilename.split('_')[0]
            time = justthefilename.split('_')[self._config[key]['index timer'] - 1]
            # the minus one is getting around a bug. TODO fix.
        except:
            # try returning the last part of the filename:
            justthefilename = filepath.split('/')[-1]
            filenamewithoutsuffix = justthefilename.rsplit('.', 1)[0]
            time = filenamewithoutsuffix.split('_')[-1]
        try:
            minutes, seconds = time.split('.')
            timetoload = 60*int(minutes) + int(seconds)
            return timetoload
        except:
            return 9999


def merge_file_and_format(filename, format):
    return dict(itertools.izip_longest(format, split_file_name(filename),
                                       fillvalue=''))


def split_file_name(filename, keep_slash=False):
    """Extracts metadata (underscore-separated)"""
    if not keep_slash:
        filename = os.path.basename(filename)
    basename = os.path.splitext(filename)[0]
    return tuple(basename.split('_'))

    # Hard-coded way to disregard 'Icon' files (stupid Mac thing):
    #if len(fname) <= 5 or 'Icon' in fname:


def all_spotbox_files(media_dir):
    paths = [os.path.join(media_dir, fname) for fname in os.listdir(media_dir)
             if not fname.startswith('.')]
    return (x for x in paths if os.path.isfile(x))
