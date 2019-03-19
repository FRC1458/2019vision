import numpy as np
import cv2
import time
import collections
import colorsys

from detect_target import detect_target

img = cv2.imread("/Users/anish/Desktop/vision_triple.png")

while True:
    frame = img.copy()
    offset, angle = detect_target(frame)

    cv2.imshow("frame", frame)
    cv2.waitKey(5)

