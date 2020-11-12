'''
Class for Ultrasonic Sensors to be used for simulations
Status: Complete
By: Bipasha Goyal
Last modified: November 6, 2020
'''
import time 
#from grove_ultrasonic_ranger import *

class Ultrasonic_sim:
    def __init__(self,pin0,pin1,pin2):
        self.dist0 = 0 
        self.dist1 = 0 
        self.dist2 = 0 

    def getReadings(self):
        '''
        #Function called in Main control function.
        #Takes average of readings over a defined time interval. Then averages all readings from all sensors.
        start_time = time.time()
        #seconds = 0.1 #can change time here
        i=0
        dist0_read = []
        dist1_read = []
        dist2_read = []

        while True:
            #elapsed_time = time.time() - start_time

            if i<10: 
            #elapsed_time < seconds:
                dist0_read.append(self.dist0.get_distance())
                dist1_read.append(self.dist1.get_distance())
                dist2_read.append(self.dist2.get_distance()) 
            i=i+1
            if i>10: 
            #elapsed_time >= seconds:
                i=0
                break 
        #print(dist0_read)
        #print(dist1_read)
        #print(dist2_read)

        dist_ave =[sum(dist0_read)/len(dist0_read),sum(dist1_read)/len(dist1_read),sum(dist2_read)/len(dist2_read)]
        dist_final = sum(dist_ave)/len(dist_ave)
        print(dist_final)
        return dist_final
        #return  dist_final = mean([mean(dist0_read),mean(dist1_read),mean(dist2_read)])
        '''
        print ("Scanning")
        distance = 0.5
        return distance 
