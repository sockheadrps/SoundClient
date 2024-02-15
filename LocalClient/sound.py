import pygame
from time import sleep
from threading import Thread,  Event, Lock

song_list = None
song_ended = False


class Sound:
    def __init__(self, event_queue):
        self.playing = None
        self.current_idx = 0
        self.playing_thread = None
        self.volume = 1.0
        self.event_queue = event_queue
        self.stop_event = Event()
        self.pause_event = Event()
        self.lock = Lock()
        pygame.mixer.init()
        self.load_paused = False

    def play(self, fp, paused=False):
        self.playing = True
        self.playing_thread = Thread(
            target=self._play, args=(fp, self.pause_event, paused))
        self.playing_thread.start()

    def _play(self, fp, pause_event, paused):
        if paused:
            while True:
                sleep(0.1)
                if not pause_event.is_set():
                    self.playing = True
                    break

        pygame.mixer.music.load(fp)
        pygame.mixer.music.set_volume(self.volume)
        pygame.mixer.music.play()

        while not self.stop_event.is_set() and pygame.mixer.music.get_busy():
            sleep(0.1)

            if pause_event.is_set():
                pygame.mixer.music.pause()
                while True:
                    sleep(0.1)
                    if self.load_paused:
                        # If the song is paused and the next button is pressed
                        self.stop()
                        self.load_paused = False
                        return
                    # is paused, and unpause is pressed
                    if not pause_event.is_set():
                        pygame.mixer.music.unpause()
                        self.playing = True
                        break
        self.stop()

    def pause(self):
        with self.lock:
            if self.playing:
                self.playing = False
                self.event_queue.put({"event": "pauseing"})
                self.pause_event.set()
            else:
                self.event_queue.put({"event": "unpausing"})
                self.pause_event.clear()

    def resume(self):
        # self.event_queue.put({"event": "resume"})
        self.pause_event.clear()

    def stop(self):
        self.event_queue.put({"event": "song_end"})
        self.stop_event.set()
        pygame.mixer.music.stop()
        self.stop_event.clear()

    def is_playing(self):
        with self.lock:
            return self.playing

    def set_volume(self, volume):
        self.volume = volume
        if self.playing:
            # self.event_queue.put({"event": "volume", "volume": volume})
            print(self.volume, "volume")
            pygame.mixer.music.set_volume(self.volume)
