import numpy as np
import cv2
import time
import collections

from networktables import NetworkTables
import cscore as cs

from cvsink_thread import CvSinkThread, crop

from detect_target import detect_target


front_cam = cs.UsbCamera("front_cam", 0)
front_cam.setVideoMode(cs.VideoMode.PixelFormat.kMJPEG, 480, 270, 30)
front_cam.setBrightness(40)
front_cam.setExposureManual(2)

front_cam_sink = cs.CvSink("front_cam_sink")
front_cam_sink.setSource(front_cam)

mjpeg_source = cs.CvSource("mjpeg_source", cs.VideoMode.PixelFormat.kMJPEG, 320, 240, 8)
mjpeg_server = cs.MjpegServer("mjpeg_server", 8083)
mjpeg_server.setSource(mjpeg_source)
mjpeg_server.setDefaultCompression(50)
mjpeg_server.setCompression(50)

thread = CvSinkThread(front_cam_sink, (270, 480, 3))

def main_loop():
    # grab frame
    frame = thread.get_frame()

    detect_target(frame)

    # show frame
    mjpeg_source.putFrame(crop(frame, 320, 240))

print("Started")

while True:
    main_loop()
    time.sleep(0.005)

