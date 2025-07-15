from flask import request
from ytmusicapi import YTMusic


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
    songs = music.search(query=query, filter="songs", limit=5)[:6]
    out = list()
    for song in songs:
        out.append(get_song_data(song, isplaylist=False))
    return out

def get_playlist(query):
    music = YTMusic()
    playlists = music.search(query=query, filter="playlists", limit=5)[:6]
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
    albums = music.search(query=query, filter="albums", limit=5)[:6]
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
     

if __name__=="__main__":
    pass
