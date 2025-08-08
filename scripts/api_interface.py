from ytmd_sdk import Events, YTMD, Parser
from ytmd_sdk.parser import queue as ytmdqueue
from time import sleep
from threading import Lock
from time import time
import json
import os
from random import random

import scripts.search_engine as search_engine
import scripts.video_player as video_player

lock = Lock()

def get_lock():
    return Lock


def on_update(data):
    if not data:
        return

    with lock:
        playlist_id = data["playlistId"]
        if playlist_id == search_engine.get_queue_playlist_id():
            current_song_data =data["video"] 
            playlist_data = data["player"]

            song_duration = int(current_song_data["durationSeconds"])
            song_progress = int(playlist_data["videoProgress"])
            time_remaining = song_duration-song_progress

            skip_threshold_time = 3
            if time_remaining < skip_threshold_time:
                queue = playlist_data["queue"]
                queue_elements = queue["items"] 
                selected_index = int(queue["selectedItemIndex"])
                target_song = queue_elements[selected_index+1]
                target_song_id = target_song["videoId"]
                video_player.refresh_player(target_song_id,playlist_id)
        try: 
            with open("temp/song_data_temp.json","w") as file:
                json.dump(data, file, indent=4)
            os.replace("temp/song_data_temp.json", "temp/song_data.json")
        except (PermissionError, FileNotFoundError):
            pass


def read_data() -> dict:
    with lock:
        with open("temp/song_data.json","r") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return {}
   

def ytmd_load():
    ytmd = YTMD("soundbarcontroller", "SoundbarController", "1.0.0")
  
    with open("data/credentials.json", "r") as file:
        data = json.load(file)
        key = data["ytmd_token"] 
    if key == "insert token here":
        print("no token, autheniticate")
        key = ytmd.authenticate() # get token key and sets it at same time
        data.update({"ytmd_token": key})
        with open("data/credentials.json", "w") as file:
            json.dump(data, file, indent=4)
    else:
        ytmd.update_token(key) # if you already have a token key you can set it like this
    return ytmd

def ytmd_initialize_data(ytmd: YTMD):
    with lock:
        with open("temp/song_data.json", "w") as file:
            json.dump(ytmd.get_state().json(), file, indent=4)

def ytmd_connect_socket():
    ytmd = ytmd_load()
    ytmd_initialize_data(ytmd)
    ytmd.register_event(Events.state_update, on_update)
    ytmd.connect()
    sleep(0.5) # give a second for the api to catch up
    return ytmd

def safe_read_data():
    data = read_data()
    while data == {}:    
        data=read_data()

    statuscode_error = 429
    while data.get("statusCode") == statuscode_error:
        timeout_message = data["message"]
        delay_number_char_index = 30
        timeout_delay = timeout_message[delay_number_char_index]
        timeout_delay = int(timeout_delay)
        sleep(timeout_delay+1) # add a second to account for rounding. might be .5 but erring on the side of caution.
        ytmd_initialize_data(ytmd_load())
        data = read_data()   
        
    return data


def load_song_metadata():
    data = safe_read_data()         
    data = dict(data)
    parser = Parser(data)
    song_data = parser.video_state
    artist = song_data.author
    title = song_data.title
    if isinstance(song_data.thumbnails, list):
        thumbnail = song_data.thumbnails[-1].url  #select largest thumbnail
    else:
        thumbnail = song_data.thumbnails.url    
    return {
        "artist" : artist,
        "title" : title,
        "thumbnail" : thumbnail
        }

def toggle_loop():
    data = safe_read_data()
    parser = Parser(data)

    repeat_mode =parser.player_state.repeatMode
    if repeat_mode == 2: 
        toggled_repeat = 1
    else:
        toggled_repeat = 2
    ytmd_load().repeatMode(toggled_repeat)


    
def get_queue():
    data = safe_read_data()
    try:
        queue = data["player"]["queue"]
    except KeyError:
        return list()
    start_index = queue["selectedItemIndex"]
    items = queue["items"]
    end_index = len(items)
    out = list()
    if data["video"]["author"]== "null":
        return out
    for i in range(start_index, end_index):
        try:
            item = items[i]
        except IndexError:
            break
        if isinstance(item["thumbnails"], list):
            thumbnail = item["thumbnails"][0]["url"]  #select largest thumbnail
        else:
            thumbnail = item["thumbnails"]["url"]    
        out.append({
            "title" : item["title"],
            "artist" : item["author"],
            "thumbnail" : thumbnail
        })
    return out


def main():
    get_queue()

if __name__ == "__main__":    
    main()
