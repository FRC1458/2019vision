import cv2
import numpy as np
import time

from threading import Thread

class CvSinkThread:
    def __init__(self, cvsink, shape):
        self.stream = cvsink
        self.frame = np.zeros(shape=shape, dtype=np.uint8)
        self.newstream = None
        _, self.frame = self.stream.grabFrame(self.frame)

        Thread(target=self.update, args=()).start()

    def update(self):
        print("updating")
        while True:
            if self.newstream is not None:
                self.stream = self.newstream
                self.newstream = None

            _, self.frame = self.stream.grabFrameNoTimeout(self.frame)
            time.sleep(0.001)

    def get_frame(self):
        return self.frame.copy()
