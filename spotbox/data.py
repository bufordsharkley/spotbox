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
        info = dict(zip((x.lower() for x in config_components[1:]),
                        components[1:]))
        self.type = prefix
        self.path = path
        self.subject = info[_find_subject_field(config_components[1:])]
        self.time = _convert_to_seconds(info['time'])
        self.info = info


def _find_subject_field(components):
    for field in components:
        if field.lower() != 'time':
            return field.lower()
    else:
        raise RuntimeError('No subject in configs: {}'.format(components))


def _convert_to_seconds(timestring):
    # format we assume: m.ss
    minutes, seconds = (int(x) for x in timestring.split('.'))
    return 60 * minutes + seconds


class Datasheet(object):
    """list of lists (dicts?), basically. Searchable, sortable.

    Each has a list of spots (original datasheet) which is full
    and a public datasheet : whatever should be displayed (searched, sorted).
    """

    def __init__(self):
        self._all_spots = set()
        self._public = []

    def add_spot(self, spot):
        self._all_spots.add(spot)

    def search(self, searchterm):
        self.reset()
        self._public = [spot for spot in self._public if
                        any(searchterm.lower() in field.lower()
                            for field in spot.info.values())]

    def __getitem__(self, index):
        return self._public[index]

    def __iter__(self):
        # allows to iterate through all spots in the datasheet
        return iter(self._public)

    def sort(self, key, reverse=False):
        self._public = sorted(self._public,
                              key=lambda x: x.info[key.lower()],
                              reverse=reverse)

    def reset(self):
        # when datasheet is brought to top, it resets its filter and randomizes
        self._public = list(self._all_spots)
        random.shuffle(self._public)


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
