from ytmd_sdk import Events, YTMD, Parser
from ytmd_sdk.parser import queue as ytmdqueue
from time import sleep
from threading import Lock
from time import time
import json
import os
from random import random

lock = Lock()

def get_prev_song():
    with open("prev_song_id.txt", "r") as file:
        return file.read()

def update_prev_song(title):
    with open("prev_song_id.txt", "w") as file:
        file.write(title)


def on_update(data):
    try: 
        with lock:
            with open("song_data_temp.json","w") as file:
                json.dump(data, file, indent=4)
        
            os.replace("song_data_temp.json", "song_data.json")
    except (PermissionError, FileNotFoundError):
            pass


def read_data() -> dict:
    with lock:
        with open("song_data.json","r") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return {}
   

def ytmd_load():
    ytmd = YTMD("touchportalytmdd", "TouchPortalYTMDD", "1.0.0")
  
    with open("token.txt", "r") as file:
        key = file.read()
    if key == "":
        print("no token, autheniticate")
        key = ytmd.authenticate() # get token key and sets it at same time
        with open("token.txt", "w") as file:
            file.write(key)
    else:
        ytmd.update_token(key) # if you already have a token key you can set it like this
    return ytmd

def ytmd_initialize_data(ytmd: YTMD):
    with lock:
        with open("song_data.json", "w") as file:
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
    queue = data["player"]["queue"]
    start_index = queue["selectedItemIndex"]
    items = queue["items"]
    end_index = len(items)

    out = list()
    for i in range(start_index, end_index):
        item = items[i]
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
