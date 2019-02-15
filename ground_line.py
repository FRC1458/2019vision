import cv2
import numpy as np
import imutils
from threading import Thread

print("Welcome to TurtwigVision!")

class WebcamVideoStream:
    def __init__(self, src=0, name="WebcamVideoStream", size=None):
        self.stream = cv2.VideoCapture(src)
        if size is not None:
            self.stream.set(3, size[0])
            self.stream.set(4, size[1])

        (self.grabbed, self.frame) = self.stream.read()

        self.name = name

        self.stopped = False

    def start(self):
        # start the thread to read frames from the video stream
        t = Thread(target=self.update, name=self.name, args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                return

            # otherwise, read the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        # return the frame most recently read
        return True, self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True


def solidity(contour):
    return float(cv2.contourArea(contour)) / float(cv2.contourArea(cv2.convexHull(contour)))

def region_of_interest(img, vertices):
    mask = np.zeros_like(img)

    if len(img.shape) > 2:
        channel_count = img.shape[2]
        ignore_mask_color = (255,) * channel_count
    else:
        ignore_mask_color = 255

    cv2.fillPoly(mask, vertices, ignore_mask_color)

    masked_image = cv2.bitwise_and(img, mask)
    return masked_image

def process_frame(frame):

    min_area = frame.shape[0] * frame.shape[1] * 0.00162
    min_solidity = 0.25

    # y-coord of point directly under the camera
    straight_down = 130

    # color threshold TODO change to white-on-black
    hue = [78, 143]
    sat = [48, 255]
    val = [25, 255]

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, (hue[0], sat[0], val[0]),  (hue[1], sat[1], val[1]))

    # morphological (fill holes/gaps)
    kernel = np.ones((3, 3), np.uint8)
    #mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    #mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    #cv2.imshow("m", mask)

    _, contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # filter based on area and solidity
    contours = list(filter(lambda c: ((cv2.contourArea(c) > min_area) and (solidity(c) > min_solidity)), contours))

    contour = max(contours, key=lambda c: cv2.contourArea(c)) if len(contours) > 0 else None

    if contour is None:
        return (None, None, frame)

    [vx, vy, x, y] = cv2.fitLine(contour, cv2.DIST_L2, 0, 0.01, 0.01)

    #cv2.drawContours(frame, [contour], 0, (0, 255, 0), 3)
    #cv2.line(frame, (0, straight_down), (frame.shape[1] - 1, straight_down), (0, 0, 255), 5)

    pt_x = x + (vx * (straight_down - y) / vy)
    center_x = 360 # (frame.shape[1] / 2.0)

    center_intercept = y + (vy * (center_x - x) / vx)

    """slope = abs(vx / vy)
    slope_sign = -1.0 if center_intercept > straight_down else 1.0
    slope = slope * slope_sign"""
    slope = vx/vy

    horiz_offset = (pt_x - center_x) / center_x

    # draw center point and line
    cv2.circle(frame, (pt_x, straight_down), 8, (255, 255, 0), -1)
    lefty = int((-x * vy / vx) + y)
    righty = int(((frame.shape[1] - x) * vy / vx) + y)
    cv2.line(frame, (frame.shape[1]-1, righty), (0, lefty), (0, 255, 0), 2)

    #cv2.imshow("IMAGE", frame)
    #cv2.waitKey(10)

    return horiz_offset, slope, frame


# Test code
if __name__ == "__main__":
    cap = cv2.VideoCapture(1)
    cap.set(3, 600)
    cap.set(4, 400)

    while True:
        img = cap.read()[1]
        horiz_offset, angle_offset, frame = process_frame(img)
        print(horiz_offset, angle_offset)
        cv2.imshow("FRAME", frame)
        cv2.waitKey(10)
