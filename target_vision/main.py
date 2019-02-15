import numpy as np
import cv2
import time
import collections

from networktables import NetworkTables
import cscore as cs

from cvsink_thread import CvSinkThread

# CONFIG OPTIONS
FRONT_CAM = "/dev/v4l/by-id/usb-046d_HD_Webcam_C615_1A5D6660-video-index0"
FRONT_LINECAM = "/dev/v4l/by-id/usb-HD_Camera_Manufacturer_USB_2.0_Camera-video-index0"
REAR_CAM = "/dev/v4l/by-id/usb-046d_HD_Pro_Webcam_C920_A63EFE4F-video-index0"

ROBORIO_IP = "192.168.0.100"

FRONT_BRIGHTNESS_VISION = 70
FRONT_BRIGHTNESS_HUMAN = 50
FRONT_EXPOSURE_VISION = 10
FRONT_EXPOSURE_HUMAN = 50


FRONT_LINE_BRIGHTNESS_VISION = 70
FRONT_LINE_BRIGHTNESS_HUMAN = 50
FRONT_LINE_EXPOSURE_VISION = 10
FRONT_LINE_EXPOSURE_HUMAN = 50


REAR_BRIGHTNESS_VISION = 70
REAR_BRIGHTNESS_HUMAN = 50
REAR_EXPOSURE_VISION = 10
REAR_EXPOSURE_HUMAN = 50


# General setup
NetworkTables.initialize(server=ROBORIO_IP)

# Globals
front_cam = cs.UsbCamera("front_cam", FRONT_CAM)
front_cam.setVideoMode(cs.VideoMode.PixelFormat.kMJPEG, 320, 240, 30)
front_cam_sink = cs.CvSink("front_cam_sink")
front_cam_sink.setSource(front_cam)

front_linecam = cs.UsbCamera("front_linecam", FRONT_LINECAM)
front_linecam.setVideoMode(cs.VideoMode.PixelFormat.kMJPEG, 320, 240, 30)
front_linecam_sink = cs.CvSink("front_linecam_sink")
front_linecam_sink.setSource(front_linecam)

rear_cam = cs.UsbCamera("rear_cam", REAR_CAM)
rear_cam.setVideoMode(cs.VideoMode.PixelFormat.kMJPEG, 320, 240, 30)
rear_cam_sink = cs.CvSink("rear_cam_sink")
rear_cam_sink.setSource(rear_cam)


table = NetworkTables.getTable("VisionTable")

mjpeg_source = cs.CvSource("mjpeg_source", cs.VideoMode.PixelFormat.kMJPEG, 320, 240, 8)
mjpeg_server = cs.MjpegServer("mjpeg_server", 8083)
mjpeg_server.setSource(mjpeg_source)
mjpeg_server.setDefaultCompression(50)
mjpeg_server.setCompression(50)

thread = CvSinkThread(front_cam_sink, (240, 320, 3))

current_camera = 0 # 0 = front, 1 = front line, 2 = rear
vision_enabled = False

def main_loop():
    global current_camera, vision_enabled, frame

    prev_cam = current_camera
    current_camera = int(round(table.getNumber("current_camera", 0)))
    if current_camera not in [0, 1, 2]:
        current_camera = 0

    if prev_cam != current_camera:
        thread.newstream = [front_cam_sink, front_linecam_sink, rear_cam_sink][current_camera]

    prev = vision_enabled
    vision_enabled = table.getBoolean("vision_enabled", False)

    # change exposure between driver cam and vision-only
    if prev != vision_enabled:
        if vision_enabled:
            front_cam.setBrightness(FRONT_BRIGHTNESS_VISION)
            front_cam.setExposureManual(FRONT_EXPOSURE_VISION)

            front_linecam.setBrightness(FRONT_LINE_BRIGHTNESS_VISION)
            front_linecam.setExposureManual(FRONT_LINE_EXPOSURE_VISION)

            rear_cam.setBrightness(REAR_BRIGHTNESS_VISION)
            rear_cam.setExposureManual(REAR_EXPOSURE_VISION)
        else:
            front_cam.setBrightness(FRONT_BRIGHTNESS_HUMAN)
            front_cam.setExposureManual(FRONT_EXPOSURE_HUMAN)

            front_linecam.setBrightness(FRONT_LINE_BRIGHTNESS_HUMAN)
            front_linecam.setExposureManual(FRONT_LINE_EXPOSURE_HUMAN)

            rear_cam.setBrightness(REAR_BRIGHTNESS_HUMAN)
            rear_cam.setExposureManual(REAR_EXPOSURE_HUMAN)

            table.putBoolean("vision_ready", False)

    # grab frame
    frame = thread.get_frame()

    if vision_enabled:
        # vision processing
        cv2.circle(frame, (50, 50), 15, (0, 0, 0), -1)

    # resize, greyscale, and send out frame to mjpeg
    mjpeg_source.putFrame(frame[::1, ::1])
    #mjpeg_source.putFrame(cv2.cvtColor(frame[::1, ::1], cv2.COLOR_BGR2GRAY))

    # Must be at end
    if prev and vision_enabled:
        table.putBoolean("vision_ready", True)
    else:
        table.putBoolean("vision_ready", False)

print("Started")

timestamps = collections.deque(maxlen=25)
timestamps.append(time.time())
while True:
    main_loop()
    time.sleep(0.005)
    timestamps.append(time.time())
    #print(len(timestamps) / (timestamps[-1] - timestamps[0]))

