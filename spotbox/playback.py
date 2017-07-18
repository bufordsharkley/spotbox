"""SPOTBOX media playback backend"""

import os
import stat
import subprocess
import time



class Playback:
    """A playback object, allows for audio files to be loaded, played back,
    and stopped whilst playing.
    """
    def load(self, spotnumber, filepath):
        raise NotImplementedError

    def play(self, spotnumber):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError


class StubPlayback(Playback):

    def load(self, spotnumber, spot):
        print('LOADING {} ({})'.format(spotnumber, spot))

    def play(self, spotnumber):
        print('PLAYING {}'.format(spotnumber))

    def stop(self):
        print('STOPPING')


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
        # iTunes/OS-X-10.7/iTunes-10.6.1/html/

    def initialize_one_player(self, spotnumber):
        # iTunes doesn't need to, assuming the playlists
        # have been created (TODO - check?)
        # try:
        #    tab.visible()
        # except:
        #   throw a toplevel warning to create such a playlist...
        pass

    def stop(self):
        self.itunes.stop()

    def load(self, spotnumber, spot):
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


class MplayerPlayback(Playback):

    def __init__(self):
        self._chambers = {ii: None for ii in range(3)}
        path = '/tmp/spotboxfifo'
        if not os.path.exists(path):
            os.mkfifo(path)
        if not stat.S_ISFIFO(os.stat(path).st_mode):
            raise RuntimeError('{} is not a FIFO'.format(path))
        try:
            devnull = open(os.devnull, 'w')
            subprocess.check_call(['lsof', path], stdout=devnull, stderr=devnull)
        except subprocess.CalledProcessError:
            if False:
                command = ('gnome-terminal --command="mplayer '
                    '-slave -idle -input file={}"').format(path)
            else:
                command = 'open -b com.apple.terminal /tmp/shell.sh'
            subprocess.check_call(command, shell=True)

    def stop(self):
        with open('/tmp/spotboxfifo', 'w') as f:
            f.write('stop\n')

    def load(self, spotnumber, spot):
        self._chambers[spotnumber] = spot

    def play(self, spotnumber):
        spot = self._chambers[spotnumber]
        command = 'loadfile "{}"'.format(spot.path)
        with open('/tmp/spotboxfifo', 'w') as f:
            f.write('volume 100 1\n')
            f.write(command + '\n')



valid_modes = {'ITUNES': iTunesPlayback,
               'STUB': StubPlayback,
               'MPLAYER': MplayerPlayback}
