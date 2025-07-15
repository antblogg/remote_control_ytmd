 
 function convert_song_length(song_length){
  
  minutes = Math.floor(song_length/60).toString().slice(0,1)  
  seconds = (song_length % 60).toString().slice(0,2)
  if (seconds[1] == "."){
    seconds = seconds[0]
  }
  if (seconds < 10){
    seconds = "0" + seconds
  }
  
  return minutes +":" + seconds
}
    let real_progress =0
    let song_duration = 0
    let displayed_progress = 0

 
 setInterval(() => {
    fetch("/songdata")
      .then(res => res.json())
      .then(data => {
        
        var player = data.player
        var current_song = data.video

        song_title = current_song.title
        song_artist = current_song.author
        thumbnails = current_song.thumbnails
        thumbnail = thumbnails[thumbnails.length - 1]
        album_cover = thumbnail.url
        current_progress = player.videoProgress
        song_length_seconds = current_song.durationSeconds
        
        real_progress = parseFloat(current_progress); 
        song_duration = parseFloat(song_length_seconds);
    
        displayed_progress = real_progress*10; // sync visual to real
        
        current_progress_text = convert_song_length(current_progress)
        song_length_text = convert_song_length(song_length_seconds)

        document.getElementById("song_title").textContent = song_title
        document.getElementById("song_artist").textContent = song_artist
        document.getElementById("album_cover").src = album_cover
        document.getElementById("progress_bar_current_duration").textContent = current_progress_text
        document.getElementById("progress_bar_song_length").textContent = song_length_text
        
        document.getElementById("progress_bar").max = song_length_seconds*10
        document.getElementById("progress_bar").value = current_progress*10

        
      
      
      })
     .catch(err => console.error("Fetch error:", err));
  }, 1000); 



  // 2. Smooth update every 100ms
setInterval(() => {
  // Drift correction — don't let it outrun reality by more than 1s
 if (displayed_progress < real_progress + 1 && displayed_progress < song_duration) {

    displayed_progress +=0.1;
    console.log("progress" + displayed_progress)

    document.getElementById("progress_bar").value = displayed_progress;

  }
}, 10);