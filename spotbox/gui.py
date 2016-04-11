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
        self.running = False

    def load(self, seconds):
        self._update_text(format_time(seconds))
        self._original_time = seconds

    def _update_text(self, newtext, running=False):
        if running:
            newtext = '{}...'.format(newtext)
        self.configure(text=newtext)

    def kick_off(self):
        self.running = True
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
        self.running = False
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

    def __init__(self, master, menus, playback_obj, playback_count):
        super(LoadAndPlayButtons, self).__init__(master)

        playlists = range(playback_count)
        self._playback = playback_obj
        self._menus = menus
        self.pack()

        stop = tk.Button(self, text="STOP", command=self._stop)
        help = tk.Button(self, text="HELP", command=self._open_github)
        spottexts = [tk.StringVar() for _ in playlists]
        labels = [tk.Label(self, textvariable=text) for text in spottexts]
        loaders = [tk.Button(self,
                             text='LOAD' + str(ii+1),
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

    def _open_github(self):
        webbrowser.open_new(r"http://www.github.com/bufordsharkley/spotbox")

    def _loadspot(self, spottext, index):
        """ Loads file into given playlist

        Takes the file name currently stored as spot_to_load in data module,
        clears playlist and places respective file into playlist, read to be
        played. Also loads counter with the correct amount of time, based upon
        the metadata in the file.
        """
        # TODO: detect if playlist is currently playing,
        # and don't allow overwrite
        if self._menus.spot_to_load is None:
            print "NOTHING TO LOAD"
            return
        spot = self._menus.spot_to_load
        if self.countdowns[index].running:
            return
        self._playback.load(index, spot)
        self.countdowns[index].load(seconds=spot.time)
        spottext.set(spot.subject)

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

        self.pack()
        self.menumode = tk.IntVar()
        self.menumode.set(0)
        # TODO this currently displays LID, PSA, NEWS, SFX,
        # instead of "Sound Effects" etc.
        for index, text in enumerate(order):
            tk.Radiobutton(self,
                           text=text,
                           variable=self.menumode,
                           command=self._update_menus,
                           value=index).grid(row=0, column=index)
        self._order = order
        self._menus = menus
        self._header = header

    def _update_menus(self):
        """Give the menus object the new key, have it update what is shown"""
        key = self._order[self.menumode.get()]
        self._menus.switch_to(key)
        self._header.update()


class SearchBox(tk.Frame, object):
    """Box for searching through menu, plus search and clear buttons"""

    def __init__(self, master, menus):
        super(SearchBox, self).__init__(master)
        search = tk.Button(self, text="Search", command=self._search)
        clear = tk.Button(self, text="Clear", command=self._clear)

        clear.grid(row=0, column=0)
        search.grid(row=0, column=2)

        searchstring = tk.StringVar()
        searchstring.set('')

        searchentry = tk.Entry(self, textvariable=searchstring)
        searchentry.grid(row=0, column=1)
        searchentry.bind('<Return>', lambda e: self._search())

        self._menus = menus
        self._searchstring = searchstring
        self._searchentry = searchentry

    def _search(self):
        self._menus.search(self._searchstring.get())

    def _clear(self):
        self.clear_text()
        self._search()  # Searching for blank string: retrieve everything.
                        # Gross trick.

    def clear_text(self):
        self._searchentry.delete(0, tk.END)


class MenuOfSpots(tk.Frame, object):
    """A menu object. Contains all metadata in columns, and also scrollbar"""

    def __init__(self, master, menusobject, header_info, datasheet):
        super(MenuOfSpots, self).__init__(master)

        # each frame is a new column in the multi-column menu
        frames = [tk.Frame(self) for _ in header_info]
        for frame in frames:
            frame.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)

        headers, labels = self._initialize_headers(header_info, frames)

        self._columns = [tk.Listbox(frame,
                                    width=info['width'],
                                    borderwidth=0,
                                    selectborderwidth=0,
                                    relief=tk.FLAT,
                                    exportselection=tk.FALSE)
                        for (info, frame) in zip(header_info, frames)]

        for column in self._columns:
            self._bind_column(column)

        scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL, command=self._scroll)
        self._columns[0]['yscrollcommand'] = scrollbar.set

        # Pack:
        for label in labels:
            label.pack(fill=tk.X)
        for column in self._columns:
            column.pack(expand=tk.YES, fill=tk.BOTH)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # attributes to remember:
        self._datasheet = datasheet
        # TODO - parent only called for spot to load--
        self._parent = menusobject
        self._headers = headers
        self._labels = labels

        self._sortedcolumn = None
        self._sortreversed = False

    def _initialize_headers(self, header_info, frames):
        headers = [tk.StringVar() for _ in header_info]

        for header, info in zip(headers, header_info):
            header.set(u'{} {}'.format(info['field'], DIAMOND))

        labels = [tk.Label(frame,
                           text=header.get(),
                           borderwidth=1,
                           relief=tk.RAISED)
                  for frame, header in zip(frames, headers)]
        for ii, label in enumerate(labels):
            label.bind('<Button-1>', lambda e, ii=ii: self._sort(ii))
        return headers, labels

    @staticmethod
    def _text_from_header(header):
        # ends with space then glyph...
        return header.get()[:-2]

    def _bind_column(self, column):
        column.bind('<B1-Motion>', lambda e, s=self: s._select(e.y))
        column.bind('<Button-1>', lambda e, s=self: s._select(e.y))
        column.bind('<Leave>', lambda e: 'break')
        column.bind('<B2-Motion>', lambda e, s=self: s._select(e.y))
        column.bind('<Button-2>', lambda e, s=self: s._select(e.y))
        # Mousewheel for OSX
        column.bind('<MouseWheel>', lambda e: self._mousewheel(-e.delta))
        # Mousewheel for Ubuntu
        column.bind('<Button-4>', lambda e: self._mousewheel(-1))
        column.bind('<Button-5>', lambda e: self._mousewheel(1))

    def refresh(self, reset_spots=False):
        # delete all, then insert all.
        if reset_spots:
            self._datasheet.reset()
        for column in self._columns:
            column.delete(0, tk.END)
        for spot in self._datasheet:
            spot_fields = [spot.info[self._text_from_header(header).lower()]
                           for header in self._headers]
            for ii, column in enumerate(self._columns):
                column.insert(tk.END, spot_fields[ii])

    def _sort(self, column_index):
        key = self._text_from_header(self._headers[column_index])
        self._datasheet.sort(key, reverse=self._sortreversed)
        # Toggle the reversed field:
        self._sortreversed = not self._sortreversed
        self.refresh()
        self._update_sort_label(column_index)

    def _update_sort_label(self, column_index):
        if self._sortedcolumn != column_index:
            self._turn_all_arrows_off()
            self._sortedcolumn = column_index
        glyph = UPARROW if self._sortreversed else DOWNARROW
        header = self._headers[column_index]
        label = self._labels[column_index]
        self._update_header_with_glyph(header, label, glyph)

    def _turn_all_arrows_off(self):
        for index, header in enumerate(self._headers):
            label = self._labels[index]
            self._update_header_with_glyph(header, label, glyph=DIAMOND)

    @staticmethod
    def _update_header_with_glyph(header, label, glyph):
        header.set(header.get()[:-1] + glyph)
        label.configure(text=header.get())

    def _select(self, y):
        row = self._columns[0].nearest(y)
        self._selection_clear(0, tk.END)
        self._selection_set(row)
        self._parent.spot_to_load = self._datasheet[row]
        # Stops each pane from being selected:
        return 'break'

    def _selection_clear(self, first, last=None):
        for column in self._columns:
            column.selection_clear(first, last)

    def _selection_set(self, first, last=None):
        for column in self._columns:
            column.selection_set(first, last)

    def _mousewheel(self, delta):
        for column in self._columns:
            column.yview("scroll", delta, "units")
        # An ancient tkinter trick from the old country:
        return 'break'

    def _scroll(self, *args):
        for column in self._columns:
            column.yview(*args)

    def search(self, searchterm):
        self._datasheet.search(searchterm)
        self.refresh()
        self._turn_all_arrows_off()



class Header(tk.Frame, object):
    """Header object. In charge of coordinating behavior of
    all widgets in header frame.
    """
    def __init__(self, master, menus, lookuptable, playback_obj, config):
        super(Header, self).__init__(master)
        #newframe = tk.Frame(master)
        #newframe.pack()
        self.pack()
        # the widgets that live in the header
        buttonarray = LoadAndPlayButtons(self, menus, playback_obj, config.num_spots)
        categoryselect = CategorySelect(self, lookuptable.order, menus, self)
        self.searchbox = SearchBox(self, menus)

        # add the graphic...
        graphicfile = config.graphic
        graphic = tk.PhotoImage(file=graphicfile)
        graphicw = tk.Label(self, image=graphic)
        graphicw.image = graphic

        # organize and pack the insides, and then itself:
        categoryselect.pack(side=tk.BOTTOM, fill=tk.X)
        self.searchbox.pack(side=tk.BOTTOM, fill=tk.X)
        buttonarray.pack(side=tk.RIGHT, fill=tk.BOTH)
        graphicw.pack(side=tk.LEFT)

        #graphicw.grid(row=0, column=0)
        #buttonarray.grid(row=0, column=1)
        #self.searchbox.grid(row=2, column=0)
        #categoryselect.grid(row=2, column=1)

    def update(self):
        # currently, only cleanup is clearing search box:
        self.searchbox.clear_text()


class Menus(object):
    """Menus object.

    Contains references to all existing menus. An instance is
    passed to other widgets, so that if menu manipulation is needed, it is
    coordinated through this object.
    """
    def __init__(self, master, datasheets, config):
        self._menus = {key: MenuOfSpots(master, self, config.headers[key],
                                           datasheets[key])
                          for key in config.order}
        for menu in self._menus.values():
            menu.refresh(reset_spots=True)

        # Defaults to first in order.
        self._currentmenu = self._menus[config.order[0]]
        self._currentmenu.pack(expand=True, fill=tk.BOTH)
        # the last file (full path) that the user clicked:
        self._spot_to_load = None

    def switch_to(self, newkey):
        """Clears current menu, packs new menu,
        and then fills the menu that was just cleared (in order that you
        don't have to wait for menu to be randomized/etc.
        """
        self._currentmenu.pack_forget()
        oldmenu = self._currentmenu
        self._currentmenu = self._menus[newkey]
        self._currentmenu.pack(expand=True, fill=tk.BOTH)
        oldmenu.refresh(reset_spots=True)

    def search(self, searchterm):
        return self._currentmenu.search(searchterm)

# class GUIState(object):

# currentmenu
# spot_to_load
# playback object


class SpotboxGUI(tk.Tk, object):

    def __init__(self, config, datasheets, playback_obj):
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
        header = Header(headerframe, menus, config.menu_config, playback_obj, config)
        # an object that maintains all menus; info about spots to load
        # similar object for coordinating header widgets
        overallframe.pack(expand=True, fill=tk.BOTH)

    def run_continuously(self):
        self.mainloop()
