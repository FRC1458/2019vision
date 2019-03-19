import numpy as np
import cv2
import time
import collections
import colorsys

from networktables import NetworkTables
import cscore as cs

from detect_target import detect_target
from cvsink_thread import CvSinkThread, crop

# CONFIG OPTIONS

"""
FRONT_CAM = "/dev/v4l/by-id/usb-046d_HD_Webcam_C615_1A5D6660-video-index0"
FRONT_LINECAM = "/dev/v4l/by-id/usb-HD_Camera_Manufacturer_USB_2.0_Camera-video-index0"
REAR_CAM = "/dev/v4l/by-id/usb-046d_0825_8710FCE0-video-index0"

ROBORIO_IP = "192.168.0.100"
"""

FRONT_CAM = "/dev/v4l/by-id/usb-046d_HD_Pro_Webcam_C920_A63EFE4F-video-index0"
FRONT_LINECAM = "/dev/v4l/by-id/usb-HD_Camera_Manufacturer_USB_2.0_Camera-video-index0"
REAR_CAM = "/dev/v4l/by-id/usb-Microsoft_Microsoft®_LifeCam_HD-3000-video-index0"

ROBORIO_IP = "10.14.58.2"
time.sleep(15)

MIN_PRESSURE = 65 # psi

FRONT_BRIGHTNESS_VISION = 50
FRONT_BRIGHTNESS_HUMAN = 50
FRONT_EXPOSURE_VISION = 1
FRONT_EXPOSURE_HUMAN = 50


FRONT_LINE_BRIGHTNESS_VISION = 5
FRONT_LINE_BRIGHTNESS_HUMAN = 5
FRONT_LINE_EXPOSURE_VISION = 2
FRONT_LINE_EXPOSURE_HUMAN = 2


REAR_BRIGHTNESS_VISION = 70
REAR_BRIGHTNESS_HUMAN = 50
REAR_EXPOSURE_VISION = 10
REAR_EXPOSURE_HUMAN = 50


# General setup
NetworkTables.initialize(server=ROBORIO_IP)

# Globals
# TODO change resolution to widescreen on wider cameras

front_cam = cs.UsbCamera("front_cam", FRONT_CAM)
front_cam.setVideoMode(cs.VideoMode.PixelFormat.kMJPEG, 480, 270, 30)
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

mjpeg_source = cs.CvSource("mjpeg_source", cs.VideoMode.PixelFormat.kMJPEG, 320, 240, 6)
mjpeg_server = cs.MjpegServer("mjpeg_server", 5801)
mjpeg_server.setSource(mjpeg_source)
mjpeg_server.setDefaultCompression(30)
mjpeg_server.setCompression(30)

thread = CvSinkThread(front_cam_sink, (240, 320, 3))

current_camera = 0 # 0 = front, 1 = front line, 2 = rear
vision_enabled = False

pin_time = 0

def main_loop():
    global current_camera, vision_enabled, frame, pin_time

    prev_cam = current_camera
    current_camera = int(round(table.getNumber("current_camera", 0)))
    if current_camera not in [0, 1, 2]:
        current_camera = 0

    if prev_cam != current_camera:
        thread.newstream = [front_cam_sink, front_linecam_sink, rear_cam_sink][current_camera]

    prev = vision_enabled
    vision_enabled = table.getBoolean("vision_enabled", False)
    pinning = table.getBoolean("defense_timer", False)
    pressure = table.getNumber("pressure_psi", 0)

    # change exposure between driver cam and vision-only
    if prev != vision_enabled:
        if vision_enabled:
            front_cam.setBrightness(FRONT_BRIGHTNESS_VISION)
            front_cam.setExposureManual(FRONT_EXPOSURE_VISION)

            front_linecam.setBrightness(23)

            rear_cam.setBrightness(REAR_BRIGHTNESS_VISION)
            rear_cam.setExposureManual(REAR_EXPOSURE_VISION)
        else:
            front_cam.setBrightness(FRONT_BRIGHTNESS_HUMAN)
            front_cam.setExposureManual(FRONT_EXPOSURE_HUMAN)

            front_linecam.setBrightness(23)

            rear_cam.setBrightness(REAR_BRIGHTNESS_HUMAN)
            rear_cam.setExposureManual(REAR_EXPOSURE_HUMAN)

            table.putBoolean("vision_ready", False)

    # grab frame
    frame = thread.get_frame()

    if vision_enabled:
        if current_camera == 1:
            offset = 0.0
            angle = 0.0

            table.putNumber("horiz_offset", offset)
            table.putNumber("angle_offset", angle)

        else:
            offset, angle = detect_target(frame)
            if offset is None:
                offset = 0.0

            if angle is None:
                angle = 0.0

            table.putNumber("horiz_offset", offset)
            table.putNumber("angle_offset", angle)

    if current_camera == 1:
        frame = frame[::-1, ::-1]

    # crop before draw ui
    frame = crop(frame[::1, ::1], 320, 240).copy()

    if pinning:
        if pin_time == 0:
            pin_time = time.time()
        else:
            _time = (time.time() - pin_time)
            coord = int(240 * (_time / 5.0))
            rgb = colorsys.hsv_to_rgb(max(0.25 - 0.25*(_time / 5.0), 0), 0.92, 0.81)
            cv2.rectangle(frame, (300, 0), (319, coord), (255*rgb[2], 255*rgb[1], 255*rgb[0]), -1)
    else:
        pin_time = 0

    if current_camera == 1:
        coord = int(240 * (pressure / 120.0))
        thresh = int(240 * (MIN_PRESSURE / 120.0))
        cv2.rectangle(frame, (0, 0), (20, coord), (255, 206, 94), -1)
        cv2.rectangle(frame, (0, thresh), (20, thresh+3), (249, 112, 222), -1)


    # resize, greyscale, and send out frame to mjpeg
    mjpeg_source.putFrame(frame)
    #mjpeg_source.putFrame(cv2.cvtColor(frame[::1, ::1], cv2.COLOR_BGR2GRAY))

    # Must be at end
    if prev and vision_enabled:
        table.putBoolean("vision_ready", True)
    else:
        table.putBoolean("vision_ready", False)

print("Started")

while True:
    main_loop()
    time.sleep(0.005)

