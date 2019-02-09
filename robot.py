import cv2

from pycreate2 import Create2
import time

from ground_line import process_frame, WebcamVideoStream

bot = Create2("/dev/ttyUSB0")
bot.start()
bot.full()
bot.drive_direct(0.2, 0.2)

time.sleep(5)

"""cap = cv2.VideoCapture(1)
cap.set(3, 600)
cap.set(4, 400)"""
cap = WebcamVideoStream(src=1, size=(600, 400))
cap.start()

while True:
    img = cap.read()[1]
    horiz_offset, angle_offset = process_frame(img)

    s = bot.get_sensors().bumps_wheeldrops
    if s.bump_left or s.bump_right:
        bot.drive_direct(0.0, 0.0)
        break

    if horiz_offset is None:
        bot.drive_direct(0.0, 0.0)
        continue

    horiz_offset = horiz_offset[0]
    angle_offset = angle_offset[0]

    scale = 500

    speed = 0.8

    KP = -0.9
    KD = 0.4

    steer = KP * horiz_offset + KD * angle_offset
    print(steer)
    bot.drive_direct(scale * (speed + steer), scale * (speed - steer))
    time.sleep(0.05)

cap.stop()
