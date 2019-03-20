import numpy as np
import cv2
import time
import collections
import colorsys
import sys

from detect_target import detect_target

img = cv2.imread(sys.argv[1])

while True:
    frame = img.copy()
    offset, angle = detect_target(frame)

    cv2.imshow("frame", frame)
    cv2.waitKey(5)

