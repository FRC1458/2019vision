import time
from networktables import NetworkTables

import logging
logging.basicConfig(level=logging.DEBUG)

NetworkTables.initialize()
table = NetworkTables.getTable("VisionTable")

table.putBoolean("vision_enabled", False)
table.putNumber("current_camera", 0)

i = 0
while True:
    table.putNumber("time", i)
    time.sleep(1)
    i += 1
