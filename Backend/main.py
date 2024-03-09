import os
import subprocess
from edgevoice import voices_list,msft_tts
from gpt import *
from video import *
from utils import *
from search import *
from uuid import uuid4
from tiktokvoice import *
from flask_cors import CORS
from termcolor import colored
from dotenv import load_dotenv
from youtube import upload_video
from apiclient.errors import HttpError
from flask import Flask, request, jsonify,send_from_directory
import ffmpeg
import sox
import asyncio
import nltk
from nltk.tokenize import sent_tokenize
nltk.download('punkt')

# Load environment variables
load_dotenv("../.env")

# Set environment variables
SESSION_ID = os.getenv("TIKTOK_SESSION_ID")
openai_api_key = os.getenv('OPENAI_API_KEY')
#change_settings({"IMAGEMAGICK_BINARY": os.getenv("IMAGEMAGICK_BINARY")})

# Initialize Flask
app = Flask(__name__, static_folder='../Frontend')
CORS(app)


# Constants
HOST = "127.0.0.1"
PORT = 8080
AMOUNT_OF_STOCK_VIDEOS = 5
GENERATING = False


with open('audiolibrary.json', 'r') as f:
    songs = json.load(f)
    
    
def list_to_dict(lst):

   res_dict = {}

   for i in range(0, len(lst)):

       res_dict[i] = lst[i]

   return res_dict
   
@app.route('/g4f-models', methods=['GET'])
def g4f_models_list():
  g4fm = g4f.Model.__all__()
  return g4fm
   
   
@app.route('/pexels/photo/search/<term>', methods=['GET'])  
def search_pexels_photos(term):
  // TODO
@app.route('/pexels/video/search/<term>', methods=['GET'])  
def search_pexels_videos(term):
  // TODO
@app.route('/pixabay/photo/search/<term>', methods=['GET'])  
def search_pixabay_photos(term):
  // TODO
@app.route('/pixabay/video/search/<term>', methods=['GET'])  
def search_pixabay_videos(term):
  // TODO
@app.route('/unsplash/photo/search/<term>', methods=['GET'])  
def search_unsplash_photos(term):
  // TODO
@app.route('/flickr/photo/search/<term>', methods=['GET'])  
def search_flickr_photos(term):
  // TODO
   
   
@app.route('/songs/download/<songid>', methods=['GET'])
def grabSong(songid):
  base_path = "../music"
  songfile = songid+'.mp3'
  
  fullpath = os.path.normpath(os.path.join(base_path, songfile))
  print(fullpath)
  if not fullpath.startswith(base_path):
        raise Exception("not allowed")
  if os.path.exists(fullpath):
    return jsonify({'downloaded':'true', 'filename':fullpath})
  else:
    songurl = 'http://docs.google.com/uc?export=open&id='+songid
    
    gdwn = subprocess.run(['wget', songurl, '-O', fullpath])
    
    if gdwn.returncode == 0:
      return jsonify({'downloaded':'true', 'filename':fullpath})
    else:
      return jsonify({'downloaded':'false'})

@app.route('/songs/artists', methods=['GET'])   
def get_all_artists():
    #Filter for artists names
    filtered_songs = [] 
    for song in songs.values():
      artist = song['artist']
      if artist not in filtered_songs:
        filtered_songs.append(artist)
    return jsonify(filtered_songs)

@app.route('/songs/titles', methods=['GET'])   
def get_all_titles():
    #Filter for artists names
    filtered_songs = [] 
    for song in songs.values():
      title = song['title']
      if title not in filtered_songs:
        filtered_songs.append(title)
    return jsonify(filtered_songs)

@app.route('/songs/moods', methods=['GET'])   
def get_all_moods():
    #Filter for artists names
    filtered_songs = [] 
    for song in songs.values():
      mood = song['mood']
      if mood is not None:
        mood = song['mood'].lower()
        if mood not in filtered_songs:
          filtered_songs.append(mood)
      else:
        pass 
    return jsonify(filtered_songs)

@app.route('/songs/genres', methods=['GET'])   
def get_all_genres():
    #Filter for artists names
    filtered_songs = [] 
    for song in songs.values():
      genre = song['genre']
      if genre is not None:
        genre = song['genre'].lower()
        if genre not in filtered_songs:
          filtered_songs.append(genre)
      else:
        pass 
    return jsonify(filtered_songs)
    

@app.route('/songs/instruments', methods=['GET'])   
def get_all_instruments():
    filtered_songs = [] 
    for song in songs.values():
      instrumentlist = song['instruments']
      for instrument in instrumentlist:
        instrument = instrument.lower()
        if instrument not in filtered_songs:
          filtered_songs.append(instrument)
 
    return jsonify(filtered_songs)
    
@app.route('/songs', methods=['GET'])
def get_all_tracks():
  
  

    # Get the parameters from the query string
    artist = request.args.get("artist")
    title = request.args.get("title")
    mood = request.args.get("mood")
    genre = request.args.get("genre")
    instrument = request.args.get("instrument")
    filtered_songs = songs
    if artist is not None:
      filtered_songs = list_to_dict([song for song in filtered_songs.values() if artist.lower() in song['artist'].lower()])
    if title is not None:
          filtered_songs = list_to_dict([song for song in filtered_songs.values() if title.lower() in song['title'].lower()])
    if mood is not None:
      filtered_songs = list_to_dict([song for song in filtered_songs.values() if song['mood'] is not None and song['mood'].lower() == mood.lower()])
    if genre is not None:
      filtered_songs = list_to_dict([song for song in filtered_songs.values() if genre.lower() in  song['genre'].lower()])
    if instrument is not None:
      filtered_songs = list_to_dict([song for song in filtered_songs.values() for item in song['instruments'] if instrument.lower() in item.lower()])
      
  
  
    return jsonify(filtered_songs)
    

# A route for getting songs by a specific artist
@app.route('/songs/artist/<artist>')
def get_songs_by_artist(artist):
    # Filter the songs by the artist name
    filtered_songs = [song for song in songs.values() if artist.lower() in song['artist'].lower()]
    # Return the filtered songs as a JSON response
    return jsonify(filtered_songs)
   
# A route for getting songs by a specific artist
@app.route('/songs/title/<title>')
def get_songs_by_title(title):
    # Filter the songs by the title
    filtered_songs = [song for song in songs.values() if title.lower() in song['title'].lower()]
    # Return the filtered songs as a JSON response
    return jsonify(filtered_songs)
    
    
# A route for getting songs by a specific mood
@app.route('/songs/mood/<mood>')
def get_songs_by_mood(mood):
    # Filter the songs by mood
    filtered_songs = [song for song in songs.values() if song['mood'] is not None and song['mood']== mood]
    # Return the filtered songs as a JSON response
    return jsonify(filtered_songs)
    
# A route for getting songs by a specific genre
@app.route('/songs/genre/<genre>')
def get_songs_by_genre(genre):
    # Filter the songs by the genre
    filtered_songs = [song for song in songs.values() if genre.lower() in  song['genre'].lower()]
    # Return the filtered songs as a JSON response
    return jsonify(filtered_songs)
    
     

# A route for getting songs by a specific instrument
@app.route('/songs/instrument/<instrument>')
def get_songs_by_instrument(instrument):
    # Filter the songs by the instrument name
    filtered_songs = [song for song in songs.values()  for item in song['instruments'] if instrument.lower() in item.lower()]
    
    # Return the filtered songs as a JSON response
    return jsonify(filtered_songs)
    
    


@app.route('/<path:path>')
def serve_page(path):
    return send_from_directory(app.static_folder, path)
@app.route('/music/<path>')
def serve_music(path):
    return send_from_directory('../music', path)

@app.route('/')
def home():
    asyncio.run(voices_list())
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
        script = generate_script(data["videoSubject"], paragraph_number, ai_model, voice, data["customPrompt"], g4f_model)  # Pass the AI model to the script generation
        print(script)
        # Generate search terms
        search_terms = get_search_terms(
            data["videoSubject"], AMOUNT_OF_STOCK_VIDEOS, script, ai_model,g4f_model
        )

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
            tts(sentence, voice, filename=current_tts_path)
          elif ttsengine=="microsoft":
            try:
              asyncio.run(msft_tts(sentence,voice,current_tts_path))
            except (Exception, e):
              raise e

          paths.append(current_tts_path)
          fcount += 1

          # Combine all TTS files using sox
        final_audio = concat_audio(paths)

        tts_path = os.path.abspath('../temp/ttsoutput.mp3')
        try:
          subtitles_path = generate_subtitles(audio_path=tts_path, sentences=sentences, audio_clips=paths, voice=voice_prefix)
        except Exception as e:
          print(colored(f"[-] Error generating subtitles: {e}", "red"))
          subtitles_path = None         
          
        # Concatenate videos
        if use_music:
          music_file=os.path.abspath(data['bgSong'])
          print("Processing music File: "+music_file)
          process_music(music_file)
        ttsoutput_duration = sox.file_info.duration(tts_path)

        video_urls = []
        
        # Defines how many results it should query and search through
        it = 15
        
        # Defines the minimum duration of each clip
        min_dur = 10

        for search_term in search_terms:
          if not GENERATING:
            return jsonify(
                    {
                        "status": "error",
                        "message": "Video generation was cancelled",
                        "data": [],
                    }
                )
          found_urls = search_for_stock_videos(
                search_term, os.getenv("PEXELS_API_KEY"), it, min_dur
            )
            # Check for duplicates
          for url in found_urls:
            if url not in video_urls:
              video_urls.append(url)
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

        # Let user know
        print(colored("[+] Script generated!\n", "green"))


        
        combined_video_path = combine_videos(video_paths, ttsoutput_duration, 10,vformat)
        # Put everything together
        try:
            final_video_path = generate_video('../temp/videoaudio.mp4', tts_path, subtitles_path, subtitles_position)
        except Exception as e:
            print(colored(f"[-] Error generating final video: {e}", "red"))
            final_video_path = None

        # Define metadata for the video, we will display this to the user, and use it for the YouTube upload
        title, description, keywords = generate_metadata(data["videoSubject"], script, ai_model, g4f_model)

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
            }
        )
  #  except Exception as err:
      #  print(colored(f"[-] Error: {str(err)}", "red"))
     #   return jsonify(
      #      {
       #         "status": "error",
        #        "message": f"Could not retrieve stock videos: {str(err)}",
         #       "data": [],
          #  }
        #)


@app.route("/api/cancel", methods=["POST"])
def cancel():
    print(colored("[!] Received cancellation request...", "yellow"))

    global GENERATING
    GENERATING = False

    return jsonify({"status": "success", "message": "Cancelled video generation."})


if __name__ == "__main__":

    # Run Flask App
    app.run(debug=True, host=HOST, port=PORT)
