#!/usr/bin/python

"""
Spotbox (aka digicart aka jinglebox) GUI, using TKinter

Scans directories for the relevant files (based upon configuration), adds to
several menus (searchable, sortable). Files can be loaded, and then played.
Time is kept track.

Options are available for automatic updating of directory-searches (for a
folder that may be altered remotely, and the contents should be updated)

Playback defaults to iTunes, using appscript. The places in code for alternate
implementations of audio playback (with pyglet, likely) are clear, but not yet
implemented.

Author: Mark Mollineaux
2013
"""

# if ITUNESMODE, it will run appscript and interface with iTunes.
# if not, it will run pyglet and run its own sound

# Note-- non-iTunes mode is not yet implemented.

ITUNESMODE = False

import os
from spotbox.spotboxdata import DatasheetNotebook
import spotbox.spotboxplayback as sbplayback
from spotbox.spotboxgui import SpotboxTkInterface
from spotbox.spotboxconfig import folderconfiguration, configuration


if __name__ == '__main__':
    datasheets = DatasheetNotebook()
    datasheets.update_from_configuration(folderconfiguration, configuration)
    if ITUNESMODE:
        playback = sbplayback.iTunesPlayback()
    else:
        # this class does nothing for load/play/stop/etc, just pass for each
        playback = sbplayback.Playback()
    spotboxgui = SpotboxTkInterface(configuration, datasheets, playback)
    spotboxgui.run_continuously()
