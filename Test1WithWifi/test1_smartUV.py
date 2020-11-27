""" Main class for top level control.  
"""
# Note:
#   1.  All GPIO pins will follow BCM (Broadcom) convention instead of board convention. 
#   2.  Note to hardware test: Current program cannot run. Still need to integrate in other program classes.                         
#   3.  Note to self: Add in proxy functions to test state machine.
#----------------------------------------------------------------------------     
# Status:   in progress.
# Last edit: Jordan Hong, 17:10  October 12, 2020  (Updated for integration and refactoting. Todo: proxy functions and confirm with team)

# Dependency###################################################
## Modules: ultrasonic, PIR, timer classes
## Assumed to have following methods from the above classes

## Ultrasonic
##  - getReadings(): Returns the readings of the ultrasonic sensor. (number in meters)

## PIR 
##  - getReadings(): Returns the readings of the PIR sensor. (True/False)

## Timer: count down timer
##  - set(time):        Configures starting value for count down.
##  - pause():          Pause timer, retains current remaining time.
##  - reset():          Resets timer. This forces remaining time to be -1.
##  - Timer.check():    Updates TO flag.
##  - Timer.isSet():    Returns whether timer is set to a value. (Could return something like: not time==-1.
##  - Timer.TO:         Timeout flag. True when time=0. Reset to False. 


import selectors
import RPi.GPIO as GPIO
import controlLamp
from time_track_2 import *
from motion_sensor_3 import *
from ultrasonic_sensor_3 import *
import multiconnClientClass2

'''
# State constants
IDLE    = 0
ACTIVE  = 1
INITIAL = 2
DETECT  = 3
TIMER   = 4
HUMAN   = 5
'''
# State constants
IDLE    = "IDLE"
ACTIVE  = "ACTIVE"
INITIAL = "INITIAL"
DETECT  = "DETECT"
TIMER   = "TIMER"
HUMAN   = "MOTION"


# GPIO in BCM mode 
## Output
GPIO_warning    = 6 
GPIO_lamp       = 26 
## Input
GPIO_PIR0       = 9 
GPIO_PIR1       = 11 
GPIO_PIR2       = 5

GPIO_DIST0      = 13
GPIO_DIST1      = 19
GPIO_DIST2      = 12


#set up selector variable for wifi
sel = selectors.DefaultSelector()



class sim_smartUV:

    def __init__(self):

        # Declare parameters
        self.lampON = 0
        self.state = DETECT    ## state variable
        self.dist = 0           ## distance in cm, measured from self.distanceSensor
        self.onTime = 0         ## Time calculated by optical parameters
        self.timeTheta = [320.25, -76.859, 444.6, -72.298]
        self.seeHuman = False   ## boolean to indicate whether human is detected
        #Declare wifi parameters
        self.wifiName = "defaultName"
        self.wifi = None

        self.setup_GPIO()       # Setup GPIO

        # Initialize utility classes with respective GPIO pins
        self.distanceSensor = Ultrasonic(GPIO_DIST0, GPIO_DIST1, GPIO_DIST2)
        self.motionSensor   = PIR(GPIO_PIR0, GPIO_PIR1, GPIO_PIR2)
        self.timer          = TimeTrack()
        self.context        = IDLE
    
    def main(self):
        """ Main function to loop through when system is not in IDLE state.
        """
        while True:
            self.pre_cycle()    # Check connection and update information from PyUI
            
            if (self.state==IDLE):
                self.state_IDLE()
            elif (self.state==INITIAL):
                self.state_INITIAL()
            elif (self.state==ACTIVE):
                self.state_ACTIVE()

            self.post_cycle()   # Confirms state and context with PyUI
            self.print_state()
            time.sleep(1)

        return 0
    
    #------------------- Raspberry PI GPIO Functions ----------------------------------#
    def setup_GPIO(self):
        """ Setup the GPIO pins that is interfaced directly here.
            Ignores the grove library pins, only set up GPIO pins for warnings and UV lamp power control
        """
       
        # Set board pin numbering system as BCM  
        GPIO.setmode(GPIO.BCM)

        # Set pin mode for warning and lamps as write
        GPIO.setup(GPIO_warning, GPIO.out)
        GPIO.setup(GPIO_lamp, GPIO.out)

        print ("Setting up GPIO")

        return True

    def lamp_turnOn(self):
        """ Turns lamp on 
        """
        GPIO.output(GPIO_lamp, GPIO.HIGH)
        print ("Turning lamp ON")
        self.lampON = 1
        return True

    def lamp_turnOff(self):
        """ Turns lamp off
        """
        GPIO.output(GPIO_lamp, GPIO.LOW)
        print ("Turning lamp off")
        self.lampON = 0
        return True
        
    def warning_turnOn(self):
        """ Turns warning on
        """
        GPIO.output(GPIO_warning, GPIO.HIGH)
        print ("Turning warning light on")
        return True
    
    def warning_turnOff(self):
        """ Turns warning off
        """
        GPIO.output(GPIO_warning, GPIO.LOW)
        print ("Turning warning light off")
        return True

    #------------------- State Machine Functions ----------------------------------#
    def state_IDLE(self):
        """
        State when light is off.
        """

        if (self.lampON==1):
            self.lamp_turnOff()      # Turns lamp off
            self.warning_turnOff()   # Turns warning off
            self.timer.pause()
        return 0

    def state_INITIAL(self):
        """
        Initial state prior to emitting UV.
        Scans distance and compute disinfection time.
        """
        # Get distance 
        self.dist   = self.distanceSensor.getReadings() 
        # Calculate onTime
        self.onTime = controlLamp.distance_to_On_time(self.dist, self.timeTheta)

       
        # Configure next state to ACTIVE
        self.state = ACTIVE
        # Set timer
        self.onTime=10 #TODO: remove this, just for simulation
        self.timer.setPeriod(self.onTime)


        return 0

    def state_ACTIVE(self):
        """
        State when UV light emitting
        """
        # check timer 
        self.timer.check()

        # Turn on lamp if currently off
        if (self.lampON==0):
            self.lamp_turnOn()      # Turns lamp off
            self.warning_turnOn()   # Turns warning off
            self.timer.startTimer()
            self.context = ACTIVE

        elif (self.timer.TO):
            # Time up
            print ("Time is up!")
            self.state = IDLE     
            self.state_IDLE()

        return 0

    def pre_cycle(self):
        """ 
        Check WIFI and update from wifi.
        """
        '''
        if (self.state==DETECT):
            print ("Connected")
            self.state=IDLE
        '''
        if (self.state==DETECT):
            #initialize wifi
            #initialStateList is in the format [initial actualState, actualName, actualCurrentTime]
            self.state=IDLE
            if self.state == ACTIVE:
                initialStateList = ["ON", self.wifiName, 0]
            else:
                initialStateList = ["OFF", self.wifiName, 0]                

            self.wifi = multiconnClientClass2.wifiCommunicator(sel, initialStateList)
            print ("Connected")

        if (self.state==IDLE):
            #wifistate = int (input("State IDLE, turn on? [1/0]?"))
            #if (wifistate==1):
            #    self.state = INITIAL
            pass




        # Connection = False 
        # wifiState  = 0
        # resetTimer = True
        
        #---------- Simulation only ----------------#
        #Connection = True 
        #wifiState  = 1
        #wifiName = "Test"
        #resetTimer = False
        #-------------------------------------------#

        # Check connection
        self.wifi.checkWifi() # This updates the internal memory

        # Fetch updated data from checkwifi()
        (Connection, wifiState, self.wifiName, resetTimer) = self.wifi.getState()

        if (Connection=="CONNECTED"):
            # Only change state when there is a connection
            if (wifiState=="ON"):
                print ("Connection true, lampON: ", self.lampON)
                if (self.lampON==0 and self.timer.period==-1):
                    # Lamp off and timer not set
                    self.state = INITIAL
                else:
                    # Lamp off and timer was set:
                    # Resume disinfection
                    self.state = ACTIVE
            else:
                self.state = IDLE

            if (resetTimer==True):
                # Reset time should be effective whether lamp on (turn off, reset time), 
                # or lamp off (simply reset time to -1)
                self.state = IDLE
                self.timer.reset()  # Resets timer time to -1
        else:
            self.state = IDLE
            print("Not connected to base station.")


        # Detect human
        self.seeHuman = self.motionSensor.getReadings()
        if (self.seeHuman):
            self.state = IDLE       # If human detect, go to IDLE


        return 0


    def post_cycle(self):
        if (self.state==IDLE):
            # If OFF 
            self.context = IDLE
            
            if (self.timer.TO):
                # Time out
                self.context = TIMER

                # clear timer
                print ("Timer resetting")
                self.timer.reset()

            elif self.seeHuman:
                self.context = HUMAN
            
        # self.wifi.confirmState(self.state, self.context)
        if self.state == ACTIVE:    
            self.wifi.confirmState("ON", self.wifiName, None, self.context)
        else:
            self.wifi.confirmState("OFF", self.wifiName, None, self.context)

        return 0


    #------------------- Simlulation only----------------------------------------#
    def sim_input(self):
        #self.motionSensor.getInput()#was only for simulation purposes
        pass

    def print_state(self):
        # Print the state of UV lamp
        state_map = ["IDLE", "ACTIVE",  "INITIAL", "DETECT", "TIMER", "HUMAN"]
        #if not (self.context==IDLE):
        #print (state_map[self.state], state_map[self.context])
        print (self.state, self.context)


if __name__ == "__main__":
    mySmartUV = sim_smartUV()
    mySmartUV.main()
