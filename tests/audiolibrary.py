import requests
import json
audio_lib_url = "https://raw.githubusercontent.com/operator-name/youtube-audio-library-download-all/master/music/music-1000.json"
audio_down_url = "https://thibaultjanbeyer.github.io/YouTube-Free-Audio-Library-API/api.json"
infor= requests.get(audio_lib_url)
infodata = infor.json()
downr = requests.get(audio_down_url)
downdata = downr.json()["all"]
audiolibrary = {}
for song in infodata['tracks']:
  filename = song["title"].replace(" ","_")+".mp3"
  for i,d in enumerate(downdata):
    if d["name"] == filename:
      songdata = {}
      songdata["artist"] = song["artist"]
      songdata["title"] = song["title"]
      songdata["genre"] = song["genre"]
      songdata["mood"] = song["mood"]
      songdata["instruments"] = song["instruments"]
      songdata["url"] = "http://docs.google.com/uc?export=download&id="+d["id"]
      audiolibrary[i] = songdata
with open("audiolibrary.json", "w") as f:
  json.dump(audiolibrary,f)