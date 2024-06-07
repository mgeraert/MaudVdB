#!/usr/bin/env python3

import PySimpleGUI as sg
import CamSettings
import depthai as dai
import cv2

focus_value = 0

def CreatePipeLine(focusValue):
    focus_value = focusValue
    pipeline = dai.Pipeline()
    camRgb = pipeline.create(dai.node.ColorCamera)
    camRgb.setFps(60)
    camRgb.initialControl.setManualFocus(focusValue)
    xoutRgb = pipeline.create(dai.node.XLinkOut)
    xoutRgb.setStreamName("rgb")
    camRgb.setPreviewSize(1027, 720)
    camRgb.setInterleaved(False)
    camRgb.preview.link(xoutRgb.input)

    cam_control_in = pipeline.createXLinkIn()
    cam_control_in.setStreamName("cam_control")
    cam_control_in.out.link(camRgb.inputControl)

    return pipeline

def getDeviceInfo(device_infos, mxid):
    for device_info in device_infos:
        if device_info.mxid == mxid:
            return device_info

cam_list = []
label_list_header = sg.Text("Camera list", font=("Helvetica", 12, "bold"))
camera_list = sg.Listbox(cam_list, size=(40, 14), key='-CAM_LIST-', enable_events=True)
lblF = [sg.Text('Focus ', size=(14,1)), sg.Text('', size=(50,1), key='-LBLFOCUS-')],
sliderF = sg.Slider((0, 255), size=(40, 16), orientation='horizontal', key='-SLIDERF-')
lblW = [sg.Text('WhiteBalance ', size=(14,1)), sg.Text('', size=(50,1), key='-LBLWB-')],
sliderW = sg.Slider((1000, 12000), size=(40, 16), orientation='horizontal', key='-SLIDERW-')

layout = [
    [label_list_header],
    [camera_list],
    [sg.Text('Status: ', size=(10,1)), sg.Text('', size=(50,1), key='-STATUS-')],
    [sg.Text('Cam selected: ', size=(14,1)), sg.Text('', size=(50,1), key='-CAMSELECTED-')],
    [sliderF],
    [lblF],
    [sliderW],
    [lblW],
    [sg.Text('File loc:', size=(10,1)), sg.Button('Open', key='-OPEN-'), sg.Text('', size=(50,1), key='-FILELOC-')],
    [sg.Text('Frames:', size=(10,1)), sg.Text('', size=(10,1), key='-FRAMES-')]
]

window = sg.Window('Video control', layout, size=(500, 550), finalize=True)

device_infos = dai.Device.getAllAvailableDevices()

for device_info in device_infos:

    dev_str = device_info.mxid + " - " + CamSettings.getAlias(device_info.mxid)
    print(f"=== Connecting to {dev_str}")
    window['-STATUS-'].update(f"=== Connecting to {dev_str}")
    window.refresh()
    print(f"===   Connected to {dev_str}")
    window['-STATUS-'].update(f"Connected to {dev_str}")
    cam_list.append(dev_str)
    window['-CAM_LIST-'].update(cam_list)
    window.refresh()

window['-STATUS-'].update("")
window.refresh()

usb_speed = dai.UsbSpeed.SUPER
openvino_version = dai.OpenVINO.Version.VERSION_2021_4

camSelected = device_infos[0]
previous_selection = ''
window_closed = False

window['-CAMSELECTED-'].update(cam_list[0])


while True:
        device = dai.Device(openvino_version,camSelected,usb_speed)
        pipeline = CreatePipeLine(0)
        device.startPipeline(pipeline)
        qRgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
        controlQueue = device.getInputQueue('cam_control')

        previous_focus_value = focus_value
        previous_wb_value = 2700

        while True:

            inRgb = qRgb.get()  # blocking call, will wait until a new data has arrived

            # Retrieve 'bgr' (opencv format) frame
            cv2.imshow("rgb", inRgb.getCvFrame())

            event, values = window.read(timeout=20)

            if event in (None, 'Clear'):
                window_closed = True
                cv2.destroyWindow("rgb")
                break
            elif event == '+Focus':
                focus = 127
            elif event == '-START-':
                focus = 127
            elif event == '-CAM_LIST-':
                focus = 127
            elif previous_focus_value != values['-SLIDERF-']:
                focus_value = int(values['-SLIDERF-'])
                previous_focus_value = focus_value
                ctrl = dai.CameraControl()
                ctrl.setManualFocus(focus_value)
                controlQueue.send(ctrl)
            elif previous_wb_value != values['-SLIDERW-']:
                wb_value = int(values['-SLIDERW-'])
                previous_wb_value = wb_value
                ctrl = dai.CameraControl()
                ctrl.setManualWhiteBalance(wb_value)
                controlQueue.send(ctrl)

            selected_item = values['-CAM_LIST-']
            if selected_item != []:
                string_parts = selected_item[0].split(' - ')
                mxid = string_parts[0]
                if selected_item[0] != previous_selection:
                    previous_selection = selected_item[0]
                    window['-CAMSELECTED-'].update(selected_item[0])
                    camSelected = getDeviceInfo(device_infos, mxid)
                    cv2.destroyWindow("rgb")
                    break

