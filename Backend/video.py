import os
import uuid

import requests
import srt_equalizer
import assemblyai as aai

from typing import List
from termcolor import colored
from dotenv import load_dotenv
from datetime import timedelta
import ffmpeg
import sox

load_dotenv("../.env")

ASSEMBLY_AI_API_KEY = os.getenv("ASSEMBLY_AI_API_KEY")


def save_video(video_url: str, count: int, directory: str = "../temp"):
    """Saves a video from a given URL and returns the path to the video.
    
    Saves a video from a given URL and returns the path to the video.

    Args:
        video_url (str): The URL of the video to save.
        directory (str): The path of the temporary directory to save the video to

    Returns:
        str: The path to the saved video.
    """
    video_id = str(count)
    video_path = f"{directory}/{video_id}.mp4"
    with open(video_path, "wb") as f:
        f.write(requests.get(video_url).content)

    return video_path


def __generate_subtitles_assemblyai(audio_path: str, voice: str) -> str:
    """Generates subtitles from a given audio file and returns the path to the subtitles.

    Args:
        audio_path (str): The path to the audio file to generate subtitles from.

    Returns:
        str: The generated subtitles
    """
    language_mapping = {
        "br": "pt",
        "id": "en",  # AssemblyAI doesn't have Indonesian
        "jp": "ja",
        "kr": "ko",
    }

    if voice in language_mapping:
        lang_code = language_mapping[voice]
    else:
        lang_code = voice

    aai.settings.api_key = ASSEMBLY_AI_API_KEY
    config = aai.TranscriptionConfig(language_code=lang_code)
    transcriber = aai.Transcriber(config=config)
    transcript = transcriber.transcribe(audio_path)
    subtitles = transcript.export_subtitles_srt()

    return subtitles


def __generate_subtitles_locally(
    sentences: List[str], audio_files: List[str]
) -> str:
    """Generates subtitles from a given audio file and returns the path to the subtitles.

    Args:
        sentences (List[str]): all the sentences said out loud in the audio files
        audio_files (List[str]): all the paths to the individual audio files which will make up the final audio track
    Returns:
        str: The generated subtitles
    """

    def convert_to_srt_time_format(total_seconds):
        # Convert total seconds to the SRT time format: HH:MM:SS,mmm
        if total_seconds == 0:
            return "0:00:00,0"
        return (
            str(timedelta(seconds=total_seconds)).rstrip("0").replace(".", ",")
        )

        return str(timedelta(seconds=total_seconds)).rstrip("0").replace(".", ",")

    start_time = 0
    subtitles = []

    for i, (sentence, audio_file) in enumerate(
        zip(sentences, audio_files), start=1
    ):
        # Create a stream object from the audio file
        ffmpeg.input(audio_file)
        # Get the duration of the audio stream in seconds
        duration = sox.file_info.duration(audio_file)
        end_time = start_time + duration

        # Format: subtitle index, start time --> end time, sentence
        subtitle_entry = f"{i}\n{convert_to_srt_time_format(start_time)} --> {convert_to_srt_time_format(end_time)}\n{sentence}\n"
        subtitles.append(subtitle_entry)
        start_time += duration  # Update start time for the next subtitle

    return "\n".join(subtitles)


def generate_subtitles(
    audio_path: str, sentences: List[str], audio_clips: List[str], voice: str
) -> str:

    """Generates subtitles from a given audio file and returns the path to the subtitles.

    Args:
        audio_path (str): The path to the audio file to generate subtitles from.
        sentences (List[str]): all the sentences said out loud in the audio clips
        audio_clips (List[AudioFileClip]): all the individual audio clips which will make up the final audio track

    Returns:
        str: The path to the generated subtitles.
    """

    def equalize_subtitles(srt_path: str, max_chars: int = 10) -> None:
        # Equalize subtitles
        srt_equalizer.equalize_srt_file(srt_path, srt_path, max_chars)

    # Save subtitles
    subtitles_path = f"../subtitles/{uuid.uuid4()}.srt"

    if ASSEMBLY_AI_API_KEY is not None and ASSEMBLY_AI_API_KEY != "":
        print(colored("[+] Creating subtitles using AssemblyAI", "blue"))
        subtitles = __generate_subtitles_assemblyai(audio_path, voice)
    else:
        print(colored("[+] Creating subtitles locally", "blue"))
        subtitles = __generate_subtitles_locally(sentences, audio_clips)
        # print(colored("[-] Local subtitle generation has been disabled for the time being.", "red"))
        # print(colored("[-] Exiting.", "red"))
        # sys.exit(1)

    with open(subtitles_path, "w") as file:
        file.write(subtitles)

    # Equalize subtitles
    equalize_subtitles(subtitles_path)

    print(colored("[+] Subtitles generated.", "green"))

    return subtitles_path


def resize_to_portrait(video_path, input_duration, idx):
    probe = ffmpeg.probe(video_path)
    video_stream = next(
        s for s in probe["streams"] if s["codec_type"] == "video"
    )

    width = video_stream["width"]
    height = video_stream["height"]

    # Calculate aspect ratio
    aspect_ratio = width / height

    # Determine cropping and resizing parameters
    if aspect_ratio < 0.5625:  # Landscape video (wider than tall)
        new_width = width

        new_height = round(width / 0.5625)  # Maintain aspect ratio for landscape
    else:  # Portrait video (taller than wide)
        new_height = height
        new_width = round(0.5625 * height)  # Maintain aspect ratio for portrait

    # Ensure new dimensions are within valid ranges to avoid errors
    new_width = max(new_width, 1)  # Minimum width of 1 pixel
    new_height = max(new_height, 1)  # Minimum height of 1 pixel

    # Calculate x and y coordinates for centered cropping
    x = (width - new_width) // 2
    y = (height - new_height) // 2

    (
        ffmpeg.input(video_path, ss=0, t=input_duration)
        .video
        # Remove audio
        .filter(
            "crop", w=new_width, h=new_height, x=x, y=y
        )  # Crop to the same aspect ratio
        .filter("scale", 1080, 1920)  # Resize to the same resolution
        .filter("fps", fps=30)  # Set fps to 30
        .output(
            "../temp/" + str(idx) + ".mpg",
            vcodec="libx264",
            preset="ultrafast",
            format="mp4",
        )
        .run()
    )


def resize_to_landscape(video_path, input_duration, idx):
    probe = ffmpeg.probe(video_path)
    video_stream = next(
        s for s in probe["streams"] if s["codec_type"] == "video"
    )
    video_stream = next(s for s in probe["streams"] if s["codec_type"] == "video")
    width = video_stream["width"]
    height = video_stream["height"]

    # Calculate aspect ratio
    aspect_ratio = width / height

    # Determine cropping and resizing parameters
    if aspect_ratio > 1.7777:  # If the video is wider than 16:9
        new_height = height
        new_width = round(
            height * 1.7777
        )  # Adjust width to maintain 16:9 aspect ratio
        new_width = round(height * 1.7777)  # Adjust width to maintain 16:9 aspect ratio
    else:  # If the video is narrower than 16:9
        new_width = width
        new_height = round(
            width / 1.7777
        )  # Adjust height to maintain 16:9 aspect ratio

    # Ensure new dimensions are within valid ranges to avoid errors
    new_width = max(new_width, 1)  # Minimum width of 1 pixel
    new_height = max(new_height, 1)  # Minimum height of 1 pixel

    # Calculate x and y coordinates for centered cropping
    x = (width - new_width) // 2
    y = (height - new_height) // 2

    (
        ffmpeg.input(video_path, ss=0, t=input_duration)
        .video
        # Remove audio
        .filter(
            "crop", w=new_width, h=new_height, x=x, y=y
        )  # Crop to the same aspect ratio
        .filter("scale", 1920, 1080)  # Resize to 1920x1080 for YouTube
        .filter("fps", fps=30)  # Set fps to 30
        .output(
            "../temp/" + str(idx) + ".mpg",
            vcodec="libx264",
            preset="ultrafast",
            format="mp4",
        )  # Output format changed to mp4
        .run()
    )


def loop_video(input_file, req_dur):
  """
  Loops an input video and creates an output of specified duration with the same filename.

  Args:
    input_file: Path to the input video file (e.g., "input.mp4").
    req_dur: The requested duration of the output video in seconds (float).
  """
  
  # Generate a unique temporary filename within the same directory
  base, ext = os.path.splitext(input_file)
  temp_filename = f"{base}_temp.{ext}"
  
  stream = ffmpeg.input(input_file)
  output = ffmpeg.output(stream, temp_filename, loop=-1, t=req_dur, c="copy")
  ffmpeg.run(output)
  
  # Overwrite the original file with the temporary file
  os.replace(temp_filename, input_file)



def combine_videos(
    video_paths: List[str],
    max_duration: int,
    vformat: str,
) -> str:
    
    """
    Combines a list of videos into one video and returns the path to the combined video.

    Args:
        video_paths (List): A list of paths to the videos to combine.
        max_duration (int): The maximum duration of the combined video.
        max_clip_duration (int): The maximum duration of each clip.
        threads (int): The number of threads to use for the video processing.

    Returns:
        str: The path to the combined video.
    """

    print(video_paths)

    video_id = "videoseq"
    combined_video_path = f"../temp/{video_id}.mp4"

    # Required duration of each clip
    req_dur = max_duration / len(video_paths)

    print(colored("[+] Combining videos...", "blue"))
    print(
        colored(
            f"[+] Each clip will be maximum {req_dur} seconds long.", "blue"
        )
    )
    print(colored(f"[+] Each clip will be maximum {req_dur} seconds long.", "blue"))


    tot_dur = 0

    idx = 1

    while tot_dur < max_duration:
        for video_path in video_paths:
            if tot_dur > max_duration:
                break

            print(colored("[+] Working on part " + str(idx), "blue"))
            # Get the duration of the input stream
            iprobe = ffmpeg.probe(video_path)
            input_duration = float(iprobe["format"]["duration"])
            if input_duration<req_dur:
              loop_video(video_path, req_dur)
            input_duration = float(iprobe["format"]["duration"])
            # Check if clip is longer than the remaining audio
            if (max_duration - tot_dur) < input_duration:
                input_duration = max_duration - tot_dur
            if req_dur < input_duration:
                input_duration = req_dur
            if input_duration == 0:
                break

            print("This clip duration after: " + str(input_duration))

            # Apply filters to single clips
            if vformat == "landscape":
                resize_to_landscape(video_path, input_duration, idx)
            elif vformat == "portrait":
                resize_to_portrait(video_path, input_duration, idx)
            else:
                print(colored("Something is wrong with video mode..", "red"))
                break
            # Increment duration until it meets the audio duration from TTS
            tot_dur += input_duration
            idx += 1

            # Write the clips to the main video
    print(colored("[+] Merging " + str(idx) + " videos..", "blue"))

    input_paths = []
    for f in os.listdir("../temp"):
        if f.endswith(".mpg"):
            input_paths.append("../temp/" + f)
    open("../temp/concat.txt", "w").writelines(
        [("file %s\n" % input_path) for input_path in input_paths]
    )
    ffmpeg.input("../temp/concat.txt", format="concat", safe=0).output(
        combined_video_path, c="copy", an=None
    ).run()

    print(colored("[+] Successfully merged", "green"))

    return combined_video_path

    # Concatenate videos


def generate_video(
    combined_video_path: str,
    tts_path: str,
    subtitles_path: str,
    subtitles_position: str,
) -> str:

    """This function creates the final video, with subtitles and audio.


    
    Args:
        combined_video_path (str): The path to the combined video.
        tts_path (str): The path to the text-to-speech audio.
        subtitles_path (str): The path to the subtitles.
        threads (int): The number of threads to use for the video processing.
        subtitles_position (str): The position of the subtitles.

    Returns:
        str: The path to the final video.
    """

    # Create a stream object from the combined video
    video_stream = ffmpeg.input(combined_video_path)

    # Create a stream object from the text-to-speech audio
    duration = sox.file_info.duration(tts_path)
    audio_stream = ffmpeg.input(tts_path, t=duration)

    # Add the subtitles to the video stream using the subtitles filter
    # You can adjust the font, size, color, etc. of the subtitles using the options argument
    video_stream = video_stream.filter(
        "subtitles",
        subtitles_path,
        **{
            "force_style": f"FontName=bold_font,FontSize=18,PrimaryColour=&H00FFFF,OutlineColour=&H000000,Outline=1,Alignment={subtitles_position}"
        },
    )

    # Merge the video and audio streams into one output stream
    output_stream = ffmpeg.output(
        video_stream,
        audio_stream,
        "../Frontend/output.mp4",
        vcodec="libx264",
        preset="ultrafast",
    )

    # Run the ffmpeg command and generate the output file
    ffmpeg.run(output_stream, overwrite_output=True)

    return "../Frontend/output.mp4"
