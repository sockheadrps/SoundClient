from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from utils.playlist import Playlist, Masterlist, Song
from fastapi.encoders import jsonable_encoder
import os
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any

app = FastAPI()

origins = ["http://localhost", "http://localhost:8080", "http://localhost:5173", "http://127.0.0.1"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

app.mount("/static", StaticFiles(directory="static"), name="static")

meda_path = os.path.join(os.getcwd(), "media")
meda_path = rf"F:\wIPED\music\Nujabes\[Mp3] OST - Samurai Champloo (Complete Original Soundtrack)\samurai champloo music records - playlist [Tsutchie - fat jon]"
l = [os.path.join(meda_path, file) for file in os.listdir(meda_path) if file.lower().endswith(".mp3")]
play_list = Playlist("My playlist", from_list=l)

masterlist = Masterlist()
masterlist.add_playlist(play_list)
masterlist.save_playlists()



@app.get("/test")
def read_test():
    return JSONResponse(content={"tst": "test"})

@app.get("/playlist")
def read_playlist():
    json_compatible_item_data = jsonable_encoder({"Masterlist": masterlist.playlist_data})
    print(json_compatible_item_data)
    return JSONResponse(content=json_compatible_item_data)


@app.post("/save_playlist")
def save_playlist(playlist_data:Dict[Any, Any]):
    playlist_name = playlist_data['name']
    playlist_media = playlist_data['media']

    # Process the playlist data
    print(f"Playlist Name: {playlist_name}")
    print("Media:")
    for item in playlist_media:
        print(f"  Artist: {item['artist']}, Song: {item['title']}, File Path: {item['file_path']}")

    # Return a confirmation response
    return {"message": "Playlist saved successfully"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)