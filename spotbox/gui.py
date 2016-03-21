import Tkinter as tk
import webbrowser

UPARROW = u'\u25b4'
DOWNARROW = u'\u25be'
DIAMOND = u'\u25c7'


class Countdown(tk.Label, object):
    """The countdown timer to the right of the spot subject.

    It lists length of file on load, and counts down until reaching zero,
    when it resets to original value.
    """

    def __init__(self, master):
        super(Countdown, self).__init__(master)
        self._original_time = None
        self._callbacks = []

    def load(self, seconds):
        self._original_time = seconds
        self._update_text(format_time(self._original_time))

    def _update_text(self, newtext, running=False):
        if running:
            newtext = '{}...'.format(newtext)
        self.configure(text=newtext)

    def kick_off(self):
        self._cancel_callbacks()  # When already-running job kicked off again.
        remaining = self._original_time
        self._continue_countdown(remaining)

    def _continue_countdown(self, remaining):
        if remaining < 0:
            return self.cancel_and_reset()
        self._update_text(format_time(remaining), running=True)
        self._callbacks.append(
            self.after(1000, self._continue_countdown, remaining - 1))

    def cancel_and_reset(self):
        """Stops running of counter, and resets at its initial value."""
        self._cancel_callbacks()
        if self._original_time is not None:
            self._update_text(format_time(self._original_time))

    def _cancel_callbacks(self):
        while self._callbacks:
            self.after_cancel(self._callbacks.pop())


def format_time(seconds):
    """Format integer time (i.e. 86) into correct format (1:26)"""
    minutes = 0
    seconds = seconds
    while seconds > 60:
        minutes += 1
        seconds -= 60
    return '{}:{:02d}'.format(minutes, seconds)


class LoadAndPlayButtons(tk.Frame, object):
    """Grid of load and play buttons, plus stop and help buttons"""

    def __init__(self, master, menus, playback, number_of_playlists):
        super(LoadAndPlayButtons, self).__init__(master)

        playlists = range(number_of_playlists)
        self._playback = playback
        self._menus = menus
        self.pack()

        stop = tk.Button(self, text="STOP", command=self._stop)
        help = tk.Button(self, text="HELP", command=self._help)
        spottexts = [tk.StringVar() for _ in playlists]
        labels = [tk.Label(self, textvariable=text) for text in spottexts]
        loaders = [tk.Button(self, text='LOAD' + str(ii+1),
                             command=lambda ii=ii: self._loadspot(spottexts[ii], ii))
                   for ii in playlists]
        players = [tk.Button(self, text='PLAY' + str(ii+1),
                             command=lambda ii=ii: self._playspot(ii))
                   for ii in playlists]

        for ii in playlists:
            pass
            #self._playback.initialize_one_player(ii)

        self.countdowns = [Countdown(master=self) for ii in playlists]

        # organize the placement of everything:
        stop.grid(row=0, column=1)
        help.grid(row=0, column=2)

        things = zip(loaders, players, labels, self.countdowns)
        for ii, (load, play, text, time) in enumerate(things):
            row = ii + 1
            load.grid(row=row, column=0)
            play.grid(row=row, column=1)
            text.grid(row=row, column=2)
            time.grid(row=row, column=3)

        for text in spottexts:
            text.set("no file loaded")

    def _stop(self):
        self._playback.stop()
        for countdown in self.countdowns:
            countdown.cancel_and_reset()

    def _help(self):
        window = tk.Toplevel()
        window.title('Help')
        helplabel = tk.Label(window, text='see github:bufordsharkley/spotbox.')
        helplabel.pack()
        def callback(event):
            webbrowser.open_new(r"http://www.github.com/bufordsharkley/spotbox")
        helplabel.bind("<Button-1>", callback)
        window.geometry("500x250")

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
        self._playback.load(spotnumber, self._menus.filepathtoload)
        spottext.set(self._menus.filesubjecttoload)
        self.countdowns[spotnumber].load(seconds=self._menus.filetimetoload)

    def _playspot(self, spotnumber):
        self._playback.play(spotnumber)
        countdowntostart = self.countdowns[spotnumber]
        for countdown in self.countdowns:
            if countdown is countdowntostart:
                countdown.kick_off()
            else:
                countdown.cancel_and_reset()


class CategorySelect(tk.Frame, object):
    """The radio buttons that select between menus"""
    def __init__(self, master, order, menus, header):
        super(CategorySelect, self).__init__(master)
        # assumes that it's being called from header... note: ???
        self._headerobject = header
        self.order = order
        self._menus = menus

        self.pack()
        self.menumode = tk.IntVar()
        self.menumode.set(1)  # this guy is one-indexed... TODO magic number
        radiobuttontypes = [(key, index+1) for index, key in enumerate(order)]
        # TODO
        # this currently displays LID, PSA, NEWS, SFX,
        # instead of "Sound Effects" etc.
        for index, typetuple in enumerate(radiobuttontypes):
            tk.Radiobutton(self,
                           text=typetuple[0],
                           variable=self.menumode,
                           command=self._update_menus,
                           value=typetuple[1]).grid(row=0, column=index)

    @property
    def _currentkey(self):
        # the menumode is the index of the radio button selected, but
        # one-indexed a correction is made, and the lookup table (used
        # to construct the radio buttons' order) is used to find key
        return self.order[self.menumode.get() - 1]

    def _update_menus(self):
        """Give the menus object the new key, have it update what is shown"""
        self._menus.update_menus_by_key(self._currentkey)
        self._headerobject.cleanup_after_change()


class SearchBox(tk.Frame, object):
    """Box for searching through menu, plus search and clear buttons"""

    def __init__(self, master, menus):
        super(SearchBox, self).__init__(master)
        self._menus = menus
        tk.Button(self,
                  text="Search",
                  command=self._search).grid(row=0, column=2)
        tk.Button(self,
                  text="Clear",
                  command=self._clear).grid(row=0, column=0)

        self._searchstring = tk.StringVar()
        self._searchstring.set('')

        self._searchentry = tk.Entry(self, textvariable=self._searchstring)
        self._searchentry.grid(row=0, column=1)
        self._searchentry.bind('<Return>', lambda e: self._search())

    def _search(self):
        searchterm = self._searchstring.get()
        self._menus.searchby(searchterm)

    def _clear(self):
        self.clear_text()
        self._search()  # Searching for blank string: retrieve everything.
                        # Gross trick.

    def clear_text(self):
        self._searchentry.delete(0, tk.END)


class MenuOfSpots(tk.Frame, object):
    """A menu object. Contains all metadata in columns, and also scrollbar"""
    def __init__(self, master, menusobject, key, headers, datasheet):
        super(MenuOfSpots, self).__init__(master)
        self.key = key
        self._datasheet = datasheet
        self._parent = menusobject

        # Which column is currently sorted, and how?
        # Defaults to -1 (no column is currently sorted):
        self._sortedcolumn = None
        self._sortedbackwards = False

        # each frame is a new column in the multi-column menu
        frames = [tk.Frame(self) for _ in headers]
        for frame in frames:
            frame.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)

        self._allcolumns = [tk.Listbox(frame,
                            width=header['width'],
                            borderwidth=0,
                            selectborderwidth=0,
                            relief=tk.FLAT,
                            exportselection=tk.FALSE)
                for ii, (header, frame) in enumerate(zip(headers, frames))]
        for column in self._allcolumns:
            column.pack(expand=tk.YES, fill=tk.BOTH)
            column.bind('<B1-Motion>', lambda e, s=self: s._select(e.y))
            column.bind('<Button-1>', lambda e, s=self: s._select(e.y))
            column.bind('<Leave>', lambda e: 'break')
            column.bind('<B2-Motion>', lambda e, s=self: s._select(e.y))
            column.bind('<Button-2>', lambda e, s=self: s._select(e.y))
            column.bind('<MouseWheel>', self._mousewheel)

        self._headerlist = [tk.StringVar() for _ in headers]

        self._headertext = [x['field'] for x in headers]
        for bip, x in zip(self._headerlist, self._headertext):
            bip.set(u'{} {}'.format(x, DIAMOND))

        self._labellist = [tk.Label(frame,
                               text=headerstring.get(),
                               borderwidth=1,
                               relief=tk.RAISED)
                            for frame, headerstring in zip(frames, self._headerlist)]
        for label in self._labellist:
            label.pack(fill=tk.X)
            label.bind('<Button-1>', lambda e, ii=ii: self._sort(ii))
        self._numberofcolumns = ii
        sb = tk.Scrollbar(self, orient=tk.VERTICAL, command=self._scroll)
        self._allcolumns[0]['yscrollcommand'] = sb.set
        sb.pack(side=tk.RIGHT, fill=tk.Y)

    def refresh(self):
        #self._datasheet = datasheets.get_fresh_sheet_by_key(self.key)
        self.fillwithcontent()

    def fillwithcontent(self):
        return
        self._fill_with(self._datasheet)
        self._turn_all_arrows_off()

    def _sort(self, columnnumber):
        # get key from columnnumber ...
        sortkey = self._headertext[columnnumber]
        # okay, that's fine. (but should be passed earlier?)
        self._datasheet.sort_by_key(sortkey)  # sure.
        # crashes for menus without . fix, TODO
        # (that is, menus with emergency fill)
        self._fill_with(self._datasheet)
        # update the information on currently sorted column:
        self._update_the_sort_labels(columnnumber)

    def _update_the_sort_labels(self, columnnumber):
        # the unicode manipulation here should be abstracted TODO
        if self._sortedcolumn == columnnumber and not self._sortedbackwards:
            # update the arrow in the header:
            self._headerlist[columnnumber].set(
                self._headerlist[columnnumber].get()[:-1] + UPARROW)
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
                self._headerlist[columnnumber].get()[:-1] + DOWNARROW)
            self._labellist[columnnumber].configure(
                text=self._headerlist[columnnumber].get())
            self._sortedbackwards = False
        self._sortedcolumn = columnnumber

    def _turn_all_arrows_off(self):
        for index, header in enumerate(self._headerlist):
            header.set(header.get()[:-1] + DIAMOND)
            self._labellist[index].configure(text=header.get())

    def _select(self, y):
        row = self._allcolumns[0].nearest(y)
        self._selection_clear(0, tk.END)
        self._selection_set(row)
        self._parent.filepathtoload = self._datasheet.get_filepath_for_index(row)
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
    def __init__(self, master, menus, lookuptable, playback, config):
        newframe = tk.Frame(master)
        newframe.pack()
        # the widgets that live in the header
        buttonarray = LoadAndPlayButtons(newframe, menus, playback, config.num_spots)
        categoryselect = CategorySelect(newframe, lookuptable.order, menus, self)
        self.searchbox = SearchBox(newframe, menus)

        # add the graphic...
        graphicfile = config.graphic
        graphic = tk.PhotoImage(file=graphicfile)
        graphicw = tk.Label(master, image=graphic)
        graphicw.image = graphic

        # organize and pack the insides, and then itself:
        graphicw.pack()
        buttonarray.pack()
        self.searchbox.pack()
        categoryselect.pack()

        """
        graphicw.grid(row=0, column=0)
        buttonarray.grid(row=0, column=1)
        self.searchbox.grid(row=2, column=0)
        categoryselect.grid(row=2, column=1)
        """

    def cleanup_after_change(self):
        # currently, only cleanup is clearing search box:
        self.searchbox.clear_text()


class Menus(object):
    """Menus object.

    Contains references to all existing menus. An instance is
    passed to other widgets, so that if menu manipulation is needed, it is
    coordinated through this object.
    """
    def __init__(self, master, datasheets, config):
        defaultkey = config.order[0]  # Defaults to first in order.
        self._datasheets = datasheets
        self._allmenus = {key: MenuOfSpots(master, self, key, config.headers[key],
            datasheets.get_fresh_sheet_by_key(key)) for key in config.order}

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
        #if self._currentmenu.static_or_polling == 'polling':
        # if it's polling, needs to be queried:
        #self._currentmenu.query()
        self._currentmenu.pack(expand=True, fill=tk.BOTH)
        oldmenu.freshen()

    def __iter__(self):
        return iter(self._allmenus.values())

    def searchby(self, searchterm):
        self._currentmenu.searchby(searchterm)


class SpotboxGUI(tk.Tk, object):

    def __init__(self, config, datasheets, playback):
        super(SpotboxGUI, self).__init__()

        self.title('{} Spotbox'.format(config.entity))
        self.geometry("1000x500")

        overallframe = tk.Frame(self)

        # header: frame that contains buttons, graphic, radio buttons, search.
        headerframe = tk.Frame(overallframe)
        headerframe.pack()
        # menu frame is the rest of the screen, which contains the menus.
        menuframe = tk.Frame(overallframe)
        menuframe.pack(expand=True, fill=tk.BOTH)
        menus = Menus(menuframe, datasheets, config.menu_config)
        header = Header(headerframe, menus, config.menu_config, playback, config)
        # an object that maintains all menus; info about spots to load
        # similar object for coordinating header widgets
        overallframe.pack(expand=True, fill=tk.BOTH)

    def run_continuously(self):
        self.mainloop()
