import configparser
import json

config = configparser.ConfigParser()
config.read('CamsSetup.ini')

cams = json.loads(config.get('cams','idx'))
aliases = json.loads(config.get('cams','aliases'))
focusvalues = json.loads(config.get('cams','focusvalues'))
resolution = json.loads(config.get('cams','resolution'))
video_folder = config.get('cams','video_folder')

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

def getResolution(camIdx):
    return resolution[getIndex(camIdx)]

def getVideoFolder():
    return video_folder