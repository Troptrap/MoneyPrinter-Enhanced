import os
import logging
import sox
from typing import List
from termcolor import colored

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
    cbn = sox.Combiner()
    cbn.build(paths, os.path.abspath("../temp/ttsoutput.mp3"), "concatenate")


def process_music(input_file):
    # Create a transformer
    tfm = sox.Transformer()
    target_rate = sox.file_info.sample_rate(
        os.path.abspath("../temp/ttsoutput.mp3")
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
        os.path.abspath("../temp/ttsoutput.mp3")
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
        [os.path.abspath("../temp/ttsoutput.mp3"), audio2_path],
        os.path.abspath("../temp/mixed_audio.mp3"),
        "mix",
    )
    duration_mixed = sox.file_info.duration(
        os.path.abspath("../temp/mixed_audio.mp3")
    )
    print("Mixed file duration: " + str(duration_mixed))
    # Remove the temporary file if it was created
    print("Succesfull mixing! Cleaning ..")
    os.remove("../temp/ttsoutput.mp3")
    os.rename("../temp/mixed_audio.mp3","../temp/ttsoutput.mp3")
    if "repeated" in audio2_path or "trimmed" in audio2_path:
        os.remove(audio2_path)

