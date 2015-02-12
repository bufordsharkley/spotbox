#!/usr/bin/python

"""SPOTBOX data backend"""

import os
from operator import itemgetter
import random


class Datasheet(object):
    """list of lists (dicts?), basically. Searchable, sortable."""
    # each has a list of spots (original datasheet) which is full
    # and a public datasheet : whatever should be displayed (searched, sorted)
    def __init__(self, config):
        self._originaldatasheet = []
        self._publicdatasheet = []
        self._menuheaders = [x[0] for x in config['menu headers']]
        self._indices = config['filename indices']
        self._sortedkey = None
        self._sortedbackwards = False
        self._source = config['file directory']

    def add_spot(self, spotmetadata):
        try:
            spotinfo = dict(zip(self._menuheaders, [spotmetadata[ii]
                                for ii in self._indices]))
            spotinfo['fullfilepath']=spotmetadata[0]
            self._originaldatasheet.append(spotinfo)
        except:
            # for use of importing from MEDIA folder. These should be
            # strictly read
            print 'ERROR ADDING %s TO DATASHEET' % spotmetadata
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
        if self._sortedkey == key and not self._sortedbackwards:
            sortbackwards = True
        else:
            sortbackwards = False
        self._publicdatasheet = sorted(self._publicdatasheet,
                                       key=itemgetter(key),
                                       reverse=sortbackwards)
        self._sortedkey = key
        self._sortedbackwards = sortbackwards

    def freshen(self):
        # when datasheet is brought to top, it resets its filter and randomizes
        self._publicdatasheet = self._originaldatasheet
        self._sortedkey = None
        self._sortedbackwards = False
        random.shuffle(self._publicdatasheet)

    def query_source(self):
        """ go to source directory directly and check files in folder"""
        for spot_info in extract_datasheet_from_dir(self._source):
            try:
                self.add_spot(spot_info)
            except:
                print 'problem adding polling to datasheet. MAJOR PROBLEM'


class DatasheetNotebook(object):
    """An object that holds all information about the spotbox files"""

    def __init__(self):
        self._currentdatasheet = None
        self._lastdatasheet = None
        self._datasheets = {}

    def update_from_configuration(self, folderconfiguration, configuration):
        self._config = configuration
        self._datasheets = {spottype: Datasheet(configuration[spottype])
                            for spottype in configuration}
        self._folders = folderconfiguration
        # Create a list of static headers
        statickeys = []
        for menukey in configuration:
            if (configuration[menukey]['static or polling'] == 'static'):
                statickeys.append(menukey)
        self.get_datasheets_from_media_folder(statickeys)
        for datasheet in self:
            datasheet.freshen()

    def get_fresh_sheet_by_key(self, key):
        """simply give the datasheet for the key because it's freshened
        when the currentdatasheet is set, you don't have to freshen
        it here; saves on computation; the sheet can be served quicker
        """
        return self._datasheets[key]

    def __iter__(self):
        """allows iteration through the datasheets in the notebook"""
        return iter(self._datasheets.values())

    @property
    def currentdatasheet(self):
        return self._currentdatasheet

    @currentdatasheet.setter
    def currentdatasheet(self, datasheet):
        # set the currentsheet, and then freshen the old sheet.
        # so it's re-randomized, etc, before you get to it again
        oldsheet = self._currentdatasheet
        self._currentdatasheet = datasheet
        if oldsheet:
            oldsheet.freshen()

    def get_datasheets_from_media_folder(self, statickeys):
        """From media folder , pull out all files and create dict
        by header.
        """
        for possiblefile in os.listdir(self._folders['MEDIADIRECTORY']):
            fullname = os.path.join(self._folders['MEDIADIRECTORY'],
                                    possiblefile)
            # disregard all subdirs, only look at files, and not hidden files:
            if (os.path.isfile(fullname) and not possiblefile[0] == '.'):
                filenamecomponents = split_file_name(fullname)
                testkey = filenamecomponents[1]
                if testkey in statickeys:
                    self._datasheets[testkey].add_spot(filenamecomponents)

    def subject_from_filepath(self, filepath):
        try:
            justthefilename = filepath.split('/')[-1]
            key = justthefilename.split('_')[0]
            subject = justthefilename.split('_')[self._config[key][
                'index subject'] - 1]
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
            justthefilename = filepath.split('/')[-1]
            key = justthefilename.split('_')[0]
            time = justthefilename.split('_')[self._config[key][
                'index timer'] - 1]
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


def split_file_name(filename):
    """Given complete file path, extracts metadata (underscore-separated)"""
    # TODO - don't assume it's a full path: have option for just the file name.
    # Look at only the file, remove file extension, and path:
    justthefilename = ((filename.rsplit('/', 1))[1]).rsplit('.', 1)[0]
    # the following line just gives it a little extra error protection against
    # user input error:
    justthefilename += '___'
    # Then split on underscores
    filenamecomponents = justthefilename.split('_')
    filenamecomponents.insert(0, filename)
    return filenamecomponents


def extract_datasheet_from_dir(directorystring):
    """Go into folder, and track all files"""
    # disregard all folders, only look at files, and not hidden files:
    filenamelist = []
    for possiblefile in os.listdir(directorystring):
        fullname = os.path.join(directorystring, possiblefile)
        if (os.path.isfile(fullname) and not possiblefile[0] == '.'):
            # Hard-coded way to disregard 'Icon' files (stupid Mac thing):
            # TODO make better
            if not ((len(possiblefile) <= 5) and ('Icon' in possiblefile)):
                filenamelist.append(split_file_name(
                    directorystring+possiblefile))
    return filenamelist


if __name__ == '__main__':
    pass
