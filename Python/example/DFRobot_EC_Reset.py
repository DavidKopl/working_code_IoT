#This example ues to reset ecdata.txt to default value
import sys
sys.path.append('/home/davidkopl/Documents/working_code_IoT/Python')
import time

from DFRobot_EC import DFRobot_EC
ec = DFRobot_EC()

ec.reset()
time.sleep(0.5)
sys.exit(1)