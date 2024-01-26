import json
import os
import eyed3
from sqlalchemy import create_engine, ForeignKey, Column, Integer, String, CHAR
from sqlalchemy_utils import JSONType
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
from pathlib import Path

Base = declarative_base()


def get_mp3_info(file_path):
    audiofile = eyed3.load(file_path)

    if audiofile.tag:
        file_name = os.path.basename(file_path)
        title = audiofile.tag.title if audiofile.tag.title else file_name
        artist = audiofile.tag.artist if audiofile.tag.artist else ""
        return title, artist
    else:
        print("No ID3 tag found in the file.")


class Song():
    def __init__(self, fp) -> None:
        if os.path.isfile(fp) and fp.lower().endswith(".mp3"):
            self.file_path = fp
            self.title, self.artist = get_mp3_info(fp)
        else:
            raise ValueError(f"Invalid or non-MP3 file path: {fp}")
        
    def set_title(self, title):
        self.title = title

    def set_artist(self, artist):
        self.artist = artist

    def validate_file(self):
        return os.path.isfile(self.file_path) and self.file_path.lower().endswith(".mp3")
    
    def data_to_dict(self):
        data = {
            'title': self.title,
            'artist': self.artist,
            'file': self.file_path
        }
        return data
    
    def __repr__(self):
        return json.dumps(self.data_to_dict(), indent=2)

        
class Playlist(Base):
    __tablename__ = 'playlist_db'
    playlist_name = Column(String, primary_key=True, unique=True)
    playlist_data = Column(JSONType)
    def __init__(self, title, from_list=False) -> None:
        self.song_list = []
        self.title = title
        self.song_list = []
        self.playlist_name = title
        self.playlist_data = []

        if from_list:
            for fp in from_list:
                self.add_song(Song(fp))
    
    def add_song(self, song: Song):
        self.song_list.append(song)
        self.playlist_data.append(song.data_to_dict())

    def del_song_by_title(self, title):
        self.song_list.remove(title)

    def data_to_dict(self):
        dict_songs = []
        for song in self.song_list:
            dict_songs.append(song)

        data = {
            self.title: dict_songs,
        }
        return data
    
    def __repr__(self) -> str:
        return f"Playlist: {self.title}, data: {self.data_to_dict()}"
    
    def validate_songs(self):
        validated_songs = []
        for song in self.song_list:
            
            if song.validate_file():
                validated_songs.append(song)
    

class Masterlist():
    def __init__(self) -> None:
        self.create_playlist_json()
        self.current_playlist = None
        self.playlist_data = {}
        self.load_playlists()

    def create_playlist_json(self):
        if not os.path.exists('utils/playlist.json'):
            with open('utils/playlist.json', 'w') as jsonfile:
                json.dump({}, jsonfile, indent=2)
        else:
            return

    def load_playlists(self):
        try:
            with open('utils/playlist.json', 'r') as jsonfile:
                self.playlist_data = json.load(jsonfile)
        except FileNotFoundError:
            print("File 'playlist.json' not found. Returning an empty playlist.")

    def save_playlists(self):
        json_data = {}
        for ps in self.playlist_data:
            play_list_name = ps
            if isinstance(ps, Playlist):
                play_list_list = [ps.data_to_dict() for ps in self.playlist_data[play_list_name]]
                json_data[play_list_name] = play_list_list
            else:
                if isinstance(ps[0], Song):
                    print('is a song')
                    json_data[play_list_name] = [s.data_to_dict() for s in self.playlist_data[ps]]
                else:
                    print('is a dict')
                    json_data[play_list_name] = [s for s in self.playlist_data[ps]]
                    for item in json_data[play_list_name]:
                        json_data[play_list_name] = item.data_to_dict()
                        print(f"item: {item} item type: {type(item)}")

        with open('utils/playlist.json', 'w') as jsonfile:
            json.dump(json_data, jsonfile, indent=2)
    

    def access_one(self, playlist_name):
        if self.playlist_data.get(playlist_name):
            self.current_playlist = playlist_name
            playlist = Playlist(play_list=self.playlist_data[playlist_name], title=playlist_name)
            return playlist
        
        
    def add_playlist(self, play_list: Playlist):
        title = next(iter(play_list.data_to_dict().keys()), None)
        p_list = play_list.data_to_dict()[title]
        self.playlist_data[title] = p_list
        self.save_playlists()


if __name__ == "__main__":
    load_dotenv()
    database_url = os.getenv("DB_URL")
    db_user = os.getenv("DB_USER")
    db_user_password = os.getenv("DB_USER_PASSWORD")
    SQLALCHEMY_DATABASE_URL = f"postgresql://{db_user}:{db_user_password}@{database_url}"
    print(SQLALCHEMY_DATABASE_URL)

    engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
    Base.metadata.create_all(bind=engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    current_directory = os.path.dirname(__file__)  # Get the directory of the current script
    meda_path = os.path.join(os.getcwd(), "./media")
    l = [os.path.join(meda_path, file) for file in os.listdir(meda_path) if file.lower().endswith(".mp3")]


    play_list = Playlist("My playlist", from_list=l)
    # masterlist = Masterlist()
    # masterlist.add_playlist(play_list)  
    # masterlist.save_playlists()

    session.add(play_list)
    session.commit()


