"""SPOTBOX media playback backend"""




class Playback:
    """A playback object, allows for audio files to be loaded, played back,
    and stopped whilst playing.
    """

    #def initialize_one_player(self, spotnumber):
    #    raise NotImplementedError

    def load(self, spotnumber, filepath):
        raise NotImplementedError

    def play(self, spotnumber):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError


class StubPlayback(Playback):

    def load(self, spotnumber, filepath):
        print('LOADING {} ({})'.format(spotnumber, filepath))

    def play(self, spotnumber):
        print('PLAYING {} ({})'.format(spotnumber, filepath))

    def stop(self):
        print('STOPPING {} ({})'.format(spotnumber, filepath))


class iTunesPlayback(Playback):
    # imperfect: itunes volume/ repeat mode is not currently handled directly.

    def __init__(self):
        try:
            import appscript
            import mactypes
        except ImportError:
            raise RuntimeError('you shouldnt use itunes mode')
        # TODO - number of playlists.
        self.itunes = self.appscript.app('iTunes')
        # make sure iTunes is opened???? TODO
        # USEFUL: applescript directory:
        # http://www.mugginsoft.com/html/kosmictask/ASDictionaryDocs/Apple/
        #iTunes/OS-X-10.7/iTunes-10.6.1/html/

    def initialize_one_player(self, spotnumber):
        # iTunes doesn't need to, assuming the playlists
        # have been created (TODO - check?)
        #try:
        #    tab.visible()
        #except:
        #   throw a toplevel warning to create such a playlist...
        pass

    def stop(self):
        self.itunes.stop()

    def load(self, spotnumber, filepath):
        playlisttoload = self.itunes.playlists['SPOTBOX' + str(spotnumber + 1)]
        playlisttracks = playlisttoload.tracks()
        if len(playlisttracks) > 0:
            self.itunes.delete(playlisttoload.tracks)
        self.itunes.add(self.mactypes.Alias(filepath), to=playlisttoload)
        # Now check to make sure the file actually loaded:
        playlisttracks = playlisttoload.tracks()
        if len(playlisttracks) == 0:
            # if the playlist is now empty, it's an error. don't continue.
            # possible reasons: it's a non-music file, that iTunes won't accept
            #                   it's a corrupted mp3, etc
            # Don't list the name in the 'load' text.
            return False
        # Check (enable) the file, (index 0 because
        # there can be only one) to make sure it plays!
        playlisttracks[0].enabled.set(1)
        return True

    def play(self, spotnumber):
        self.itunes.play(self.itunes.playlists['SPOTBOX'+str(spotnumber+1)])


class PygletPlayback(Playback):

    def __init__(self):
        import pyglet
        self.playerarray = []

    def initialize_one_player(self, spotnumber):
        pygplayer = self.pyglet.media.Player()
        self.playerarray.append(pygplayer)

    def stop(self):
        for player in self.playerarray:
            player.pause()

    def load(self, spotnumber, filepath):
        # at moment, throws "NOT A WAVE" exception, even for .wav
        print filepath
        media = self.pyglet.media.load(filepath, streaming=False)
        del self.playerarray[spotnumber]
        self.playerarray[spotnumber].queue(media)

    def play(self, spotnumber):
        self.playerarray[spotnumber].play()

valid_modes = {'ITUNES': iTunesPlayback, 'STUB': StubPlayback}
