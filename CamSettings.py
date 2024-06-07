import configparser
import json

config = configparser.ConfigParser()
config.read('CamsSetup.ini')

cams = json.loads(config.get('cams','idx'))
aliases = json.loads(config.get('cams','aliases'))
focusvalues = json.loads(config.get('cams','focusvalues'))
wbvalues = json.loads(config.get('cams','wbvalues'))
expvalues = json.loads(config.get('cams','expvalues'))
isovalues = json.loads(config.get('cams','isovalues'))
resolution = json.loads(config.get('cams','resolution'))
video_folder = config.get('cams','video_folder')
video_copy_to_folder = config.get('cams','copy_2_folder')

def getIndex(camIdx):
    index = 0
    for cam in cams:
        if cam == camIdx:
            return index
        index += 1

def getAlias(camIdx):
    return aliases[getIndex(camIdx)]

def getFocusValue(camIdx):
    return focusvalues[getIndex(camIdx)]

def getWBValue(camIdx):
    return wbvalues[getIndex(camIdx)]

def getEXPValue(camIdx):
    return expvalues[getIndex(camIdx)]

def getResolution(camIdx):
    return resolution[getIndex(camIdx)]

def getVideoFolder():
    return video_folder
def getVideoCopyToFolder():
    return video_copy_to_folder

def FilesNeed2BeCopied():
    if not video_copy_to_folder:
        return False
    else:
        return True