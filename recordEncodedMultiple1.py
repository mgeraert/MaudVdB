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

# Check if the directory exists
if not os.path.exists(file_location):
    # If not, create the directory
    os.makedirs(file_location)
    print(f"Directory '{file_location}' created successfully.")
else:
    print(f"Directory '{file_location}' already exists.")

def create_pipeline():
    # Create pipeline
    pipeline = dai.Pipeline()

    # Define sources and outputs
    cam_rgb = pipeline.create(dai.node.ColorCamera)
    cam_rgb.initialControl.setManualFocus(255)
    video_enc = pipeline.create(dai.node.VideoEncoder)
    xout = pipeline.create(dai.node.XLinkOut)

    xout.setStreamName('h265')

    # Properties
    cam_rgb.setBoardSocket(dai.CameraBoardSocket.CAM_A)
    cam_rgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
    video_enc.setDefaultProfilePreset(60, dai.VideoEncoderProperties.Profile.H265_MAIN)

    # Linking
    cam_rgb.video.link(video_enc.input)
    video_enc.bitstream.link(xout.input)
    return pipeline

def save_stream(queue, file_name, device_count):
    with open(file_name, 'wb') as video_file:
        print(f"Saving stream to {file_name}. Press Ctrl+C to stop encoding...")
        counter = 0
        try:
            while counter<500:
                h265_packet = queue.tryGet()  # Blocking call, will wait until a new data has arrived
                if h265_packet is not None:
                    h265_packet.getData().tofile(video_file)  # Appends the packet data to the opened file
                    counter = counter + 1
                    if device_count == 0:
                        print(str(counter))
                    else:
                        print('    ' + str(counter))
        except KeyboardInterrupt:
            print('Hello user, you have pressed ctrl-c button.')
        except Exception as e:
            print(f"Error while saving stream: {e}")

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
        print(f"=== Connected to {device_info.getMxId()}")

        calibData = device.readCalibration()
        intrinsics = calibData.getCameraIntrinsics(dai.CameraBoardSocket.CAM_A)
        distortionValues = calibData.getDistortionCoefficients(dai.CameraBoardSocket.CAM_A)

        with open("intrinsics.txt","w") as intrinsics_file:
            intrinsics_file.write(device_info.getMxId() + '\n')

            intrinsics_file.write('  Intrinsics\n')

            for x in range(3):
                intrinsics_file.write('    '  + str(intrinsics[0][0]) + ' ' + str(intrinsics[0][1]) + ' ' + str(intrinsics[0][2]) + '\n')

            intrinsics_file.write('  Distortion\n')
            for x in range(14):
                intrinsics_file.write('    ' + str(distortionValues[x]) + '\n')


        pipeline = create_pipeline()
        device.startPipeline(pipeline)

        file_name_numbered = f"{file_base_name}_{device_counter}.h265"
        file_name_numbered = file_location + "\\" + file_name_numbered
        q = device.getOutputQueue(name="h265", maxSize=1, blocking=True)
        queues.append((q, file_name_numbered, device.getMxId()))

    counter = 0
    while counter <= 100:

        for queuetuple in queues:
            queue = queuetuple[0]
            fname = queuetuple[1]
            cam_name = queuetuple[2]

            with open(fname, 'a') as video_file:

                try:
                        h265_packet = queue.get()  # Blocking call, will wait until a new data has arrived
                        if h265_packet is not None:

                            ts = h265_packet.getTimestamp()

                            h265_packet.getData().tofile(video_file)  # Appends the packet data to the opened file

                            with open(log_file_name, 'a') as log_file:
                                log_file.write(str(counter) + " " + cam_name + " " + str(ts) + "\n")

                            if device_count == 0:
                                print(str(counter))
                            else:
                                print('    ' + str(counter))

                except KeyboardInterrupt:
                    print('Hello user, you have pressed ctrl-c button.')
                except Exception as e:
                    print(f"Error while saving stream: {e}")

        counter = counter + 1

print('Done.')


