import time
from networktables import NetworkTables

import logging
logging.basicConfig(level=logging.DEBUG)

NetworkTables.initialize()
table = NetworkTables.getTable("VisionTable")

table.putBoolean("vision_enabled", False)
table.putNumber("current_camera", 0)
table.putBoolean("defense_timer", False)

table.putNumber("pressure_psi", 80)

while True:
    x = input("? ")
    if x == "c0":
        table.putNumber("current_camera", 0)
    if x == "c1":
        table.putNumber("current_camera", 1)
    if x == "c2":
        table.putNumber("current_camera", 2)

    if x == "vo":
        table.putBoolean("vision_enabled", True)
    if x == "vx":
        table.putBoolean("vision_enabled", False)

    if x == "do":
        table.putBoolean("defense_timer", True)
    if x == "dx":
        table.putBoolean("defense_timer", False)

    if x[0] == "p":
        table.putNumber("pressure_psi", int(x[1:]))
