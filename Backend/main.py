import os
import requests
import json
import g4f
import re
from requests.exceptions import RequestException
from edgevoice import voices_list,msft_tts
import gpt
from video import save_video,generate_subtitles,combine_videos, generate_video
from utils import clean_dir,concat_audio,process_music
from tiktokvoice import tiktok_tts
from flask_cors import CORS
from termcolor import colored
from dotenv import load_dotenv
from youtube import upload_video
from apiclient.errors import HttpError
from flask import Flask, request, jsonify,Response,send_from_directory
import sox
import pydub
import asyncio
from nltk.tokenize import sent_tokenize
from werkzeug import serving
import time
def disable_endpoint_logs():
    """Disable logs for requests to specific endpoints."""

    disabled_endpoints = ('/check_messages','/songs/artists/')

    parent_log_request = serving.WSGIRequestHandler.log_request

    def log_request(self, *args, **kwargs):
        if not any(re.match(f"{de}$", self.path) for de in disabled_endpoints):
            parent_log_request(self, *args, **kwargs)

    serving.WSGIRequestHandler.log_request = log_request
# Load environment variables
load_dotenv("../.env")
disable_endpoint_logs()
# Set environment variables
SESSION_ID = os.getenv("TIKTOK_SESSION_ID")
openai_api_key = os.getenv('OPENAI_API_KEY')
#change_settings({"IMAGEMAGICK_BINARY": os.getenv("IMAGEMAGICK_BINARY")})
PEXELS_API_KEY = os.getenv('PEXELS_API_KEY')
PIXABAY_API_KEY = os.getenv('PIXABAY_API_KEY')
FLICKR_API_KEY = os.getenv('FLICKR_API_KEY')
UNSPLASH_API_KEY = os.getenv('UNSPLASH_ACCESS_KEY')
# Initialize Flask
app = Flask(__name__, static_folder='../Frontend')
CORS(app)


# Constants
HOST = "127.0.0.1"
PORT = 8080
AMOUNT_OF_STOCK_VIDEOS = 5
GENERATING = False

# Create an in-memory message queue which will be used to update frontend
message_queue = ["Waiting.."]

def message_put(message):
  message_queue.append(message)
def message_get():
  return message_queue[-1]
  

   
def generate_pexels_video_pairs(data):
    for video in data["videos"]:
        big_url = f"https://www.pexels.com/video/{video['id']}/download/"
        small_url = video['video_files'][0]['link']
        yield big_url, small_url
def generate_pixabay_video_pairs(data):
    for video in data["hits"]:
        big_url = video['videos']['large']['url']
        small_url = video['videos']['small']['url']
        yield big_url, small_url
        
@app.route('/g4f-models', methods=['GET'])
def g4f_models_list():
  g4fm = g4f.Model.__all__()
  return g4fm
@app.route('/check_messages')
def check_messages():
    # Check if there's a message in the queue (non-blocking)
    message = message_get()
    if message:
        return jsonify(message)
    else:
        return jsonify("Waiting..") # No content  
   
@app.route('/pexels/photo/search/<term>', methods=['GET'])  
def search_pexels_photos(term):
  
  url ='https://api.pexels.com/v1/search?query='+term
  headers= {
    'Authorization' : PEXELS_API_KEY
  }
  response = requests.get(url, headers=headers)
  data = response.json()
  urls = (photo["src"]["original"] for photo in data["photos"])
  return jsonify(list(urls))
@app.route('/pexels/photo/search/', methods=['GET'])  
def random_pexels_photos():
  
  url ='https://api.pexels.com/v1/curated'
  headers= {
    'Authorization' : PEXELS_API_KEY
  }
  response = requests.get(url, headers=headers)
  data = response.json()
  urls = (photo["src"]["original"] for photo in data["photos"])
  return jsonify(list(urls))
  
@app.route('/pexels/video/search/', methods=['GET'])  
def pexels_search_random():
  url = 'https://api.pexels.com/videos/popular'
  headers= {
    'Authorization' : PEXELS_API_KEY
  }
  response = requests.get(url, headers=headers)
  data = response.json()
  urls = dict(generate_pexels_video_pairs(data))
  return urls
@app.route('/pexels/video/search/<term>', methods=['GET'])  
def search_pexels_videos(term, orientation=None):
  url ='https://api.pexels.com/videos/search?query='+term
  headers= {
    'Authorization' : PEXELS_API_KEY
  }
  orientation = request.args.get('orientation')
  if orientation:
    url = url + f"&orientation={orientation}"
  response = requests.get(url, headers=headers)
  data = response.json()
  urls = dict(generate_pexels_video_pairs(data))
  return urls
  
@app.route('/pixabay/photo/search/<term>', methods=['GET'])  
def search_pixabay_photos(term):
  url = f'https://pixabay.com/api/?key={PIXABAY_API_KEY}&q={term}'
  response = requests.get(url)
  data = response.json()
  urls = (photo['largeImageURL'] for photo in data['hits'])
  return jsonify(list(urls))
@app.route('/pixabay/photo/search/', methods=['GET'])  
def random_pixabay_photos():
  url = f'https://pixabay.com/api/?key={PIXABAY_API_KEY}&per_page=15'
  response = requests.get(url)
  data = response.json()
  urls = (photo['largeImageURL'] for photo in data['hits'])
  return jsonify(list(urls))
  
@app.route('/pixabay/video/search/<term>', methods=['GET'])
def search_pixabay_videos(term):
  url = f'https://pixabay.com/api/videos/?key={PIXABAY_API_KEY}&q={term}'
  response = requests.get(url)
  data = response.json()
  urls = dict(generate_pixabay_video_pairs(data))
  return jsonify(urls)
@app.route('/pixabay/video/search/', methods=['GET'])
def random_pixabay_videos():
  url = f'https://pixabay.com/api/videos/?key={PIXABAY_API_KEY}&per_page=15'
  response = requests.get(url)
  data = response.json()
  urls = dict(generate_pixabay_video_pairs(data))
  return jsonify(urls)
  
@app.route('/unsplash/photo/search/', methods=['GET'])  
def random_unsplash_photos():
  url = f"https://api.unsplash.com/photos/random?count=15&client_id={UNSPLASH_API_KEY}"
  response = requests.get(url)
  data = response.json()
  urls = (photo['urls']['full'] for photo in data)
  return jsonify(list(urls))
@app.route('/unsplash/photo/search/<term>', methods=['GET'])  
def search_unsplash_photos(term):
  url = f"https://api.unsplash.com/search/photos?page=1&per_page=15&query={term}&client_id={UNSPLASH_API_KEY}"
  response = requests.get(url)
  data = response.json()
  urls = (photo['urls']['full'] for photo in data['results'])
  return jsonify(list(urls))
  
@app.route('/flickr/photo/search/<term>', methods=['GET'])  
def search_flickr_photos(term):
  term = term.replace(" ", ",")
  url = f"https://api.flickr.com/services/rest/?method=flickr.photos.search&api_key={FLICKR_API_KEY}&tags={term}&tag_mode=all&license=4,5,6,7&per_page=15&format=json&nojsoncallback=1"
  response = requests.get(url)
  data = response.json()
  urls = (f"https://live.staticflickr.com/{photo['server']}/{photo['id']}_{photo['secret']}_b.jpg" for photo in data['photos']['photo'])
  return jsonify(list(urls))
   
@app.route('/flickr/photo/search/', methods=['GET'])  
def random_flickr_photos():
  url = f"https://api.flickr.com/services/rest/?method=flickr.interestingness.getList&api_key={FLICKR_API_KEY}&per_page=15&format=json&nojsoncallback=1"
  response = requests.get(url)
  data = response.json()
  urls = (f"https://live.staticflickr.com/{photo['server']}/{photo['id']}_{photo['secret']}_b.jpg" for photo in data['photos']['photo'])
  return jsonify(list(urls))
   
      

@app.route('/songs/download/<songid>', methods=['GET'])
def grabSongs(songid):
    base_path = "../music"
    songfile = songid + '.mp3'

    fullpath = os.path.normpath(os.path.join(base_path, songfile))
    print(fullpath)
    if not fullpath.startswith(base_path):
        raise Exception("not allowed")

    if os.path.exists(fullpath):
        return jsonify({'downloaded': 'true', 'filename': fullpath})
    else:
        songurl = 'http://docs.google.com/uc?export=open&id=' + songid

        try:
            response = requests.get(songurl, stream=True)
            response.raise_for_status()  # Raise an exception for error status codes

            with open(fullpath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):  # Download in chunks
                    if chunk:  # Filter out keep-alive new chunks
                        f.write(chunk)

            return jsonify({'downloaded': 'true', 'filename': fullpath})

        except requests.exceptions.RequestException as err:
            print(f"Error downloading song: {err}")
            return jsonify({'downloaded': 'false'})
      

@app.route('/songs/artists', methods=['GET'])   
def get_all_artists():
    #Filter for artists names
    with open('audiolibrary.json') as f:
      songs = json.load(f)
    filtered_songs = {song['artist'] for song in songs.values()}
    return jsonify(list(filtered_songs))

@app.route('/songs/titles', methods=['GET'])   
def get_all_titles():
    #Filter for artists names
    with open('audiolibrary.json') as f:
      songs = json.load(f)
    filtered_songs = {song['title'] for song in songs.values()}
    return jsonify(list(filtered_songs))

@app.route('/songs/moods', methods=['GET'])   
def get_all_moods():
    #Filter for artists names
    with open('audiolibrary.json') as f:
      songs = json.load(f)
    filtered_songs = {song['mood'] for song in songs.values() if song['mood'] is not None}
    return jsonify(list(filtered_songs))

@app.route('/songs/genres', methods=['GET'])   
def get_all_genres():
    #Filter for artists names
    with open('audiolibrary.json') as f:
      songs = json.load(f)
    filtered_songs = {song['genre'] for song in songs.values()}
    return jsonify(list(filtered_songs))
    

@app.route('/songs/instruments', methods=['GET'])   
def get_all_instruments():
    with open('audiolibrary.json') as f:
      songs = json.load(f)
    filtered_songs = {
        instrument.lower() for song in songs.values()
        for instrument in song['instruments']
    }
    return jsonify(list(filtered_songs))
    
@app.route('/songs', methods=['GET'])
def get_all_tracks():
    # Get the parameters from the query string
    with open('audiolibrary.json') as f:
      songs = json.load(f)
    artist = request.args.get("artist")
    title = request.args.get("title")
    mood = request.args.get("mood")
    genre = request.args.get("genre")
    instrument = request.args.get("instrument")
  
    filtered_songs = {}
    for key, song in songs.items():
        if (artist is None or artist.lower() in song['artist'].lower()) and \
           (title is None or title.lower() in song['title'].lower()) and \
           (mood is None or song['mood'] is not None and song['mood'].lower() == mood.lower()) and \
           (genre is None or genre.lower() in song['genre'].lower()) and \
           (instrument is None or any(instrument.lower() in item.lower() for item in song['instruments'])):
            filtered_songs[key] = song
  
    return jsonify(filtered_songs)
    

# A route for getting songs by a specific artist
@app.route('/songs/artist/<artist>')
def get_songs_by_artist(artist):
    # Filter the songs by the artist name
    with open('audiolibrary.json') as f:
      songs = json.load(f)
    filtered_songs = (song for song in songs.values() if artist.lower() in song['artist'].lower())
    # Return the filtered songs as a JSON response
    return jsonify(list(filtered_songs))
   
# A route for getting songs by a specific artist
@app.route('/songs/title/<title>')
def get_songs_by_title(title):
    # Filter the songs by the title
    with open('audiolibrary.json') as f:
      songs = json.load(f)
    filtered_songs = (song for song in songs.values() if title.lower() in song['title'].lower())
    # Return the filtered songs as a JSON response
    return jsonify(list(filtered_songs))
    
    
# A route for getting songs by a specific mood
@app.route('/songs/mood/<mood>')
def get_songs_by_mood(mood):
    # Filter the songs by mood
    with open('audiolibrary.json') as f:
      songs = json.load(f)
    filtered_songs = (song for song in songs.values() if song['mood'] is not None and song['mood']== mood)
    # Return the filtered songs as a JSON response
    return jsonify(list(filtered_songs))
    
# A route for getting songs by a specific genre
@app.route('/songs/genre/<genre>')
def get_songs_by_genre(genre):
    # Filter the songs by the genre
    with open('audiolibrary.json') as f:
      songs = json.load(f)
    filtered_songs = (song for song in songs.values() if genre.lower() in  song['genre'].lower())
    # Return the filtered songs as a JSON response
    return jsonify(list(filtered_songs))
    
     

# A route for getting songs by a specific instrument
@app.route('/songs/instrument/<instrument>')
def get_songs_by_instrument(instrument):
    # Filter the songs by the instrument name
    with open('audiolibrary.json') as f:
      songs = json.load(f)
    filtered_songs = (song for song in songs.values()  for item in song['instruments'] if instrument.lower() in item.lower())
    
    # Return the filtered songs as a JSON response
    return jsonify(list(filtered_songs))
    
    


@app.route('/<path:path>')
def serve_page(path):
    return send_from_directory(app.static_folder, path)
    
@app.route('/music/<path>')
def serve_music(path):
    return send_from_directory('../music', path)
    
@app.route('/media/<path>')
def serve_media(path):
    return send_from_directory('../media', path)
    
@app.route('/grabmedia', methods=['POST'])
def grabmedia():
  data = request.get_json()
  url = data['url']
  with open('../media/list.json') as f:
    files = json.loads(f.read())
    if url not in files.keys():
    
      try:
        with requests.get(url) as r:
      
          fname = ''
          if "Content-Disposition" in r.headers.keys():
            fname = re.findall("filename=(.+)[;]", r.headers["Content-Disposition"])[0].replace(" ","").replace('"','').replace(':','')
            print(fname)
          else:
            fname = url.split("/")[-1]
          with open(f"../media/{fname}","wb") as f:
            f.write(r.content)
          with open('../media/list.json') as f:
            files = json.loads(f.read())
          files[url] = fname
          print(files)
          with open('../media/list.json','w') as f:
            json.dump(files,f)
      
      except RequestException as e:
        print(e)

    
  return jsonify({'downloaded':'true'})

  
@app.route('/')
def home():
    asyncio.run(voices_list())
    message_put("Loaded app")
    
    return send_from_directory(app.static_folder, 'index.html')


# Generation Endpoint
@app.route("/api/generate", methods=["POST"])
def generate():
   
        # Set global variable
        global GENERATING
        GENERATING = True

        # Clean
        clean_dir("../temp/")
        clean_dir("../subtitles/")
        message_put("Cleaned temporary files!")
        print(message_queue)

        # Parse JSON
        data = request.get_json()
        paragraph_number = int(data.get('paragraphNumber', 1))  # Default to 1 if not provided
        ai_model = data.get('aiModel')  # Get the AI model selected by the user
        g4f_model = data.get('g4fmodel')  # Get the AI model selected by the user
        
        subtitles_position = data.get('subtitlesPosition')  # Position of the subtitles in the video

        # Get 'useMusic' from the request data and default to False if not provided
        use_music = data.get('useMusic', False)

        # Get 'automateYoutubeUpload' from the request data and default to False if not provided
        automate_youtube_upload = data.get('automateYoutubeUpload', False)

        # Print little information about the video which is to be generated
        print(colored("[Video to be generated]", "blue"))
        print(colored("   Subject: " + data["videoSubject"], "blue"))
        print(colored("   AI Model: " + ai_model, "blue"))  # Print the AI model being used
        print(colored("   Custom Prompt: " + data["customPrompt"], "blue"))  # Print the AI model being used
        if not GENERATING:
            return jsonify(
                {
                    "status": "error",
                    "message": "Video generation was cancelled.",
                    "data": [],
                }
            )
        
        voice = data["voice"]
        ttsengine = data["ttsengine"]
        voice_prefix = voice[:2]
        vformat = data["format"]
        print(colored("Chosen format: "+vformat, "yellow"))


        if not voice:
            print(colored("[!] No voice was selected. Defaulting to \"en_us_001\"", "yellow"))
            voice = "en_us_001"
            voice_prefix = voice[:2]
        script = gpt.generate_script(data["videoSubject"], paragraph_number, ai_model, voice, data["customPrompt"], g4f_model)  # Pass the AI model to the script generation
        print(script)
        message_put("Script generated")
        time.sleep(2);
        message_put(f"Script text: {script}")
        # Generate search terms
        search_terms = gpt.get_search_terms(
            data["videoSubject"], paragraph_number, script, ai_model,g4f_model
        )
        message_put("Search terms generated")
        # Split script into sentences
        sentences = sent_tokenize(script)
        print(sentences)
        # Remove empty strings
        sentences = list(filter(lambda x: x != "", sentences))
        paths = []
        fcount = 1
          # Generate TTS for every sentence
        for sentence in sentences:
          if not GENERATING:
              return jsonify(
                      {
                          "status": "error",
                          "message": "Video generation was cancelled.",
                          "data": [],
                      }
                  )
          current_tts_path = os.path.abspath(f"../temp/{fcount}.mp3")
          if ttsengine=="tiktok":
            tiktok_tts(sentence, voice, filename=current_tts_path)
          elif ttsengine=="microsoft":
            try:
              asyncio.run(msft_tts(sentence,voice,current_tts_path))
            except Exception as e:
              raise e

          paths.append(current_tts_path)
          fcount += 1

          # Combine all TTS files 
        message_put("Voiceover generated")
        concat_audio(paths)

        tts_path = os.path.join("../Frontend", "ttsoutput.mp3")
        try:
          subtitles_path = generate_subtitles(audio_path=tts_path, sentences=sentences, audio_clips=paths, voice=voice_prefix)
        except Exception as e:
          print(colored(f"[-] Error generating subtitles: {e}", "red"))
          subtitles_path = None         
          
        message_put("Subtitles generated")
        if use_music:
          music_file=os.path.abspath(data['bgSong'])
          print("Processing music File: "+music_file)
          process_music(music_file)
          message_put("Audio generation complete")
        
        ttsoutput_duration = pydub.AudioSegment.from_mp3(tts_path).duration_seconds

        video_urls = []

        for search_term in search_terms:
          if not GENERATING:
            return jsonify(
                    {
                        "status": "error",
                        "message": "Video generation was cancelled",
                        "data": [],
                    }
                )
          
          found_urls = search_pexels_videos(search_term)
            # Check for duplicates
          for url in found_urls:
            if url not in video_urls:
              video_urls.append(url)
              print(url)
              break

        # Check if video_urls is empty
        if not video_urls:
            print(colored("[-] No videos found to download.", "red"))
            return jsonify(
                {
                    "status": "error",
                    "message": "No videos found to download.",
                    "data": [],
                }
            )
        # Define video_paths
        video_paths = []

        # Let user know
        print(colored(f"[+] Downloading {len(video_urls)} videos...", "blue"))
        message_put("Downloading videos..")
        # Save the videos
        for count,video_url in enumerate(video_urls, start=1):
            if not GENERATING:
                return jsonify(
                    {
                        "status": "error",
                        "message": "Video generation was cancelled.",
                        "data": [],
                    }
                )
            try:
                saved_video_path = save_video(video_url, count)
                video_paths.append(saved_video_path)
            except Exception:
                print(colored(f"[-] Could not download video: {video_url}", "red"))

        # Let user know
        print(colored("[+] Videos downloaded!", "green"))
        message_put("Videos downloaded")
        # Let user know
        print(colored("[+] Script generated!\n", "green"))


        
        combined = combine_videos(video_paths, ttsoutput_duration,vformat)
        message_put("Clips combined")
        # Put everything together
        try:
            final_video_path = generate_video(combined, tts_path, subtitles_path, subtitles_position)
        except Exception as e:
            print(colored(f"[-] Error generating final video: {e}", "red"))
            final_video_path = None

        message_put("Video generation complete")
        # Define metadata for the video, we will display this to the user, and use it for the YouTube upload
        title, description, keywords = gpt.generate_metadata(data["videoSubject"], script, ai_model, g4f_model)

        print(colored("[-] Metadata for YouTube upload:", "blue"))
        print(colored("   Title: ", "blue"))
        print(colored(f"   {title}", "blue"))
        print(colored("   Description: ", "blue"))
        print(colored(f"   {description}", "blue"))
        print(colored("   Keywords: ", "blue"))
        print(colored(f"  {', '.join(keywords)}", "blue"))

        if automate_youtube_upload:
            # Start Youtube Uploader
            # Check if the CLIENT_SECRETS_FILE exists
            client_secrets_file = os.path.abspath("./client_secret.json")
            SKIP_YT_UPLOAD = False
            if not os.path.exists(client_secrets_file):
                SKIP_YT_UPLOAD = True
                print(colored("[-] Client secrets file missing. YouTube upload will be skipped.", "yellow"))
                print(colored("[-] Please download the client_secret.json from Google Cloud Platform and store this inside the /Backend directory.", "red"))

            # Only proceed with YouTube upload if the toggle is True  and client_secret.json exists.
            if not SKIP_YT_UPLOAD:
                # Choose the appropriate category ID for your videos
                video_category_id = "28"  # Science & Technology
                privacyStatus = "private"  # "public", "private", "unlisted"
                video_metadata = {
                    'video_path': os.path.abspath(f"../temp/{final_video_path}"),
                    'title': title,
                    'description': description,
                    'category': video_category_id,
                    'keywords': ",".join(keywords),
                    'privacyStatus': privacyStatus,
                }

                # Upload the video to YouTube
                try:
                    # Unpack the video_metadata dictionary into individual arguments
                    video_response = upload_video(
                        video_path=video_metadata['video_path'],
                        title=video_metadata['title'],
                        description=video_metadata['description'],
                        category=video_metadata['category'],
                        keywords=video_metadata['keywords'],
                        privacy_status=video_metadata['privacyStatus']
                    )
                    print(f"Uploaded video ID: {video_response.get('id')}")
                    message_put(f"Uploaded video ID: {video_response.get('id')}")
                except HttpError as e:
                    print(f"An HTTP error {e.resp.status} occurred:\n{e.content}")


        # Let user know
        print(colored(f"[+] Video generated: {final_video_path}!", "green"))

        # Stop FFMPEG processes
        if os.name == "nt":
            # Windows
            os.system("taskkill /f /im ffmpeg.exe")
        else:
            # Other OS
            os.system("pkill -f ffmpeg")

        GENERATING = False

        # Return JSON
        return jsonify(
            {
                "status": "success",
                "message": "Video generated! See MoneyPrinter/Frontend/output.mp4 for result.",
                "data": final_video_path,
            })



@app.route("/api/cancel", methods=["POST"])
def cancel():
    print(colored("[!] Received cancellation request...", "yellow"))

    global GENERATING
    GENERATING = False

    return jsonify({"status": "success", "message": "Cancelled video generation."})


if __name__ == "__main__":

    # Run Flask App
    app.run(debug=True, host=HOST, port=PORT)
