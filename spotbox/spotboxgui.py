#!/usr/bin/python

import Tkinter as tk

DEFAULTINDEX = 0  # the menu/buttons that are opened intially:
NUMBEROFPLAYLISTS = 3  # TODO - in configuration???


class Countdown(tk.Label):
    """The countdown timer to the right of the spot subject.
    lists length of file on load, counts down when played"""
    def __init__(self, master):
        tk.Label.__init__(self, master, text='')
        self._remaining = 0
        self._remainingfull = 0
        self._job = None  # Whether clock is currently running on this label

    def _silencealarm(self):
        if self._job is not None:
            self.after_cancel(self._job)
            self._job = None

    def cancel_and_reset(self):
        """Stops running of counter, and resets at its initial value"""
        self._remaining = -1
        # this simulates the clock running out, and thus resets it.

    def runcountdown(self, firsttrigger=False):
        """Starts running...."""
        # when called the first time, start countdown from full length of
        # countdown, scheduling the next call to this function.
        # on repeated calls, lowers time and continues, until time is zero.
        # silencealarm: first call, pointless. Later times, unsets alarm (?)
        self._silencealarm()
        if firsttrigger:
            self._remaining = self._remainingfull
            # isn't that already the case?
        if self._remaining < 0:
            if self['text'] != '':
                self.configure(text=format_time_integer(self._remainingfull))
                self._remaining = self._remainingfull
        else:
            self.configure(text=format_time_integer(self._remaining) + '...')
            # NECESSARY STEP: Go into Language & Text, and disable
            # ellipses replace.
            # track one second passing, and set up new alarm:
            self._remaining = self._remaining - 1
            self._job = self.after(1000, self.runcountdown)

    def loadcountdown(self, remaining=None):
        # remaining - time countdown in seconds
        if remaining is not None:
            self._remainingfull = remaining
            self._remaining = remaining  # delete this line?????
            self.configure(text=format_time_integer(self._remaining))


def format_time_integer(timeinteger):
    """Format integer time (i.e. 86) into correct format (1:26)"""
    if timeinteger < 60:
        minutes = '0'
        sec = str(timeinteger)
    else:
        minutes = timeinteger//60
        sec = str(timeinteger - 60*minutes)
        minutes = str(minutes)
    if len(sec) == 1:
        sec = '0' + sec
    return minutes + ':' + sec


class LoadAndPlayButtons(tk.Frame):
    """Grid of load and play buttons, plus stop and help buttons"""
    def __init__(self, master, menus, playback):
        tk.Frame.__init__(self, master)

        self._playback = playback
        self._menus = menus
        self.pack()
        self.stopbutton = tk.Button(self,
                                    text="STOP",
                                    command=lambda: self._stop())
        self.helpbutton = tk.Button(self,
                                    text="HELP",
                                    fg="red",
                                    command=self._help)

        self.stopbutton.grid(row=0, column=1)
        self.helpbutton.grid(row=0, column=2)

        spottextlist = [tk.StringVar() for x in range(NUMBEROFPLAYLISTS)]
        for text in spottextlist:
            text.set("no file loaded")
        self.countdownarray = []
        for ii in range(NUMBEROFPLAYLISTS):
                self.loadbutton = tk.Button(self,
                                            text='LOAD' + str(ii+1),
                                            command=lambda ii=ii:
                                            self._loadspot(spottextlist[ii], ii))
                self.playbutton = tk.Button(self,
                                            text='PLAY' + str(ii+1),
                                            command=lambda ii=ii:
                                            self._playspot(ii))
                self.labelspot = tk.Label(self, textvariable=spottextlist[ii])
                countdown = Countdown(self)
                # this can't be the best way to do it...
                self.countdownarray.append(countdown)

                # organize the placement of everything:
                self.loadbutton.grid(row=ii+1, column=0)
                self.playbutton.grid(row=ii + 1, column=1)
                # remove self-- pointless...
                self.labelspot.grid(row=ii + 1, column=2)
                countdown.grid(row=ii+1, column=3)
                self._playback.initialize_one_player(ii)
        # keystroke capture: TODO not implemented at present, owing to
        # mechanical difficulties
        #in console button capture
        #master.bind_all('<Tab>', lambda event: self._playplaylist(0))
        #master.bind_all('<Alt_L>', lambda event: self._playplaylist(1))
        #master.bind_all('<Escape>', lambda event: self._playplaylist(2))
        # etc prune to match actual number of playlists

    def _stop(self):
        self._playback.stop()
        for countdownapp in self.countdownarray:
            countdownapp.cancel_and_reset()

    def _help(self):
        helpwindow = tk.Toplevel()
        helpwindow.title('HELP')
        # TODO: rewrite as separate file.
        helplabel = tk.Label(helpwindow,
                             text='Help is being written. For now,\
                             contact Mark M with feedback.')
        helplabel.pack()
        helpwindow.geometry("500x250")

    def _loadspot(self, spottext, spotnumber):
        """ Loads file into given playlist

        Takes the file name currently stored as filepathtoload in data module,
        clears playlist and places respective file into playlist, read to be
        played. Also loads counter with the correct amount of time, based upon
        the metadata in the file.
        """
        # TODO: detect if playlist is currently playing,
        # and don't allow overwrite
        if not self._menus.filepathtoload:
            print "NOTHING TO LOAD"
            return
        success = self._playback.load(spotnumber, self._menus.filepathtoload)
        if success:
            spottext.set(self._menus.filesubjecttoload)
            self.countdownarray[spotnumber].loadcountdown(
                self._menus.filetimetoload)

    def _playspot(self, spotnumber):
        self._playback.play(spotnumber)
        countdowntostart = self.countdownarray[spotnumber]
        for countdown in self.countdownarray:
            if countdown is countdowntostart:
                countdown.runcountdown(firsttrigger=True)
            else:
                countdown.cancel_and_reset()


class CategorySelect(tk.Frame):
    """The radio buttons that select between menus"""
    def __init__(self, master, lookuptable, menus, header):
        tk.Frame.__init__(self, master)
        # assumes that it's being called from header
        self._headerobject = header
        self.lookuptable = lookuptable
        self._menus = menus

        self.pack()
        self.menumode = tk.IntVar()
        self.menumode.set(DEFAULTINDEX + 1)  # this guy is one-indexed...
        radiobuttontypes = []

        for index, key in enumerate(lookuptable):
            radiobuttontypes.append((key, index+1))
            # this currently displays LID, PSA, NEWS, SFX,
            # instead of "Sound Effects" etc.
            # TODO - use config: something like:
            #radiobuttontypes.append((configuration[key]['title'],index+1))
        for index, typetuple in enumerate(radiobuttontypes):
            txt = typetuple[0]
            modenum = typetuple[1]
            tk.Radiobutton(self,
                           text=txt,
                           variable=self.menumode,
                           command=self._update_menus,
                           value=modenum).grid(row=0, column=index)

    @property
    def _currentkey(self):
        # the menumode is the index of the radio button selected, but
        # one-indexed a correction is made, and the lookup table (used
        # to construct the radio buttons' order) is used to find key
        return self.lookuptable[self.menumode.get()-1]

    def _update_menus(self):
        """Give the menus object the new key, have it update what is shown"""
        self._menus.update_menus_by_key(self._currentkey)
        self._headerobject.cleanup_after_change()


class SearchBox(tk.Frame):
    """Box for searching through menu, plus search and clear buttons"""
    def __init__(self, master, menus):
        tk.Frame.__init__(self, master)

        self._menus = menus

        tk.Button(self,
                  text="Search",
                  command=lambda:
                  self._search()).grid(row=0, column=2)
        tk.Button(self,
                  text="Clear",
                  command=lambda:
                  self._clear_button_action()).grid(row=0, column=0)
        self._searchstring = tk.StringVar()
        self._searchentry = tk.Entry(self, textvariable=self._searchstring)
        self._searchentry.grid(row=0, column=1)
        self._searchstring.set('')
        self._searchentry.bind('<Return>', lambda e: self._search())

    def _search(self):
        searchterm = self._searchstring.get()
        self._menus.searchby(searchterm)

    def _clear_button_action(self):
        self.clear_text()
        self._search()

    def clear_text(self):
        self._searchentry.delete(0, tk.END)


class MenuOfSpots(tk.Frame):
    """A menu object. Contains all metadata in columns, and also scrollbar"""
    def __init__(self,
                 master,
                 menusobject,
                 key,
                 configtuple,
                 datasheet,
                 staticorpolling):
        tk.Frame.__init__(self, master)
        self.key = key
        self._config = configtuple
        self._allcolumns = []  # yeah, this can't be best...
        self._headertext = [labeltext for labeltext, width in configtuple]
        self._headerlist = []
        self._labellist = []
        self._datasheet = datasheet
        self._parent = menusobject

        self.static_or_polling = staticorpolling

        # Which column is currently sorted, and how?
        # Defaults to -1 (no column is currently sorted):
        self._sortedcolumn = None
        self._sortedbackwards = False

        for ii, (labeltext, width) in enumerate(configtuple):
            frame = tk.Frame(self)
            # each frame is a new column in the multi-column menu
            frame.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)
            headerstring = tk.StringVar()
            headerstring.set(labeltext + ' ' u'\u25C7')
            # that's not cryptic at all...
            a_label = tk.Label(frame,
                               text=headerstring.get(),
                               borderwidth=1,
                               relief=tk.RAISED)
            a_label.pack(fill=tk.X)
            lb = tk.Listbox(frame,
                            width=width,
                            borderwidth=0,
                            selectborderwidth=0,
                            relief=tk.FLAT,
                            exportselection=tk.FALSE)
            lb.pack(expand=tk.YES, fill=tk.BOTH)
            self._allcolumns.append(lb)
            self._headerlist.append(headerstring)
            self._labellist.append(a_label)
            lb.bind('<B1-Motion>', lambda e, s=self: s._select(e.y))
            lb.bind('<Button-1>', lambda e, s=self: s._select(e.y))
            lb.bind('<Leave>', lambda e: 'break')
            lb.bind('<B2-Motion>', lambda e, s=self: s._select(e.y))
            lb.bind('<Button-2>', lambda e, s=self: s._select(e.y))
            lb.bind('<MouseWheel>', self._mousewheel)
            a_label.bind('<Button-1>', lambda e, ii=ii: self._sort(ii))
        self._numberofcolumns = ii
        sb = tk.Scrollbar(self, orient=tk.VERTICAL, command=self._scroll)
        self._allcolumns[0]['yscrollcommand'] = sb.set
        sb.pack(side=tk.RIGHT, fill=tk.Y)

    def refresh(self):
        #self._datasheet = datasheets.get_fresh_sheet_by_key(self.key)
        self.fillwithcontent()

    def fillwithcontent(self):
        self._fill_with(self._datasheet)
        self._turn_all_arrows_off()

    def _sort(self, columnnumber):
        # get key from columnnumber ...
        sortkey = self._headertext[columnnumber]
        # okay, that's fine. (but should be passed earlier?)
        self._datasheet.sort_by_key(sortkey)  # sure.
        # crashes for menus without . fix, TODO
        # (that is, menus with emergency fill)
        #if current_static_or_polling() == STATIC:
        self._fill_with(self._datasheet)
        # update the information on currently sorted column:
        self._update_the_sort_labels(columnnumber)

    def _update_the_sort_labels(self, columnnumber):
        # the unicode manipulation here should be abstracted TODO
        if self._sortedcolumn == columnnumber and not self._sortedbackwards:
            # update the arrow in the header:
            self._headerlist[columnnumber].set(
                self._headerlist[columnnumber].get()[:-1]+u'\u25B4')
            self._labellist[columnnumber].configure(
                text=self._headerlist[columnnumber].get())
            self._sortedbackwards = True
        else:
            # if that's not the case, it's essentially
            # a column being sorted the first time.
            # Give it a down arrow, and turn all the other arrows off.
            self._turn_all_arrows_off()
            # append the down arrow to the last position:
            self._headerlist[columnnumber].set(
                self._headerlist[columnnumber].get()[:-1]+u'\u25BE')
            self._labellist[columnnumber].configure(
                text=self._headerlist[columnnumber].get())
            self._sortedbackwards = False
        self._sortedcolumn = columnnumber

    def _turn_all_arrows_off(self):
        for index, header in enumerate(self._headerlist):
            header.set(header.get()[:-1]+u'\u25C7')
            self._labellist[index].configure(text=header.get())

    def _select(self, y):  # not private... TODO
        row = self._allcolumns[0].nearest(y)
        self._selection_clear(0, tk.END)
        self._selection_set(row)
        self._parent.filepathtoload = \
            self._datasheet.get_filepath_for_index(row)
        return 'break'

    def _mousewheel(self, event):
        for column in self._allcolumns:
            column.yview("scroll", -event.delta, "units")
        return "break"

    def _scroll(self, *args):
        for column in self._allcolumns:
            column.yview(*args)

    def _delete(self, first, last=None):
        for column in self._allcolumns:
            column.delete(first, last)

    def get(self, first, last=None):
        result = []
        for l in self._allcolumns:
            result.append(l.get(first, last))
        if last:
            return map(None, *result)
        return result

    def index(self, index):
        self._allcolumns[0].index(index)

    def _insert(self, index, *elements):
        for e in elements:
            for ii, column in enumerate(self._allcolumns):
                column.insert(index, e[ii])

    def numcols(self):
        return self._numberofcolumns

    def _selection_clear(self, first, last=None):
        for column in self._allcolumns:
            column.selection_clear(first, last)

    def _selection_set(self, first, last=None):
        for column in self._allcolumns:
            column.selection_set(first, last)

    def _fill_with(self, datasheet):
        """Take a datasheet, make a copy of the list (so items can be removed
        without problem) iterate through take datasheet and load into the
        thing... Take list of list (metadata for all files), and load into menu
        """
        self._delete(0, tk.END)
        fillablecontent = datasheet.fillable()
        for spot in fillablecontent:
            # spot = dict of fields, with ...
            spotcontent = [spot[header] for header in self._headertext]
            self._insert(tk.END, spotcontent)

    def searchby(self, searchterm):
        self._datasheet.search(searchterm)
        self._fill_with(self._datasheet)
        # AND RESET HEADERS FOR SORT SYMBOLS, ETC
        self._turn_all_arrows_off()

    def freshen(self):
        self._datasheet.freshen()
        self._fill_with(self._datasheet)

    def query(self):
        """used for polling menus. updates datasheet from source."""
        self._datasheet.query_source()
        self._fill_with(self._datasheet)


class Header(object):
    """Header object. In charge of coordinating behavior of
    all widgets in header frame.
    """
    def __init__(self, master, menus, lookuptable, playback):
        # the widgets that live in the header
        buttonarray = LoadAndPlayButtons(master, menus, playback)
        categoryselect = CategorySelect(master, lookuptable, menus, self)
        self.searchbox = SearchBox(master, menus)

        PARENTDIRECTORY = '/Applications/SPOTBOX/'  # pass in config. TODO

        # add the graphic...
        graphicfile = PARENTDIRECTORY + 'spotboxgraphicsmall.gif'
        graphic = tk.PhotoImage(file=graphicfile)
        graphicw = tk.Label(master, image=graphic)
        graphicw.image = graphic

        # organize and pack the insides, and then itself:
        graphicw.grid(row=0, column=0)
        buttonarray.grid(row=0, column=1)
        self.searchbox.grid(row=2, column=0)
        categoryselect.grid(row=2, column=1)

    def cleanup_after_change(self):
        # currently, only cleanup is clearing search box:
        self.searchbox.clear_text()


class Menus(object):
    """Object that contains references to all existing menus. An instance is
    passed to other widgets, so that if menu manipulation is needed, it is
    coordinated through this object.
    """
    def __init__(self, master, configuration, datasheets, lookuptable):
        defaultkey = lookuptable[DEFAULTINDEX]
        self._datasheets = datasheets

        self._config = configuration

        self._allmenus = {}
        for key in lookuptable:
            spot_menu = MenuOfSpots(master,
                                    self,
                                    key,
                                    configuration[key]['menu headers'],
                                    datasheets.get_fresh_sheet_by_key(key),
                                    configuration[key]['static or polling'])
            self._allmenus[key] = spot_menu

        for menu in self:
            menu.fillwithcontent()

        self._currentmenu = self._allmenus[defaultkey]
        self._currentmenu.pack(expand=True, fill=tk.BOTH)
        self._filepathtoload = None
        self._subjecttoload = None
        self._timetoload = None

    @property
    def filepathtoload(self):
        # the last file (full path) that the user clicked:
        return self._filepathtoload

    @filepathtoload.setter
    def filepathtoload(self, newpath):
        self._filepathtoload = newpath
        # also update the subject and time fields for header:
        self._subjecttoload = self._datasheets.subject_from_filepath(
            self.filepathtoload)
        self._timetoload = self._datasheets.time_from_filepath(
            self.filepathtoload)

    @property
    def filesubjecttoload(self):
        return self._subjecttoload

    @property
    def filetimetoload(self):
        return self._timetoload
        return self._datasheets.time_from_filepath(self.filepathtoload)

    def update_menus_by_key(self, newkey):
        """Called by menu selector. Clears current menu, packs new menu,
        and then fills the menu that was just cleared (in order that you
        don't have to wait for menu to be randomized/etc.
        """
        self._currentmenu.pack_forget()
        oldmenu = self._currentmenu
        self._currentmenu = self._allmenus[newkey]
        # if new menu is static, load from existing version. if polling,
        # it needs to be queried
        if self._currentmenu.static_or_polling == 'polling':
            # if it's polling, needs to be queried:
            self._currentmenu.query()
        self._currentmenu.pack(expand=True, fill=tk.BOTH)
        oldmenu.freshen()

    def __iter__(self):
        return iter(self._allmenus.values())

    def searchby(self, searchterm):
        self._currentmenu.searchby(searchterm)


class SpotboxTkInterface(tk.Tk):
    def __init__(self, configuration, datasheets, playback):
        tk.Tk.__init__(self)

        # create master ordering of buttons...
        # configuration manipulation - lookuptable:
        # guarantees that indices won't conflict, even if config imperfect:
        lookuptable = {configkey: configuration[configkey]['button order']
                       for configkey in configuration}
        lookuptable = sorted(lookuptable, key=lookuptable.get)

        self.title('KZSU Spotbox')
        self.geometry("1000x500")

        overallframe = tk.Frame(self)

        # header: frame that contains buttons, graphic, radio buttons, search.
        headerframe = tk.Frame(overallframe)
        # menu frame is the rest of the screen, which contains the menus.
        menuframe = tk.Frame(overallframe)

        # an object that maintains all menus; info about spots to load
        menus = Menus(menuframe, configuration, datasheets, lookuptable)
        # similar object for coordinating header widgets
        header = Header(headerframe, menus, lookuptable, playback)

        headerframe.pack()
        menuframe.pack(expand=True, fill=tk.BOTH)
        overallframe.pack(expand=True, fill=tk.BOTH)

    def run_continuously(self):
        self.mainloop()

if __name__ == '__main__':
    pass
