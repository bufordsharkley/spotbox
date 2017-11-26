"""SPOTBOX media playback backend"""

import os
import stat
import subprocess
import sys
import time



class Playback:
    """A playback object, allows for audio files to be loaded, played back,
    and stopped whilst playing.
    """
    def __init__(self, config):
        pass

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

    def __init__(self, config):
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

    def __init__(self, config):
        try:
            self._mplayer = config.mplayer
        except AttributeError:
            self._mplayer = 'mplayer'
        self._chambers = {ii: None for ii in range(3)}
        self._fifopath = '/tmp/spotboxfifo'
        if not os.path.exists(self._fifopath):
            os.mkfifo(self._fifopath)
        if not stat.S_ISFIFO(os.stat(self._fifopath).st_mode):
            raise RuntimeError('{} is not a FIFO'.format(path))
        # Check that there isn't already something attached to fifo:
        if not self._is_attached_process():
            self._mplayer_spawn()

    def _is_attached_process(self):
        try:
            devnull = open(os.devnull, 'w')
            subprocess.check_call(['lsof', self._fifopath], stdout=devnull, stderr=devnull)
            return True
        except subprocess.CalledProcessError:
            return False

    def _mplayer_spawn(self):
        if sys.platform == "linux" or sys.platform == "linux2":
            command = ('gnome-terminal --command="mplayer '
                    '-slave -idle -input file={}"').format(path)
        elif sys.platform == "darwin":
            with open('/tmp/mplayer_command.sh', 'w') as f:
                f.write("{} -slave -idle -input file={}".format(self._mplayer, self._fifopath))
            command = 'open -a Terminal /tmp/mplayer_command.sh'
            st = os.stat('/tmp/mplayer_command.sh')
            os.chmod('/tmp/mplayer_command.sh', st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        else:
            raise RuntimeError('Unsupported platform {}'.format(sys.platform))
        print command
        subprocess.check_call(command, shell=True)

    def stop(self):
        with open('/tmp/spotboxfifo', 'w') as f:
            f.write('pause\n')
            f.write('stop\n')

    def load(self, spotnumber, spot):
        if not self._is_attached_process():
            pass
            #raise Exception("oh no")
        self._chambers[spotnumber] = spot

    def play(self, spotnumber):
        self.stop()
        spot = self._chambers[spotnumber]
        command = 'loadfile "{}"'.format(spot.path)
        with open('/tmp/spotboxfifo', 'w') as f:
            f.write('volume 100 1\n')
            f.write(command + '\n')



valid_modes = {'ITUNES': iTunesPlayback,
               'STUB': StubPlayback,
               'MPLAYER': MplayerPlayback}
