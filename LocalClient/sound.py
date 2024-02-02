import pygame
from time import sleep
from threading import Thread
import threading
from utils.playlist import Song


song_list = None
song_ended = False


class Sound:
    def __init__(self, playlist):
        self.playing = False
        self.current_idx = 0
        self.playing_thread = None
        self.volume = 1.0
        self.playlist = playlist

    def play(self, volume=1.0):
        self.stop()
        self.volume = volume
        self.playing = True
        self.playing_thread = Thread(target=self._play)
        self.playing_thread.start()
        

    def _play(self):
        pygame.mixer.init()
        song_list = self.playlist.song_list[self.playlist.title]
        pygame.mixer.music.load(
            song_list[self.current_idx]['file'])
        pygame.mixer.music.set_volume(self.volume)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            sleep(0.1)
        self.current_idx += 1
        self.stop()

    def pause(self):
        if self.playing:
            pygame.mixer.music.pause()
            self.playing = False
        else:
            pygame.mixer.music.unpause()
            self.playing = True

    def stop(self):
        if self.playing:
            pygame.mixer.music.stop()
            self.playing = False

            # Check if there is a playing thread and it is not the current thread
            if self.playing_thread and self.playing_thread != threading.current_thread():
                self.playing_thread.join()
                self.playing_thread = None
                print("Thread joined")

            # Commenting out the recursive call to self.play() to avoid recursion
            self.play()

            # Reset other attributes if needed
            # self.sound = None

    def is_playing(self):
        return self.playing

    def set_volume(self, volume):
        self.volume = volume
        if self.playing:
            pygame.mixer.music.set_volume(self.volume)

    def get_volume(self):
        return self.volume




# sound = Sound()
sound = None


def sound_loop(event_queue):
    while True:
        sleep(0.01)
        if not event_queue.empty():
            data = event_queue.get()
            # print(data)
            match data['event']:
                case "next":
                    sound.play()
                case "pause":
                    sound.pause()
                case "resume":
                    sound.pause()
                case "load":
                    sound = Sound(data['playlist'])
                case "volume":
                    sound.set_volume(data['volume']/100)
                case "prev":
                    pass
                case "current":
                    current = {
                        "playing": sound.is_playing(),
                        "volume": sound.get_volume(),

                    }
                case "break":
                    break
