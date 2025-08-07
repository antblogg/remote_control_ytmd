import scripts.search_engine as search_engine
import scripts.video_player as video_player
import scripts.api_interface as api_interface 
import segno
from flask import request


def update_qr_code(link):
    qr_code =segno.make(link)
    qr_code.save(out="static/img/qr_code.png", scale=5.0, dark='indigo', light='goldenrod')
    
def get_playlist_link():
    link = search_engine.get_queue_playlist_link() 
    update_qr_code(link)
    return link


def start_playlist():
    link = search_engine.get_queue_playlist_id()
    ytmd = api_interface.ytmd_load()
    video_player.play_playlist(ytmd, link)

def restart_playlist():
    search_engine.create_new_queue_playlist()



def add_to_queue():
    ytmusic = search_engine.generate_authenticated_ytmusic()
    queueid = search_engine.get_queue_playlist_id()
    video_id = request.args.get("videoId")
    print(queueid)
    print(video_id)
    ytmusic.add_playlist_items(playlistId=queueid,videoIds=[video_id])
        

    




