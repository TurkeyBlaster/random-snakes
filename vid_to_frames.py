# -*- coding: utf-8 -*-
"""
Created on Sat Mar  7 18:47:19 2020

@author: user
"""

from subprocess import Popen
import os
import io
import sys

from typing import TYPE_CHECKING
StrPath = None
# _typeshed doesn't exist during runtime
if TYPE_CHECKING:
    from _typeshed import StrPath
    
ON_POSIX = 'posix' in sys.builtin_module_names
    
def timestr_check(timestr: str):
    '''
    Check whether a string is in a correct timestamp format: HH:MM:SS.mmm...
    '''
    try:
        [float(num) for num in ':'.split(str(timestr))]
        return True
    except ValueError:
        return False

def vid_fr_aud(
    source: StrPath,
    dest: StrPath,
    rate: int = 24,
    start: str = '',
    duration: str = ''
    ):
    '''
    Split a video into frames and extract the audio.
    Audio will be re-encoded as an .mp3 file.
    
    Parameters
    ----------
    source : String path
        Path location of the video file (can be relative or absolute).
    dest : String path
        Path location into which the files (frames and audio) will be written.
    rate : float, optional
        FPS with which the video will be split. Default is 24 FPS.
    start : Time str, optional
        Timestamp at which the frame and audio extraction will start.
        Format is HH:MM:SS.mmm... where mmm... is optional.
        Default is 00:00:00.
    duration : Time str, optional
        Time specifying the length of the frame and audio extraction.
        Format is HH:MM:SS.mmm... where mmm... is optional.
        Default is until the end.
        
    Returns
    -------
    result : None
        The frames (in the form of .png files) and the audio (in the form of .mp3)
        will be donwloaded to the destination folder.
    '''
    
    # Frame splitting process
    fr_proc = [
        'ffmpeg',
        '-i',
        f'{source}',
        '-r',
        f'{1/rate}' # 1/FPS = SPF
    ]
    
    # Audio re-encoding process
    aud_proc = [
        'ffmpeg',
        '-i',
        f'{source}',
        '-vn',
        '-q:a',
        '0',
        '-map',
        'a'
    ]
    
    # Only include start and duration arguments
    # If they are specified and correctly formatted
    if start and timestr_check(start):
        time_arg = ['-ss', f'{start}']
        fr_proc.extend(time_arg)
        aud_proc.extend(time_arg)
    if duration and timestr_check(duration):
        time_arg = ['-t', f'{duration}']
        fr_proc.extend(time_arg)
        aud_proc.extend(time_arg)
    
    # Add final arg (output destination)
    fr_proc.append(f'{dest}{os.path.pathsep}frame_%04d.png')
    aud_proc.append(f'{dest}{os.path.pathsep}audio.mp3')
    
    # Create a pipe to read data
    input_fd, output_fd = os.pipe()
    
    processes = [
        Popen(
            fr_proc,
            shell = True,
            stdout = output_fd,
            stderr = output_fd,
            close_fds = ON_POSIX
        ),
        Popen(
            aud_proc,
            shell = True,
            stdout = output_fd,
            stderr = output_fd,
            close_fds = ON_POSIX
        )
    ]
    
    os.close(output_fd) # Close unused end
    
    # Read output as soon as they are available
    with io.open(input_fd, 'r', buffering=1) as f:
        for line in f:
            print(line, end='')
    
    # Execute subprocesses
    for proc in processes:
        proc.wait()

if __name__ == '__main__':
    
    import argparse
    
    parser = argparse.ArgumentParser()

    # Add long and short arguments for source file location
    parser.add_argument(
        "--source",
        "-s",
        type = str,
        required = True,
        help = "Source file location (filepath)"
    )
    # Add long and short arguments for destination folder name
    parser.add_argument(
        "--dest",
        "-d",
        type = str,
        required = True,
        help = "Name of destination folder (to be created)\n \
                Default name is 'frames'"
    )
    parser.add_argument(
        "--frame-rate",
        "-f",
        type = int,
        default = 24,
        help = "Number of frames to be skipped over\n \
                Default is 0"
    )
        
    parser.add_argument(
        "--start",
        "-st",
        type = str,
        default = '',
        help = "Timestamp at which the frame and audio extraction will start.\n \
                Format is HH:MM:SS.mmm... where mmm... is optional.\n           \
                Default is 00:00:00"
    )
        
    parser.add_argument(
        "--duration",
        "-du",
        type = str,
        default = '',
        help = "Time specifying the length of the frame and audio extraction.\n \
                Format is HH:MM:SS.mmm... where mmm... is optional.\n           \
                Default is until the end."
    )
    
    # Read args from command line
    args = parser.parse_args()
    vid_fr_aud(args.source, args.dest, args.frame_rate, args.start, args.duration)