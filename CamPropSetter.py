import PySimpleGUI as sg
import CamSettings
import contextlib
import depthai as dai
import cv2


def create_pipeline(resolution, focus_value):
    # Create pipeline
    pipeline = dai.Pipeline()

    # Define sources and outputs
    cam_rgb = pipeline.create(dai.node.ColorCamera)
    cam_rgb.setFps(60)
    cam_rgb.initialControl.setManualFocus(focus_value)
    xout = pipeline.create(dai.node.XLinkOut)
    xout.setStreamName("rgb")
    cam_rgb.setPreviewSize(1027, 720)
    cam_rgb.setInterleaved(False)
    cam_rgb.preview.link(xout.input)
    return pipeline

cam_list = []
label_list_header = sg.Text("Camera list", font=("Helvetica", 12, "bold"))
camera_list = sg.Listbox(cam_list, size=(40, 14), key='-CAM_LIST-', enable_events=True)
layout = [
    [label_list_header],
    [camera_list],
    [sg.Button('Start', key='-START-'), sg.Button('Stop', key='-STOP-'), sg.Button('Exit', key='-EXIT-')],
    [sg.Text('Status: ', size=(10,1)), sg.Text('', size=(50,1), key='-STATUS-')],
    [sg.Text('Cam selected: ', size=(14,1)), sg.Text('', size=(50,1), key='-CAMSELECTED-')],
    [sg.Button('Preview', key='-PREVIEW-')],
    [sg.Text('File loc:', size=(10,1)), sg.Button('Open', key='-OPEN-'), sg.Text('', size=(50,1), key='-FILELOC-')],
    [sg.Text('Frames:', size=(10,1)), sg.Text('', size=(10,1), key='-FRAMES-')]
]

window = sg.Window('Video control', layout, size=(600, 400), finalize=True)

focus = 127

with contextlib.ExitStack() as stack:
    device_infos = dai.Device.getAllAvailableDevices()

    print ("Found " + str(device_infos.__len__()) + " camera's:")
    for device in device_infos:
        print (device.mxid + " - " + CamSettings.getAlias(device.mxid))

    usb_speed = dai.UsbSpeed.SUPER
    openvino_version = dai.OpenVINO.Version.VERSION_2021_4

    pipeline_list = []
    tasks = []
    device_count = 0

    for device_counter, device_info in enumerate(device_infos, start=1):
        mxID = device_info.mxid
        dev_str = mxID + " - " + CamSettings.getAlias(mxID)
        print(f"=== Connecting to {dev_str}")
        window['-STATUS-'].update(f"=== Connecting to {dev_str}")
        window.refresh()
        print(f"===   Connected to {dev_str}")
        window['-STATUS-'].update(f"Connected to {dev_str}")
        cam_list.append(dev_str)
        window['-CAM_LIST-'].update(cam_list)
        window.refresh()
        #pipeline = create_pipeline(CamSettings.getResolution(mxID), CamSettings.getFocusValue(mxID))
        #device.startPipeline(pipeline)
        #pipeline_list.append((pipeline, device.getMxId()))

window['-STATUS-'].update("")
window.refresh()

previous_selection = ''


while True:
    event, values = window.read(timeout=20)
    if event in (None, 'Clear'):
        break
    elif event == '+Focus':
        focus = 127
    elif event == '-Focus':
        focus = 127
    elif event == '-CAM_LIST-':
        focus = 127

    selected_item = values['-CAM_LIST-']
    if selected_item != []:
        string_parts = selected_item[0].split(' - ')
        if selected_item[0] != previous_selection:
            previous_selection = selected_item[0]
            window['-CAMSELECTED-'].update(selected_item[0])

            for device_counter, device_info in enumerate(device_infos, start=1):
                mxID = device_info.mxid
                if mxID == selected_item[0].split(' - ')[0]:
                    pipeline = create_pipeline(CamSettings.getResolution(mxID), CamSettings.getFocusValue(mxID))
                    with dai.Device(pipeline,usb2Mode=True) as device:
                        qRgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=True)




            inRgb = qRgb.get()  # blocking call, will wait until a new data has arrived
            cv2.imshow("rgb", inRgb.getCvFrame())


window.close()
quit()
