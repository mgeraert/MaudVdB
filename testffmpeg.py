import os
from subprocess import call, check_output
import subprocess
from pathlib import Path, PureWindowsPath, PurePosixPath

filepath = (r'C:\Users\lucp2284\Documents\VideosOak1\2024-05-02\11-07-18\CAM3.hvc1.mp4')
filepath = filepath.replace(os.sep, '/')
basefilepath, extension = os.path.splitext(filepath)

output_filepath = basefilepath + '.jpg'
output_filepath = output_filepath.replace(os.sep, '/')

video_opts = r' -vf "select=eq(n\,60)" -q:v 3 '



command = 'ffmpeg -i ' + filepath + video_opts + output_filepath
#command.encode('unicode_escape')

subprocess.call(command, shell=True)

call(['ffmpeg', '-i', filepath.__str__()] + video_opts.split() + [output_filepath.__str__()])

