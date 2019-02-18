import cv2
import numpy as np
import time

from threading import Thread

def crop(frame, width, height):
    w, h = frame.shape[1], frame.shape[0]
    ox = int((w - width) / 2)
    oy = int((h - height) / 2)

    return frame[oy:(oy+height), ox:(ox+width)]

class CvSinkThread:
    def __init__(self, cvsink, shape):
        self.stream = cvsink
        self.frame = np.zeros(shape=shape, dtype=np.uint8)
        self.newstream = None
        _, self.frame = self.stream.grabFrame(self.frame)

        Thread(target=self.update, args=()).start()

    def update(self):
        while True:
            if self.newstream is not None:
                self.stream = self.newstream
                self.newstream = None
                print("CHANGING STREAM")

            _, self.frame = self.stream.grabFrameNoTimeout(self.frame)
            time.sleep(0.001)

    def get_frame(self):
        return self.frame.copy()
