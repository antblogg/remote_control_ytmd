from flask import Flask, render_template, request, redirect, url_for, jsonify
from search_engine import get_search_results
from video_player import play_media
import api_interface


app = Flask(__name__)
ytmd = api_interface.ytmd_connect_socket()

@app.route("/search")
def searchpage():
    query_results = get_search_results() 
    return render_template("searchpage.html", query_results = query_results)

@app.route("/search/play")
def play_new_song():
    play_media()
    return redirect(url_for("homepage"))
    

@app.route("/home")
def homepage():
    songdata = api_interface.load_song_metadata()
    return render_template("homepage.html", song=songdata)

@app.route("/home/toggle_playback")
def toggle_play():
    api_interface.ytmd_load().toggle_playback()
    return redirect(url_for("homepage"))

@app.route("/home/next")
def go_to_next():
    api_interface.ytmd_load().next()
    return redirect(url_for("homepage"))

@app.route("/home/back")
def go_to_prev():
    api_interface.ytmd_load().previous()
    return redirect(url_for("homepage"))

@app.route("/home/repeat")
def loop_song():
    api_interface.toggle_loop()
    return redirect(url_for("homepage"))

@app.route("/home/shuffle")
def shuffle_playlist():
    api_interface.ytmd_load().shuffle()
    return redirect(url_for("homepage"))

@app.route("/home/volume_up")
def raise_volume():
    api_interface.ytmd_load().volume_up()
    return redirect(url_for("homepage"))

@app.route("/home/volume_down")
def lower_volume():
    api_interface.ytmd_load().volume_down()
    return redirect(url_for("homepage"))

@app.route("/songdata")
def song_data():
   return api_interface.safe_read_data()

@app.route("/queue")
def queuepage(): 
    queue = api_interface.get_queue()
    return render_template("queuepage.html", queue_items = queue)


  

@app.route("/") 
def index():
    return homepage()



def main():
    app.run(host="0.0.0.0", port=5000, debug=False)


if __name__ == "__main__":
    print("started")
    main()