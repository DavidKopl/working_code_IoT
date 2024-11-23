import sys
sys.path.append('/home/davidkopl/Documents/working_code_IoT/Python')
import time

from DFRobot_PH import DFRobot_PH
ph = DFRobot_PH()

ph.reset()
time.sleep(0.5)
sys.exit(1)