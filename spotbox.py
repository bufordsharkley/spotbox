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
2013-2016
"""

import os
import sys
import Tkinter as tk

import click

from spotbox import data
from spotbox import playback
from spotbox import gui
from spotbox import config

@click.command()
@click.option('--playback-mode', default='ITUNES',
              type=click.Choice(playback.valid_modes.keys()))
@click.option('--config-file', help='configuration file for spotbox')
def main(config_file, playback_mode):
    if config_file is None:
        raise RuntimeError('Please pass --config')
    cfg = config.process_raw_config_file(config_file)
    datasheets = data.DatasheetNotebook(cfg.media_directory, cfg.file_config)
    playback_obj = playback.valid_modes[playback_mode]()
    spotboxgui = gui.SpotboxGUI(cfg, datasheets, playback_obj)
    spotboxgui.run_continuously()

if __name__ == '__main__':
    main()
