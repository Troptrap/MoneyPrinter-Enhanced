import os
import logging
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



def concat_audio(paths: List[str]) -> str:
    combined_audio = pydub.AudioSegment.empty()  # Create an empty AudioSegment to hold the combined audio
    if len(paths)<2:
      return("List contains only one song")
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