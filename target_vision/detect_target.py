import cv2
import math
import numpy as np

# Config parameters
HUE = (31, 130)
#SAT = (44, 197)
SAT = (44, 255)
VAL = (161, 255)

def getRotation(contour):
    # This entire function borrowed from 3997 repo
    def translateRotation(rotation, width, height):
        if (width < height):
            rotation = -1 * (rotation - 90)
        if (rotation > 90):
            rotation = -1 * (rotation - 180)
            rotation *= -1
        return round(rotation)

    try:
        ellipse = cv2.fitEllipse(contour)
        centerE = ellipse[0]
        rotation = ellipse[2]
        widthE = ellipse[1][0]
        heightE = ellipse[1][1]
        rotation = translateRotation(rotation, widthE, heightE)
        return rotation
    except:
        rect = cv2.minAreaRect(contour)
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        center = rect[0]
        rotation = rect[2]
        width = rect[1][0]
        height = rect[1][1]
        rotation = translateRotation(rotation, width, height)
        return rotation

def contains(a, minVal, maxVal):
    return (a > minVal and a < maxVal)

def avg(a, b): # average two values
    return int((float(a) + float(b)) / 2.0)

def detect_target(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, (HUE[0], SAT[0], VAL[0]), (HUE[1], SAT[1], VAL[1]))
    _, contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_TC89_KCOS)

    if len(contours) < 2:
        return None, None

    contours = sorted(contours, key=lambda x: cv2.contourArea(x), reverse=True)

    final = []

    for c in contours:
        M = cv2.moments(c)
        hull = cv2.convexHull(c)
        area = cv2.contourArea(c)
        hullArea = cv2.contourArea(hull)

        if (float(area) < 0.15 * frame.shape[1]): # min size
            continue

        if (float(area) / float(hullArea)) < 0.5: # solidity
            continue

        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
        else:
            cx, cy = 0, 0

        if cy < 0.3 * frame.shape[0]:
            continue


        if len(final) >= 6:
            continue

        rotation = getRotation(c)

        if abs(rotation) < 20:
            continue

        rect = cv2.minAreaRect(c)
        box = cv2.boxPoints(rect)
        box = np.int0(box)

        left_color = (240, 120, 0)
        right_color = (50, 50, 240)

        color = left_color if rotation > 0 else right_color

        cv2.drawContours(frame, [box], 0, color, 2)
        cv2.circle(frame, (cx, cy), 8, color, -1)

        #              0   1     2      3      4            5
        final.append([cx, cy, rotation, c, float(0.0), rotation > 0])

    if len(final) < 2:
        return None, None

    final = sorted(final, key=lambda x: x[0])
    pairs = []

    for i in range(len(final)):
        c = final[i]

        if c[5] == False: # skip if right side
            continue

        # find the closest to the left
        r = i+1
        if r >= len(final):
            continue
        nearest = final[r]
        if nearest[5] == True: # skip if it is also a left side (shouldn't happen usually)
            continue
            #r += 1
            #if r >= len(final):
            #    continue
            #nearest = final[r]

        if abs(nearest[1] - c[1]) > 120:
            continue

        xvalue = avg(c[0], nearest[0])
        pair = [xvalue, avg(c[1], nearest[1]), c, nearest, abs((frame.shape[1] / 2.0) - xvalue)]

        # draw center point
        cv2.circle(frame, (pair[0], pair[1]), 8, (100, 200, 100), -1)

        pairs.append(pair)

    if len(pairs) < 1:
        return None, None

    pairs = sorted(pairs, key=lambda x: x[4])
    finalPair = pairs[0]


    angle = 0.0

    center = finalPair[0]
    cv2.line(frame, (center, 20), (center, frame.shape[0] - 20), (23, 4, 190), 3)
    a = ((center / float(frame.shape[1])) - 0.5) * 2.0

    return a, angle




