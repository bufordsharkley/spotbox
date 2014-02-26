# Directories for files:
PARENTDIRECTORY = '/Applications/SPOTBOX/'

#Configure the folders:

folderconfiguration = {
                       'MEDIADIRECTORY': PARENTDIRECTORY + 'MEDIA/',
                       # The os.path.expanduser makes the tilde work as intended (home folder).
                       'DROPBOXDIRECTORY': os.path.expanduser('~/Dropbox/'),

                       'GRAPHICPATH': PARENTDIRECTORY + 'spotboxgraphicsmall.gif'
                      }

# CONFIGURATION:

#Follow the format for configuring your menus:
#(
#for each key, which for media files is also the first token in a filename for a file of this type
# button order      : ordering for the radio buttons in header in GUI
# title             : Name that appears next to radio buttons
# menu headers      : The header text/widths for each menu (tuples)
# static or polling : either 'static' or 'polling', on whether updates are continuous
# file directory    : The directory for this menu's files
# filename indices  : The indices for the tokens in the file names for this menu, in re: headers
# index timer       : which index is for time [important for countdown display]
# index subject     : which index is for text display (integer) [appears next to play button]
#

configuration = {
                 'PSA'   :
                          {'button order'      : 0,
                           'title'             : 'PSA',
                           'menu headers'      : (('Subject', 37),
                                                  ('Time', 4),
                                                  ('Soundbed', 23),
                                                  ('Voice/Author', 22),
                                                  ('Outro', 1),
                                                  ('Kill', 1),
                                                  ('Added', 1)),
                           'static or polling' : 'static',
                           'file directory'    : folderconfiguration['MEDIADIRECTORY'],
                           'filename indices'  : [3, 2, 4, 5, 6, 7, 8],
                           'index timer'       : 2,
                           'index subject'     : 3
                          },
                 'LID'   :
                          {'button order'      : 1,
                           'title'             : 'LID',
                           'menu headers'      : (('LID', 22),
                                                  ('Description', 45),
                                                  ('Time', 4),
                                                  ('LID Type', 15),
                                                  ('Year', 1)),
                           'static or polling' : 'static',
                           'file directory'    : folderconfiguration['MEDIADIRECTORY'],
                           'filename indices'  : [3, 4, 2, 5, 6],
                           'index timer'       : 2,
                           'index subject'     : 3
                          },
                 'PROMO' :
                          {'button order'      : 2,
                           'title'             : 'Promos',
                           'menu headers'      : (('KZSU Show', 24),
                                                  ('Soundbed', 24),
                                                  ('Time', 5),
                                                  ('Day/Time', 17),
                                                  ('Voice/Author', 20),
                                                  ('Added', 1),
                                                  ('Now?', 1)),
                           'static or polling' : 'static',
                           'file directory'    : folderconfiguration['MEDIADIRECTORY'],
                           'filename indices'  : [3, 9, 2, 5, 6, 7, 8],
                           'index timer'       : 2,
                           'index subject'     : 3
                          },
                 'SFX'   :
                          {'button order'      : 3,
                           'title'             : 'Sound Effects',
                           'menu headers'      : (('Sound Effect', 21),
                                                  ('Description', 44),
                                                  ('Time', 5),
                                                  ('Type', 25)),
                           'static or polling' : 'static',
                           'file directory'    : folderconfiguration['MEDIADIRECTORY'],
                           'filename indices'  : [3, 4, 2, 5],
                           'index timer'       : 2,
                           'index subject'     : 3
                          },
                 'THEME' :
                          {'button order'      : 4,
                           'title'             : 'Show Themes',
                           'menu headers'      : (('Theme', 21),
                                                  ('Time', 5),
                                                  ('Description', 33),
                                                  ('KZSU Show', 16),
                                                  ('KZSU DJ', 15)),
                           'static or polling' : 'static',
                           'file directory'    : folderconfiguration['MEDIADIRECTORY'],
                           'filename indices'  : [3, 2, 4, 5, 6],
                           'index timer'       : 2,
                           'index subject'     : 3
                          },
                 'UW'    :
                          {'button order'      : 5,
                           'title'             : 'UW',
                           'menu headers'      : (('Underwriting', 37),
                                                  ('Time', 4),
                                                  ('Soundbed', 23),
                                                  ('Voice/Author', 22),
                                                  ('Outro', 1),
                                                  ('Kill', 1),
                                                  ('Added', 1)),
                           'static or polling' : 'static',
                           'file directory'    : folderconfiguration['MEDIADIRECTORY'],
                           'filename indices'  : [3, 2, 4, 5, 6, 7, 8],
                           'index timer'       : 2,
                           'index subject'     : 3
                          },
                 'NEWS'  :
                          {'button order'      : 6,
                           'title'             : 'Newscast',
                           'menu headers'      : (('Newscast for Today', 100),
                                                  ('Time', 20)),
                           'static or polling' : 'polling',
                           'file directory'    : folderconfiguration['DROPBOXDIRECTORY'],
                           'filename indices'  : [1, 2],
                           'index timer'       : 2,
                           'index subject'     : 1
                          },
                }
