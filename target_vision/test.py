import cv2
import numpy as np
#from detect_target import

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

mtx = np.array([[635.160599, 000.000000, 330.034234],
                [000.000000, 640.594657, 233.887105],
                [000.000000, 000.000000, 001.000000]])

coeffs = np.array([0.036169, -0.145812, -0.000633, 0.004249, 0.000000])

while True:
    img = cap.read()[1]
    print(img.shape)

    # process

    cv2.imshow("image", img)
    cv2.waitKey(10)
