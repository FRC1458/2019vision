import numpy as np
import cv2

from networktables import NetworkTables
import cscore as cs

# CONFIG OPTIONS
FRONT_CAM = 0
FRONT_LINECAM = 1
REAR_CAM = 2
ROBORIO_IP = "roborio-1458-frc.local"

FRONT_BRIGHTNESS_VISION = 100
FRONT_BRIGHTNESS_HUMAN = 100
FRONT_EXPOSURE_VISION = 100
FRONT_EXPOSURE_HUMAN = 100


FRONT_LINE_BRIGHTNESS_VISION = 100
FRONT_LINE_BRIGHTNESS_HUMAN = 100
FRONT_LINE_EXPOSURE_VISION = 100
FRONT_LINE_EXPOSURE_HUMAN = 100


REAR_BRIGHTNESS_VISION = 100
REAR_BRIGHTNESS_HUMAN = 100
REAR_EXPOSURE_VISION = 100
REAR_EXPOSURE_HUMAN = 100


# General setup
NetworkTables.initialize(server=ROBORIO_IP)

# Globals
front_cam = cs.UsbCamera("front_cam", FRONT_CAM)
front_cam.setVideoMode(cs.VideoMode.PixelFormat.kMJPEG, 640, 480, 30)
front_cam_sink = cs.CvSink("front_cam_sink")
front_cam_sink.setSource(front_cam)

front_linecam = cs.UsbCamera("front_linecam", FRONT_LINECAM)
front_linecam.setVideoMode(cs.VideoMode.PixelFormat.kMJPEG, 640, 480, 30)
front_linecam_sink = cs.CvSink("front_linecam_sink")
front_linecam_sink.setSource(front_linecam)

rear_cam = cs.UsbCamera("rear_cam", REAR_CAM)
rear_cam.setVideoMode(cs.VideoMode.PixelFormat.kMJPEG, 640, 480, 30)
rear_cam_sink = cs.CvSink("rear_cam_sink")
rear_cam_sink.setSource(rear_cam)

table = NetworkTables.getTable("VisionTable")

mjpeg_source = cs.CvSource("mjpeg_source", cs.VideoMode.PixelFormat.kMJPEG, 320, 240, 30)
mjpeg_server = cs.MjpegServer("mjpeg_server", 8083)
mjpeg_server.setSource(mjpeg_source)

current_camera = 0 # 0 = front, 1 = front line, 2 = rear
vision_enabled = False

def main_loop():
    prev_cam = current_camera
    current_camera = table.getNumber("current_camera")
    prev = vision_enabled
    vision_enabled = table.getBoolean("vision_enabled")

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

    # grab relavent frame
    frame = None


    pass


