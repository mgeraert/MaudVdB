#!/usr/bin/env python3

import depthai as dai
import contextlib
import keyboard
import CamSettings
import ConvertH265
import PySimpleGUI as sg
import subprocess
import os

from datetime import datetime
from Cam_files import Cam_files

cam_files = Cam_files()

print(dai.__version__)  # print depthai version

do_log  = 0
do_loop = 1

started = 0
stopped = 0

def create_pipeline(resolution, focus_value):
    # Create pipeline
    pipeline = dai.Pipeline()

    # Define sources and outputs
    cam_rgb = pipeline.create(dai.node.ColorCamera)
    cam_rgb.setFps(60)
    cam_rgb.initialControl.setManualFocus(focus_value)
    video_enc = pipeline.create(dai.node.VideoEncoder)
    xout = pipeline.create(dai.node.XLinkOut)

    xout.setStreamName('h265')

    # Properties
    cam_rgb.setBoardSocket(dai.CameraBoardSocket.CAM_A)
    if resolution == 1080:
        cam_rgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
    else:
        cam_rgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_720_P)
    video_enc.setDefaultProfilePreset(60, dai.VideoEncoderProperties.Profile.H265_MAIN)
    fps = cam_rgb.getFps();

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




layout = [
    [sg.Button('Start', key='-START-'), sg.Button('Stop', key='-STOP-'), sg.Button('Exit', key='-EXIT-')],
    [sg.Text('Status: ', size=(10,1)), sg.Text('', size=(50,1), key='-STATUS-')],
    [sg.Text('Cams found: ', size=(10,1)), sg.Text('', size=(10,1), key='-CAMS-')],
    [sg.Text('File loc:', size=(10,1)), sg.Button('Open', key='-OPEN-'), sg.Text('', size=(50,1), key='-FILELOC-')],
    [sg.Text('Frames:', size=(10,1)), sg.Text('', size=(10,1), key='-FRAMES-')]
]

window = sg.Window('Video control', layout, size=(500, 200), finalize=True)

def disableButtons(state):
    window["-START-"].update(disabled=state)
    window["-STOP-"].update(disabled=state)
    window["-EXIT-"].update(disabled=state)

disableButtons(True)


# Get current date and time

# Use ExitStack to manage devices context
with contextlib.ExitStack() as stack:
    device_infos = dai.Device.getAllAvailableDevices()

    print ("Found " + str(device_infos.__len__()) + " camera's:")
    for device in device_infos:
        print (device.mxid + " - " + CamSettings.getAlias(device.mxid))

    usb_speed = dai.UsbSpeed.SUPER
    openvino_version = dai.OpenVINO.Version.VERSION_2021_4

    queues = []
    tasks = []
    device_count = 0

    for device_counter, device_info in enumerate(device_infos, start=1):
        mxID = device_info.mxid
        dev_str = mxID + " - " + CamSettings.getAlias(mxID)
        print(f"=== Connecting to {dev_str}")
        window['-STATUS-'].update(f"=== Connecting to {dev_str}")
        window.refresh()
        device = stack.enter_context(dai.Device(openvino_version, device_info, usb_speed))
        print(f"===   Connected to {dev_str}")
        window['-STATUS-'].update(f"===   Connected to {dev_str}")
        window.refresh()

        pipeline = create_pipeline(CamSettings.getResolution(mxID), CamSettings.getFocusValue(mxID))
        device.startPipeline(pipeline)

        file_name_numbered = cam_files.run_dir + "\\"  + CamSettings.getAlias(mxID) + ".h265"

        q = device.getOutputQueue(name="h265", maxSize=1, blocking=True)
        queues.append((q, device.getMxId()))

    device_count = queues.__len__()

    window['-STATUS-'].update("Ready to record")
    window.refresh()

    print("Ready to record. Click inside the console to set focus. Type R to start recording, T to stop recoring, Y to stop program")

    window['-CAMS-'].update(str(device_count))
    window['-FILELOC-'].update(cam_files.get_log_folder())

    counter = 0
    disableButtons(False)

    while do_loop:

        event, values = window.read(timeout=10)

        if event == sg.WINDOW_CLOSED:
            do_loop = 0
            break
        elif event == '-START-':
            do_log = 1
            started = 1
            stopped = 0
            cam_files.re_init_folders()
            window['-FILELOC-'].update(cam_files.get_run_dir())
            print("Start logging")
        elif event == '-STOP-':
            do_log = 0
            started = 0
            stopped = 1
            print("Stop logging")
            ConvertH265.convertH265Dir(cam_files.get_run_dir())
        elif event == '-OPEN-':
            os.startfile(cam_files.get_run_dir())
        elif event == '-EXIT-':
            do_loop = 0
            print("Stopping program - Please wait a few seconds..")
            window.close()

        if keyboard.is_pressed("r") and not started:
            do_log = 1
            started = 1
            stopped = 0
            cam_files.re_init_folders()
            print("Start logging")

        if keyboard.is_pressed("t") and not stopped:
            do_log = 0
            started = 0
            stopped = 1
            print("Stop logging")
            ConvertH265.convertH265Dir(cam_files.get_run_dir())

        if keyboard.is_pressed("y"):
            do_loop = 0
            print("Stopping program - Please wait a few seconds..")
            window.close()

        if do_log:

            for queuetuple in queues:
                queue = queuetuple[0]
                cam_idx = queuetuple[1]
                fname = cam_files.get_stream_fname(cam_idx)

                with open(fname, 'a') as video_file:

                    try:
                            h265_packet = queue.get()  # Blocking call, will wait until a new data has arrived
                            if h265_packet is not None:

                                ts = h265_packet.getTimestamp()

                                h265_packet.getData().tofile(video_file)  # Appends the packet data to the opened file

                                with open(cam_files.log_file_name, 'a') as log_file:
                                    log_file.write(str(counter) + " " + CamSettings.getAlias(cam_idx) + " " + str(ts) + "\n")

                    except KeyboardInterrupt:
                        print('Hello user, you have pressed ctrl-c button.')
                    except Exception as e:
                        print(f"Error while saving stream: {e}")

            window['-FRAMES-'].update(str(counter))

            if counter % 60 == 0:
                if device_count == 0:
                    print(str(counter))
                else:
                    print('    ' + str(counter))

            counter = counter + 1

print('Done.')


