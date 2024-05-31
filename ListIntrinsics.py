#!/usr/bin/env python3

import depthai as dai
import contextlib
import os
import configparser
import json

from datetime import datetime

print(dai.__version__)  # print depthai version

current_datetime = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
file_base_name = str(current_datetime)
file_location = 'G:\My Drive\My Documents\PHDs\Maud'
file_location = file_location + "\\" + file_base_name
log_file_name = file_location + "\\" + file_base_name + '_log.txt'

config = configparser.ConfigParser()
config.read('CamsSetup.ini')

cams = json.loads(config.get('cams','idx'))
aliases = json.loads(config.get('cams','aliases'))
focusvalues = json.loads(config.get('cams','focusvalues'))






# Get current date and time

# Use ExitStack to manage devices context
with contextlib.ExitStack() as stack:
    device_infos = dai.Device.getAllAvailableDevices()

    print ("Found camera's:")
    for device in device_infos:
        print (device.mxid)

    usb_speed = dai.UsbSpeed.SUPER
    openvino_version = dai.OpenVINO.Version.VERSION_2021_4

    queues = []
    tasks = []
    device_count = 0

    for device_counter, device_info in enumerate(device_infos, start=1):

        device = stack.enter_context(dai.Device(openvino_version, device_info, usb_speed))

        calibData = device.readCalibration()
        intrinsics = calibData.getCameraIntrinsics(dai.CameraBoardSocket.CAM_A, 1920, 1080)
        distortionValues = calibData.getDistortionCoefficients(dai.CameraBoardSocket.CAM_A)


        print(device_info.getMxId())

        print('  Intrinsics')

        for x in range(3):
            print('    '  + str(intrinsics[0][0]) + ' ' + str(intrinsics[0][1]) + ' ' + str(intrinsics[0][2]))

        print('  Distortion')
        for x in range(14):
            print('    ' + str(distortionValues[x]))




print('Done.')


