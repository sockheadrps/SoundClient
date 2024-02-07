from fastapi import FastAPI, WebSocket, BackgroundTasks
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
from sound import Sound
from threading import Thread
import json
from time import sleep
import asyncio
from contextlib import asynccontextmanager




app = FastAPI()
event_queue = Queue()
notification_queue = Queue()
current_playlist = None
media_path = os.path.join(os.getcwd(), "media")

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
                
                # Stick the event in the event queue for sound loop to handle
                event_queue.put(data)

                # Kill server
                if data['event'] == 'break':
                    os.kill(os.getpid(), signal.SIGTERM)

            await websocket.send_json("event: success")
    except Exception as e:
        print(f"WebSocket connection closed with exception: {e}")
        raise e
    finally:
        websocket_clients.remove(websocket)


@app.on_event("startup")
async def on_start_up():
    asyncio.create_task(sound_loop())


async def sound_loop():
    current_idx = 0
    sound = Sound(event_queue)
    p_list = None
    current_playlist = None
    while True:
        await asyncio.sleep(0.01)
        if not event_queue.empty():
            data = event_queue.get()
            print(f"WS Loading event: {data['event']}")   
            match data['event']:
                case "load":
                    # Load playlist data from DB, get files paths and create a new playlist
                    playlist = session.query(Playlist).filter(
                        Playlist.playlist_name == data.get('playlist')).first()
                    file_paths = [item['file']
                                for item in playlist.playlist_data]
                    p_list = Playlist(from_list=file_paths,
                                title=playlist.playlist_name)
                    p_list.song_list = playlist.playlist_data
                    data['playlist'] = p_list
                    current_playlist = {"title": playlist.playlist_name,
                                        "song_list": p_list.song_list}

                case "break":
                     break
                
            if current_playlist is not None:
                event = None
                match data['event']:
                    case "next":
                        song = current_playlist
                        if sound.pause_event.is_set():
                            sound.stop()
                            sound.play(song['song_list'][current_idx]['file'], paused=True)
                            event = {"event": "load-paused", "song": song['song_list'][current_idx]}
                        else:
                            if sound.pause_event.is_set():
                                sound.pause_event.clear()
                                sound.stop()
                            sound.play(song['song_list'][current_idx]['file'])
                            event = {"event": "playing", "song": song['song_list'][current_idx]}
                        current_idx += 1
                    
                    case "song_end":
                        if current_idx < len(song['song_list']) and not sound.pause_event.is_set():
                            sound.play(song['song_list'][current_idx]['file'])
                            event = {"event": "playing", "song": song['song_list'][current_idx]}
                            current_idx += 1
                    
                    case "load-pause":
                        event = {"event": "paused"}
                        sound.load_paused = True
                        current_idx += 1

                    case "pause":
                        event = {"event": "paused"}
                        sound.pause()

                    case "resume":
                        event = {"event": "resumed"}
                        sound.resume()

                    case "volume":
                        event = {"event": "volume", "volume": data['volume']}
                        sound.set_volume(data['volume']/100)

                if event is not None:
                    for ws in websocket_clients:
                        await ws.send_json(event)


if __name__ == "__main__":
    try:
        uvicorn.run(app, host="127.0.0.1", port=8080, lifespan="on")

    except KeyboardInterrupt:
        print("Ctrl + C pressed. Exiting...")
    finally:
        print("Exiting...")

