import os
import numpy as np
import subprocess
from threading import Thread

if os.name == 'nt':
    import winsound


class AudioHandler():
    def __init__(self, path = None, audio_file=None):
        self.sound_files = []
        self.path = path
        self.audio_file = audio_file
        self.enabled = 1

    def build(self):
        if self.path is not None:
            filelist=os.listdir('Canvas/'+self.path)
            for song in filelist:
                if song.endswith(".wav") or song.endswith(".mp3"):
                    self.sound_files.append(song)

    def __play_in_bg(self, f):
        command = ""
        if os.name == 'nt':
            if self.path is None:
                winsound.PlaySound('{}'.format(f), winsound.SND_FILENAME)
            else:
                winsound.PlaySound('{0}/{1}'.format('Canvas/' + self.path, f), winsound.SND_FILENAME)
        else:
            if self.path is None:
                command = 'play {}'.format(f)
            else:
                command = 'play {0}/{1}'.format('Canvas/' + self.path, f)
            subprocess.call(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def play_sound_effect(self, f):
        if self.enabled:
            th = Thread(target=self.__play_in_bg, args=(f,))
            th.start()

    def play_random_effect(self):
        if self.path is None:
            self.play_sound()
        else:
            f = np.random.choice(self.sound_files)
            self.play_sound_effect(f)

    def play_sound(self, path = None):
        if path is not None:
            self.play_sound_effect(path)
        elif self.audio_file is not None:
            self.play_sound_effect(self.audio_file)
        

