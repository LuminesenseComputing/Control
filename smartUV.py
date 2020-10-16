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
##  - set(time): Configures starting value for count down.
##  - pause():   Pause timer, retains current remaining time.
##  - reset():   Resets timer. This forces remaining time to be -1.
##  - Timer.time: current remaining time


##  wifi 
##  - checkwifi():  Connect with PyUI to update internal memory. 
##  - getState():   Returns list of current state [Connection, wifiState, wifiName, resetTimer]. resetTimer resets timer time to -1 (invalid) and shuts light off imediately.  
##  - confirmState (self.state, self.context): Reports local state variable (ACTIVE or IDLE). Note that INITIAL will not be reported since the state is just intermediate and only effective in one cycle. 

import RPi.GPIO as GPIO
import controlLamp


class smartUV:
    # Declare constants 

    # State constants
    IDLE    = 0
    ACTIVE  = 1
    INITIAL = 2

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


    ## GPIO in board mode 
    ### Output
    #GPIO_warning    = 31
    #GPIO_lamp       = 37
    ### Input
    #GPIO_PIR0       = 21
    #GPIO_PIR1       = 23
    #GPIO_PIR2       = 29

    #GPIO_DIST0      = 33
    #GPIO_DIST1      = 35
    #GPIO_DIST2      = 32


    initialStateList = [["OFF", "lightName", 0]]

    # wifiComm = multiconnClientClass2.wifiCommunicator(sel, initialStateList)



    def __init__(self):

        # Declare parameters
        self.lampON = 0
        self.state = DETECT    ## state variable
        self.dist = 0           ## distance in cm, measured from self.distanceSensor
        self.onTime = 0         ## Time calculated by optical parameters
        self.timeTheta = [320.25, -76.859, 444.6, -72.298]
        self.seeHuman = False   ## boolean to indicate whether human is detected

        self.setup_GPIO()       # Setup GPIO

        # Initialize utility classes with respective GPIO pins
        #self.distanceSensor = Ultrasonic(GPIO_DIST0, GPIO_DIST1, GPIO_DIST2)
        #self.motionSensor   = PIR(GPIO_PIR0, GPIO_PIR1, GPIO_PIR2)
        #self.timer          = Timer()
        ## Integration with Chris' code
        #self.commander      = multiconnClientClass2.wifiCommunicator(sel, initialStateList)
    
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

        return 0
    
    #------------------- Raspberry PI GPIO Functions ----------------------------------#
    def setup_GPIO(self);
        """ Setup the GPIO pins that is interfaced directly here.
            Ignores the grove library pins, only set up GPIO pins for warnings and UV lamp power control
        """
       
        # Set board pin numbering system as BCM  
        GPIO.setmode(GPIO.BCM)

        # Set pin mode for warning and lamps as write
        GPIO.setup(GPIO_warning, GPIO.out)
        GPIO.setup(GPIO_lamp, GPIO.out)

        return True

    def lamp_turnOn(self);
        """ Turns lamp on 
        """
        GPIO.output(GPIO_lamp, GPIO.HIGH)
        self.lampON = 1
        return True

    def lamp_turnOff(self):
        """ Turns lamp off
        """
        GPIO.output(GPIO_lamp, GPIO.LOW)
        self.lampON = 0
        return True
        
    def warning_turnOn(self):
        """ Turns warning on
        """
        GPIO.output(GPIO_warning, GPIO.HIGH)
        return True
    
    def warning_turnOff(self):
        """ Turns warning off
        """
        GPIO.output(GPIO_warning, GPIO.LOW)
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
        self.timer.set(self.onTime)

        # Detect human
        self.seeHuman = self.motionSensor.getReadings()

        return 0

    def state_ACTIVE(self):
        """
        State when UV light emitting
        """
        
        # Detect human
        self.seeHuman = self.motionSensor.getReadings()

        # Turn on lamp if currently off
        if (self.lampON==0):
            self.lamp_turnOn()      # Turns lamp off
            self.warning_turnOn()   # Turns warning off
            self.timer.start()

        else if (self.timer.time==0):
            # Time up
            self.state = IDLE       # Change next state, prepare to turn off next cycle
            self.context = DUE 

        if (self.seeHuman):
            self.state = IDLE       # If human detect, go to IDLE
            self.context = HUMAN

        return 0

    def pre_cycle(self):
        """ 
        Check WIFI and update from wifi.
        """
        Connection = False
        wifiState  = 0
        wifiName = "Test"
        resetTimer = True

        # Check connection
        self.wifi.checkwifi() # This updates the internal memory

        # Fetch updated data from checkwifi()
        (Connection, wifiState, wifiName, resetTimer) = self.wifi.getState()

        if (Connection==True):
            # Only change state when there is a connection
            if (wifiState==1):
                if (self.lampON==0 and self.timer.time==-1):
                    # Lamp off and timer not set
                    state = INITIAL
                else:
                    # Lamp off and timer was set:
                    # Resume disinfection
                    state = ACTIVE
            else:
                state = IDLE
                if (self.lampON==1):
                    self.context = PAUSED   # Update context for off


            if (resetTimer==True):
                # Reset time should be effective whether lamp on (turn off, reset time), 
                # or lamp off (simply reset time to -1)
                state = IDLE
                self.timer.reset()  # Resets timer time to -1


        return 0


    def post_cycle(self):
        if (self.state==ACTIVE):
            # Report time as context
            self.context = self.timer.time
        self.wifi.confirmState(self.state, self.context)
        
        return 0




