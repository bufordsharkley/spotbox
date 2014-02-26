KZSU SPOTBOX
Written by Mark Mollineaux (2013) <bufordsharkley@gmail.com>
AKA "jingle box" AKA "digicart." Software that allows DJs to cue and play
back short audio tracks.

Uses Tkinter front-end, simple python backend, and allows for audio playback
through iTunes, through appscript, a python wrapper for Applescript. A more
cross-platform playback method may be Pyglet (not fully implemented), which
doesn't have the reliability of iTunes, but is less of a hacky implementation.

Allows for menus for multiple types of audio files (PSAs, LIDs), with metadata
configured in the filename itself. The menu headers/etc are configured in a
dict in the spotbox.py file.

Files are loaded statically on startup from the MEDIA folder. Any files that
need to be queried for updates (for instance, a Dropbox folder containing 
newscasts) are given the "polling" designation.
