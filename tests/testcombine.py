import ffmpeg
import sox
from termcolor import colored
from typing import List
import os
vids =['1.mp4','2.mp4']
max_dur = sox.file_info.duration('ttsoutput.mp3')
max_cl = 5
def combine_videos(video_paths: List[str], max_duration: int, max_clip_duration: int) -> str:
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
    

    video_id = 'videoaudio'
    combined_video_path = f"../temp/{video_id}.mp4"
    
    # Required duration of each clip
    req_dur = max_duration / len(video_paths)

    print(colored("[+] Combining videos...", "blue"))
    print(colored(f"[+] Each clip will be maximum {req_dur} seconds long.", "blue"))



    # Apply filters to each input stream
    # - Trim to the required duration or the remaining duration
    # - Crop and resize to the same aspect ratio and resolution
    # - Set fps to 30
  
    tot_dur = 0
    
    idx = 1
    
    while tot_dur<max_duration:
      for video_path in video_paths:
        if tot_dur>max_duration:
            break
        
        print(colored("[+] Working on clip no "+str(idx),"blue"))
        # Get the duration of the input stream
        iprobe = ffmpeg.probe(video_path)
        input_duration = float(iprobe['format']['duration'])

        # Check if clip is longer than the remaining audio
        if (max_duration - tot_dur) < input_duration:
            input_duration = max_duration - tot_dur

        # Only shorten clips if the calculated clip length (req_dur) is shorter than the actual clip to prevent still image
        if req_dur < input_duration:
            input_duration = req_dur

        if input_duration>max_clip_duration:
          input_duration=max_clip_duration
        if input_duration == 0:
          break

        print('this dur after:'+str(input_duration))
        
          
        # Apply filters to single clips
        
        (
            ffmpeg.input(video_path,ss=0,t=input_duration)
            .video
              #Remove audio
            .filter('crop', 'iw', 'min(ih*0.5625,iw)', '(iw-oh)/2', '(ih-ow)/2') # Crop to the same aspect ratio
            .filter('scale', 1080, 1920) # Resize to the same resolution
            .filter('fps', fps=30) # Set fps to 30
            .output(str(idx)+'.mpg',vcodec='libx264', format='mp4')
            .run()
        )
        # Increment duration until it meets the audio duration from TTS
        tot_dur += input_duration
        idx +=1
        
    
        # Write the clips to the main video
    print(colored("[+] Merging" +str(idx)+"videos..","blue"))
    
    
    input_paths = []
    for f in os.listdir('.'):
      if f.endswith('.mpg'):
        input_paths.append(f)
    open('concat.txt', 'w').writelines([('file %s\n' % input_path) for input_path in input_paths])
    ffmpeg.input('concat.txt', format='concat', safe=0).output('videoaudio.mp4', c='copy', an=None).run()
    
    
    print(colored("[+] Successfully merged","green"))

    return combined_video_path
    
    
          # Concatenate videos
combine_videos(vids, max_dur,max_cl)