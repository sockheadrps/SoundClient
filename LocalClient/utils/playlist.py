import json
import os
import eyed3
from sqlalchemy import create_engine, Column, String
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
        if os.path.isfile(fp) and fp.endswith(".mp3"):
            self.file_path = fp
            self.title, self.artist = get_mp3_info(fp)
        else:
            raise ValueError(f"Invalid or non-MP3 file path: {fp}")

    def set_title(self, title):
        self.title = title

    def set_artist(self, artist):
        self.artist = artist

    def validate_file(self):
        return os.path.isfile(self.file_path) and self.file_path.endswith(".mp3")

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
            self.song_list = [Song(fp) for fp in from_list]
        else:
            self.song_list = []

    def add_song(self, song: Song):
        self.song_list.append(song)
        self.playlist_data.append(song.data_to_dict())

    def del_song_by_title(self, title):
        self.song_list.remove(title)

    def data_to_dict(self):
        dict_songs = []
        if hasattr(self, 'song_list'):
            for song in self.song_list:
                dict_songs.append(song.data_to_dict())
        else:
            self.title = self.playlist_name
            for song in self.playlist_data:
                dict_songs.append(song)

        return dict_songs


    def validate_songs(self):
        validated_songs = []
        for song in self.song_list:

            if song.validate_file():
                validated_songs.append(song)


load_dotenv()
database_url = os.getenv("DB_URL")
db_user = os.getenv("DB_USER")
db_user_password = os.getenv("DB_USER_PASSWORD")
SQLALCHEMY_DATABASE_URL = f"postgresql://{db_user}:{db_user_password}@{database_url}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
session = Session()


if __name__ == "__main__":
    load_dotenv()
    database_url = os.getenv("DB_URL")
    db_user = os.getenv("DB_USER")
    db_user_password = os.getenv("DB_USER_PASSWORD")
    SQLALCHEMY_DATABASE_URL = f"postgresql://{db_user}:{db_user_password}@{database_url}"

    engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
    Base.metadata.create_all(bind=engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    current_directory = os.path.dirname(__file__)
    meda_path = os.path.join(os.getcwd(), "media")
    l = [os.path.join(meda_path, file) for file in os.listdir(
        meda_path) if file.lower().endswith(".mp3")]

    play_list = Playlist("My playlist", from_list=l)
    play_list.playlist_data = play_list.data_to_dict()

    session.add(play_list)
    session.commit()
