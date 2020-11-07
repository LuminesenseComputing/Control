'''Class for motion sensors
Status: Complete
Made by: Bipasha Goyal
Last modified: 6 November 2020
'''
import time
#from grove_mini_pir_motion_sensor import *

class PIR_sim:
    def __init__(self, pin0, pin1, pin2):
        #self.motion0 = GroveMiniPIRMotionSensor(pin0)
        #self.motion1 = GroveMiniPIRMotionSensor(pin1)
        #self.motion2 = GroveMiniPIRMotionSensor(pin2)

        self.motDet = False
        #def callback():
        #    self.motDet = True
        #self.motion0.on_detect = callback
        #self.motion1.on_detect = callback
        #self.motion2.on_detect = callback

    def setReadings(self):
        self.motDet = True

    def getInput(self):
        human = input('Human detected?[Y if true]')
        if human == 'Y':
            self.motDet = True 

    def getReadings(self):
        # Need to check with Bipasha why there's a while loop here
        if (self.motDet):
            self.motDet = False # clears
            return True
        return False

        #while True:
        #    if self.motDet == True:
        #        self.motDet = False
        #        print('Motion')
        #        time.sleep(1)
        #        #return True
        #    else:
        #        print('No motion')
        #        time.sleep(1)
        #        #return False


