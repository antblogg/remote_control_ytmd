from flask import request
from random import randint
from ytmusicapi import YTMusic, OAuthCredentials
from ytmusicapi.exceptions import YTMusicServerError
import json

def get_song_data(song, isplaylist):
    return {
            "title": song["title"],
           "videoId" : song["videoId"],
           "thumbnail" : song["thumbnails"][0]["url"],
            "artist" : song["artists"][0]["name"],
            "isPlaylist" : isplaylist
    }

def get_songs(query):
    music = YTMusic()
    songs = music.search(query=query, filter="songs")
    out = list()
    for song in songs:
        out.append(get_song_data(song, isplaylist=False))
    return out

def get_playlist(query):
    music = YTMusic()
    playlists = music.search(query=query, filter="playlists")
    out = list()
    for playlist in  playlists:
        play_id = music.get_playlist(playlistId=playlist["browseId"],limit=1)["id"]
        out.append({
            "title" : playlist["title"],
            "videoId" : play_id,
           "thumbnail" : playlist["thumbnails"][0]["url"],
           "artist" : playlist["author"],
           "isPlaylist" : True
        })
    return out
        

def get_album(query):
    music = YTMusic()
    albums = music.search(query=query, filter="albums")
    out = list()
    for album in  albums:
        out.append({
            "title" : album["title"],
            "videoId" : album["playlistId"],
           "thumbnail" : album["thumbnails"][0]["url"],
           "artist" : album["artists"][0]["name"],
           "isPlaylist" : True
        })
    return out
    

def get_artist_songs(artist_name):
    music = YTMusic()
    artist_id = music.search(query=artist_name, filter="artists",limit=1)[0]["browseId"]
    top_songs = music.get_artist(artist_id)["songs"]["results"]
    results = list()
    for song in top_songs:
       results.append(get_song_data(song, isplaylist=False))
    return results



def get_search_results():
    query = request.args.get("search_term")
    filter = request.args.get("filter")
 
    match filter:
        case "artists":
            return get_artist_songs(artist_name=query)        
        case "songs":
            return get_songs(query)
        case "playlists":
            return get_playlist(query)
        case "albums":
            return get_album(query)
        case _:
            return list()
     
def get_truncated_search_results():
    truncate_index = 30
    songs = get_search_results()
    for song in songs:
        song["title"] = song["title"][:truncate_index]
        song["artist"] = song["artist"][:truncate_index]
    return songs

def get_oauth_support_credentials():
    with open("data/credentials.json","r") as file:
        data = json.load(file)["oauth"]
        client = data["client_id"]
        secret = data["client_secret"]
        return (client, secret)
        

def generate_title():
    length = 15
    basechar = ord("a")
    out = str()
    for _ in range(length):
        charoffset = randint(0,25) 
        is_uppercase = randint(0,1)
        char: str = str(chr(basechar+charoffset))
        out += char.upper() if is_uppercase else char
    return out


def get_queue_playlist_id():
    with open("temp/queue_playlist_id.txt","r") as file:
        return file.read()

def save_queue_playlist_id(id):
    with open("temp/queue_playlist_id.txt","w") as file:
        file.write(id)


def get_queue_playlist_link():
    prefix = "https://music.youtube.com/playlist?list="
    playlist_id = get_queue_playlist_id()
    return prefix+playlist_id
    
def delete_old_playlist(ytmusic: YTMusic):
    id = get_queue_playlist_id()
    if not id == '':
        try:
            ytmusic.delete_playlist(id)
        except YTMusicServerError:
            return

def generate_authenticated_ytmusic():
    client, secret = get_oauth_support_credentials()
    credentials = OAuthCredentials(client_id=client, client_secret=secret)
    return YTMusic(auth="data/oauth.json", oauth_credentials=credentials)


def create_new_queue_playlist():
    ytmusic = generate_authenticated_ytmusic()
    delete_old_playlist(ytmusic)
    new_playlist_id = ytmusic.create_playlist(title=generate_title(), description="auto generated queue playlist", privacy_status="UNLISTED")
    save_queue_playlist_id(new_playlist_id)




if __name__=="__main__":
    delete_old_playlist(generate_authenticated_ytmusic())
    print(generate_title())
    pass
