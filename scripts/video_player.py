from scripts.api_interface import ytmd_load
from ytmd_sdk import YTMD
from flask import request
import json


def generate_data(id: str, is_playlist: bool) -> dict:
    if is_playlist:
        data = {
        "videoId": None,
        "playlistId": id
        }
    else:
        data = {
        "videoId": id,
        "playlistId": None
        }
    return data

def play_video(ytmd: YTMD, video: str):
    ytmd._command(command="changeVideo", data=generate_data(video, is_playlist=False))

def play_playlist(ytmd: YTMD, playlist: str):
    ytmd._command(command="changeVideo", data=generate_data(playlist, is_playlist=True))

def play_media():
    is_playlist = request.args.get("isPlaylist")
    song_id = request.args.get("videoId")
    ytmd = ytmd_load()
    if is_playlist == "True":
        play_playlist(ytmd, song_id)
    else:
        play_video(ytmd, song_id)

def refresh_player(song_id,playlist_id):
    ytmd = ytmd_load()
    data = {
        "videoId": song_id,
        "playlistId": playlist_id
    }
    ytmd._command(command="changeVideo", data=data)
