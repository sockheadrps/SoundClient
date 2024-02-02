from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from utils.playlist import Playlist
from fastapi.encoders import jsonable_encoder
import os
import signal
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
from utils.playlist import session
from fastapi import Path
from fastapi import HTTPException
from queue import Queue
from sound import sound_loop
from threading import Thread
import json


current_playlist = None
event_queue = Queue()
media_path = os.path.join(os.getcwd(), "media")
app = FastAPI()

origins = ["http://localhost", "http://localhost:8080",
           "http://localhost:5173", "http://127.0.0.1"]
websocket_clients = []

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/playlist/{playlist_name}")
def read_playlist(playlist_name: str = Path(..., title="The name of the playlist you want to retrieve")):
    playlist = session.query(Playlist).filter(
        Playlist.playlist_name == playlist_name).first()

    if playlist:
        json_compatible_item_data = jsonable_encoder(
            {playlist.playlist_name: playlist.playlist_data})
        return JSONResponse(content=json_compatible_item_data)
    else:
        return JSONResponse(content={"message": f"Playlist '{playlist_name}' not found"}, status_code=404)


@app.put("/{playlist_name}/update")
def update_playlist(updated_playlist: Dict[Any, Any], playlist_name: str = Path(..., title="The name of the playlist you want to update")):
    playlist = session.query(Playlist).filter(
        Playlist.playlist_name == playlist_name).first()
    if playlist:
        playlist.playlist_data = updated_playlist['media']
        session.commit()
        return {"message": f"Playlist '{playlist_name}' updated successfully"}
    else:
        new_playlist = Playlist(
            playlist_name, from_list=updated_playlist['media'])
        session.add(new_playlist)
        session.commit()
        return {"message": f"Playlist '{playlist_name}' created successfully"}


@app.delete("/{playlist_name}/delete")
def delete_playlist(playlist_name: str = Path(..., title="The name of the playlist you want to delete")):
    playlist = session.query(Playlist).filter(
        Playlist.playlist_name == playlist_name).first()
    if playlist:
        session.delete(playlist)
        session.commit()
        return {"message": f"Playlist '{playlist_name}' deleted successfully"}
    else:
        return {"message": f"Playlist '{playlist_name}' not found"}


@app.get("/media")
def media():
    l = [os.path.join(media_path, file) for file in os.listdir(
        media_path) if file.endswith(".mp3")]
    media = Playlist("All Media", from_list=l)
    return JSONResponse(content={"media": media.data_to_dict()})


@app.get("/playlist_names")
def playlists():
    sorted_playlists = session.query(Playlist).order_by(
        Playlist.playlist_name.asc()).all()
    return JSONResponse(content={"playlist_names": [l.playlist_name for l in sorted_playlists]})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    websocket_clients.append(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            data = json.loads(data)
            if data.get("event"):
                print(f"Received event: {data['event']}")
                if data['event'] == 'load':
                    playlist = session.query(Playlist).filter(
                        Playlist.playlist_name == data.get('playlist')).first()
                    file_paths = [item['file']
                                  for item in playlist.playlist_data[playlist.playlist_name]]
                    p = Playlist(from_list=file_paths,
                                 title=playlist.playlist_name)
                    p.song_list = playlist.playlist_data
                    data['playlist'] = p
                event_queue.put(data)
                if data['event'] == 'break':
                    os.kill(os.getpid(), signal.SIGTERM)
            await websocket.send_json("event: success")
    except Exception as e:
        print(f"WebSocket connection closed with exception: {e}")
        raise e
    finally:
        # Remove the WebSocket client from the list when the connection is closed
        websocket_clients.remove(websocket)


if __name__ == "__main__":
    try:
        sound_thread = Thread(target=sound_loop, args=(event_queue,))
        sound_thread.start()
        uvicorn.run(app, host="127.0.0.1", port=8080)

    except KeyboardInterrupt:
        print("Ctrl + C pressed. Exiting...")
    finally:
        sound_thread.join()
        print("Exiting...")
