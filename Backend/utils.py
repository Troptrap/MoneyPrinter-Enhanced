import os
import logging
import sox
from typing import List
from termcolor import colored
import pydub
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clean_dir(path: str) -> None:
    """Removes every file in a directory.

    Args:
        path (str): Path to directory.

    Returns:
        None
    """
    try:
        if not os.path.exists(path):
            os.mkdir(path)
            logger.info(f"Created directory: {path}")

        for file in os.listdir(path):
            file_path = os.path.join(path, file)
            os.remove(file_path)
            logger.info(f"Removed file: {file_path}")

        logger.info(colored(f"Cleaned {path} directory", "green"))
    except Exception as e:
        logger.error(
            f"Error occurred while cleaning directory {path}: {str(e)}"
        )



""" def concat_audio(paths: List[str]) -> str:
    cbn = sox.Combiner()
    cbn.build(paths, os.path.abspath("../Frontend/ttsoutput.mp3"), "concatenate")
"""

""" def process_musics(input_file):
    # Create a transformer
    tfm = sox.Transformer()
    target_rate = sox.file_info.sample_rate(
        os.path.abspath("../Frontend/ttsoutput.mp3")
    )
    # Set the volume to 20% of the original
    tfm.rate(samplerate=target_rate)
    tfm.norm(db_level=-8)
    tfm.vol(0.15)
    # Apply the transformation to the input file and create the output file

    lowvol_file = os.path.abspath("../temp/lowvolmusic.mp3")
    tfm.build(input_file, lowvol_file)

    # Print a success message
    print(
        f"The volume of {input_file} has been reduced to 15% and saved as {lowvol_file}."
    )
    duration_audio1 = sox.file_info.duration(
        os.path.abspath("../Frontend/ttsoutput.mp3")
    )
    print("TTS duration: " + str(duration_audio1))
    cmb = sox.Combiner()

    duration_audio2 = sox.file_info.duration(lowvol_file)
    print("Music duration: " + str(duration_audio2))
    if duration_audio2 < duration_audio1:
        repeat_times = int(duration_audio1 // duration_audio2) + 1
        print("Looping music..")
        tfm.repeat(count=repeat_times)
        tfm.build(lowvol_file, "audio2_repeated.mp3")
        audio2_path = "audio2_repeated.mp3"
    else:
        audio2_path = "audio2.mp3"

    if duration_audio2 > duration_audio1:
        print("Trimming music..")
        tfm.trim(0, duration_audio1)
        tfm.build(lowvol_file, "audio2_trimmed.mp3")
        audio2_path = "audio2_trimmed.mp3"

    # Combine audio1.mp3 and the modified audio2.mp3
    print("Trying to mix voice and music..")
    cmb.build(
        [os.path.abspath("../Frontend/ttsoutput.mp3"), audio2_path],
        os.path.abspath("../temp/mixed_audio.mp3"),
        "mix",
    )
    duration_mixed = sox.file_info.duration(
        os.path.abspath("../temp/mixed_audio.mp3")
    )
    print("Mixed file duration: " + str(duration_mixed))
    # Remove the temporary file if it was created
    print("Succesfull mixing! Cleaning ..")
    os.remove("../Frontend/ttsoutput.mp3")
    os.rename("../temp/mixed_audio.mp3","../Frontend/ttsoutput.mp3")
    if "repeated" in audio2_path or "trimmed" in audio2_path:
        os.remove(audio2_path)

"""


def concat_audio(paths: List[str]) -> str:
    combined_audio = pydub.AudioSegment.empty()  # Create an empty AudioSegment to hold the combined audio

    for path in paths:
        audio_file = pydub.AudioSegment.from_file(path)  # Load each audio file into an AudioSegment
        combined_audio += audio_file  # Concatenate the audio files sequentially

    combined_audio.export(
        os.path.abspath("../Frontend/ttsoutput.mp3"), format="mp3"
    )  # Export the combined audio to MP3

    return os.path.abspath("../Frontend/ttsoutput.mp3")  # Return the path to the output file


def process_music(input_file):
  """
  Processes a music file by adjusting volume
  and mixing it with the TTS audio.

  Args:
      input_file (str): Path to the music file.

  Returns:
      None
  """



  #  TTS file
  tts_file = os.path.join("../Frontend", "ttsoutput.mp3")
  tts_duration = pydub.AudioSegment.from_mp3(tts_file).duration_seconds
  print("TTS file duration:", tts_duration)
  tts_audio = pydub.AudioSegment.from_mp3(tts_file)

  # Create a pydub AudioSegment for processing
  music = pydub.AudioSegment.from_mp3(input_file)

  # Adjust volume
  adjusted_music = music - 25  # Reduce volume by 25 decibels (most forums recommend values around this number, play with it if you feel it needs finetuning)
  output_mixed = tts_audio.overlay(adjusted_music,loop = True)
  output_mixed.export(tts_file, format='mp3')
  # Get duration of mixed audio
  mixed_duration = pydub.AudioSegment.from_mp3(tts_file).duration_seconds
  print("Mixed file duration:", mixed_duration)

  # Remove temporary files
  print("Processing audio finished")