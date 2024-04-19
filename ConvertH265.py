'''
Transcode videos to H265 / hvc1.  Skip any file which is already h265 encoded.
https://trac.ffmpeg.org/wiki/Encode/H.265
'''

import os
from subprocess import call, check_output

def list_files_with_extension(directory, extension):
    files_with_extension = []
    for filename in os.listdir(directory):
        if filename.endswith(extension):
            files_with_extension.append(filename)
    return files_with_extension

def get_codec(filepath, channel='v:0'):
    ''' Return the codec and codec-tag for a given channel '''

    output = check_output(['ffprobe', '-v', 'error', '-select_streams', channel,
                           '-show_entries', 'stream=codec_name,codec_tag_string', '-of',
                           'default=nokey=1:noprint_wrappers=1', filepath])

    return output.decode('utf-8').split()


def convertH265File(filepath):

    basefilepath, extension = os.path.splitext(filepath)

    output_filepath = basefilepath + '.hvc1' + '.mp4'

    assert (output_filepath != filepath)

    if os.path.isfile(output_filepath):
        print('Skipping "{}": file already exists'.format(output_filepath))


    print(filepath)

    # Get the video channel codec
    video_codec = get_codec(filepath, channel='v:0')

    if video_codec == []:
        print('Skipping: no video codec reported')


    # Video transcode options
    if video_codec[0] == 'hevc':
        if video_codec[1] == 'hvc1':
            print('Skipping: already h265 / hvc1')

        else:
            # Copy stream to hvc1
            video_opts = '-c:v copy -tag:v hvc1'
    else:
        # Transcode to h265 / hvc1
        video_opts = '-c:v libx265 -crf 28 -tag:v hvc1 -preset slow -threads 8'

    # Get the audio channel codec
    audio_codec = get_codec(filepath, channel='a:0')

    if audio_codec == []:
        audio_opts = ''
    elif audio_codec[0] == 'aac':
        audio_opts = '-c:a copy'
    else:
        audio_opts = '-c:a aac -b:a 128k'

    call(['ffmpeg', '-i', filepath] + video_opts.split() + audio_opts.split() + [output_filepath])

def convertH265Dir(directory_path):

    h265_files = list_files_with_extension(directory_path, '.h265')

    for fname in h265_files:
        fname = os.path.join(directory_path,fname)
        convertH265File(fname)