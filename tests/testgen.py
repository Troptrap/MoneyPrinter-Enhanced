import ffmpeg
subs = '../subtitles/c7052451-259c-447d-bb34-d515fc103efc.srt'
vid = 'videoaudio.mp4'
aud = 'ttsoutput.mp3'
pos = 'center,bottom'
def generate_video(combined_video_path: str, tts_path: str, subtitles_path: str, subtitles_position: str) -> str:
    """
    This function creates the final video, with subtitles and audio.

    Args:
        combined_video_path (str): The path to the combined video.
        tts_path (str): The path to the text-to-speech audio.
        subtitles_path (str): The path to the subtitles.
        threads (int): The number of threads to use for the video processing.
        subtitles_position (str): The position of the subtitles.

    Returns:
        str: The path to the final video.
    """
  

    # Split the subtitles position into horizontal and vertical
    horizontal_subtitles_position, vertical_subtitles_position = subtitles_position.split(",")
    horizontal_subtitles_position, vertical_subtitles_position = subtitles_position.split(",")

    # Create a stream object from the combined video
    video_stream = ffmpeg.input(combined_video_path)

    # Create a stream object from the text-to-speech audio
    audio_stream = ffmpeg.input(tts_path)

    # Add the subtitles to the video stream using the subtitles filter
    # You can adjust the font, size, color, etc. of the subtitles using the options argument
    video_stream = video_stream.filter('subtitles', subtitles_path, **{'force_style': f'FontName=bold_font,FontSize=10,PrimaryColour=&H00FFFF,OutlineColour=&H000000,Outline=5,Alignment={horizontal_subtitles_position}{vertical_subtitles_position}'})

    # Merge the video and audio streams into one output stream
    output_stream = ffmpeg.output(video_stream, audio_stream,'../temp/output.mp4', vcodec='libx264')

    # Run the ffmpeg command and generate the output file
    # You can specify the number of threads to use with the threads argument
    ffmpeg.run(output_stream)

    return "output.mp4"
generate_video(vid,aud,subs,pos)