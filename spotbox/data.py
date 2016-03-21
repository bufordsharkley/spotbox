"""SPOTBOX data backend"""

import itertools
import os
import operator
import random


class Datasheet(object):
    """list of lists (dicts?), basically. Searchable, sortable.

    Each has a list of spots (original datasheet) which is full
    and a public datasheet : whatever should be displayed (searched, sorted).
    """

    def __init__(self):
        pass
        #self._datasheet = []
        #self._publicdatasheet = []
        #self._sortedkey = None
        #self._sortedbackwards = False
        #self._source = config['file directory']

    def add_spot(self, spotmetadata):
        self._datasheet.append(spotinfo)
        # for use of importing from MEDIA folder. These should be
        # strictly read
        #print 'ERROR ADDING %s TO DATASHEET' % spotmetadata
        # TODO - remove from datasheet, or else indices will be screwed up

    def search(self, searchterm):
        # TODO - always returns from original ordering...
        # filters base datasheet for string...
        self.freshen()
        self._publicdatasheet = [spot for spot in self._publicdatasheet if
                                 any(searchterm.lower() in spot[header].lower()
                                     for header in spot)]

    def __iter__(self):
        # allows to iterate through all spots in the datasheet
        return iter(self._publicdatasheet)

    def get_filepath_for_index(self, index):
        return self._publicdatasheet[index]['fullfilepath']

    def fillable(self):
        """return the public contents in a form useable for the menu GUI"""
        return self._publicdatasheet

    def sort_by_key(self, key):
        """sort the public datasheet by the selected column header"""
        sortbackwards = (True if self._sortedkey == key and not
                         self._sortedbackwards else False)
        self._publicdatasheet = sorted(self._publicdatasheet,
                                       key=operator.itemgetter(key),
                                       reverse=sortbackwards)
        self._sortedkey = key
        self._sortedbackwards = sortbackwards

    def freshen(self):
        # when datasheet is brought to top, it resets its filter and randomizes
        self._publicdatasheet = self._datasheet
        self._sortedkey = None
        self._sortedbackwards = False
        random.shuffle(self._publicdatasheet)

    def query_source(self):
        """ go to source directory directly and check files in folder"""
        for spotbox_file in all_spotbox_files(self._source):
            try:
                self.add_spot(spot_info)
            except:
                print 'problem adding polling to datasheet. MAJOR PROBLEM'


class DatasheetNotebook(object):
    """An object that holds all information about the spotbox files"""

    def __init__(self, media_directory, file_config):
        #self._currentdatasheet = None
        #self._lastdatasheet = None
        self._datasheets = {spottype: Datasheet() for spottype in file_config}
        #self._media_directory = media_directory
        # Create a list of static headers
        """From media folder , pull out all files and create dict by header."""
        for path in all_spotbox_files(media_directory):
            filenamecomponents = split_file_name(path)
            spot_type = filenamecomponents[0]
            if spot_type not in file_config:
                continue
            #print file_config[spot_type]
            #    self._datasheets[testkey].add_spot(filenamecomponents)
            #for menukey in menu_config:
            #if (configuration[menukey]['static or polling'] == 'static'
        #    self.get_datasheets_from_media_folder(menukey)
        #for datasheet in self._datasheets:
        #    datasheet.freshen()

    def __iter__(self):
        """allows iteration through the datasheets in the notebook"""
        return iter(self._datasheets.values())

    def get_fresh_sheet_by_key(self, key):
        """simply give the datasheet for the key because it's freshened
        when the currentdatasheet is set, you don't have to freshen
        it here; saves on computation; the sheet can be served quicker
        """
        return self._datasheets[key]

    @property
    def currentdatasheet(self):
        return self._currentdatasheet

    @currentdatasheet.setter
    def currentdatasheet(self, datasheet):
        # set the currentsheet, and then freshen the old sheet.
        # so it's re-randomized, etc, before you get to it again
        oldsheet = self._currentdatasheet
        self._currentdatasheet = datasheet
        if oldsheet is not None:
            oldsheet.freshen()

    def subject_from_filepath(self, filepath):
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


def split_file_name(filename):
    """Extracts metadata (underscore-separated)"""
    basename = os.path.splitext(os.path.basename(filename))[0]
    return tuple(basename.split('_'))

    # Hard-coded way to disregard 'Icon' files (stupid Mac thing):
    #if len(fname) <= 5 or 'Icon' in fname:


def all_spotbox_files(media_dir):
    """Go into folder, and track all files. only look at files, and not hidden files"""
    paths = [os.path.join(media_dir, fname) for fname in os.listdir(media_dir)
             if not fname.startswith('.')]
    return (x for x in paths if os.path.isfile(x))
