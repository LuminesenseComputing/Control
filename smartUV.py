""" Main class for top level control.  
"""
# Note:
#   1.   All GPIO pins will follow BCM (Broadcom) convention instead of board convention. 
#   2.  We need confirmState because we need to notify the pyUI when the disinfection is completed.
#   3. Implementation details to check with Chris 
#       - check1 : return value of wifiCommunicator.getState() [list or 1/0 ]?
#       - check2:  usage of checkwifi and start_connections, attemptReconnection
#       - Do I have to touch lightModuleClient??
#----------------------------------------------------------------------------     
# Status:   in progress.
# Last edit: Jordan Hong, 16:00 August 17, 2020 

# Dependency###################################################
## Modules: ultrasonic, PIR, timer classes
## Assumed to have following methods from the above classes
## Ultrasonic
##  - getReadings(): Returns the readings of the ultrasonic sensor. (number in meters)

## PIR 
##  - getReadings(): Returns the readings of the PIR sensor. (True/False)

## Timer
##  - start(): Starts the timer.
##  - timeElapsed(): returns the time elapsed.
##  - stop(): Stops the timer.

## Commander
##  - Connected():  returns if connected with PyUI (True/False)
##  - getState():   returns the state that the commander asserts (1 for lamp on, 0 for lamp off)
##  - confirmState(state): informs the commander of the current lamp state (1/0)
import RPi.GPIO as GPIO
import controlLamp


class smartUV:
    # Declare constants 

    # State constants
    DETECT  = 0
    IDLE    = 1
    INITIAL = 2
    ACTIVE  = 3

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
        self.state = INITIAL    ## state variable
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

        ## DETECT state
        while (self.state == DETECT):
            ## Checks if connected with the PyUI
            self.commander.start_connections(initialStateList)
            # check2 : Check with Chris if code works like this (No return statement from module ??
            connection = self.commander.checkWifi()
            if (connection):
                self.state = IDLE
                break

        ## IDLE state
        while (self.state == IDLE):
            ## Polls commander for ON command
            command = self.commander.getState()
            if (command==1):
                # on receiving ON command to start the UV lamp,
                # Change the state to IDLE
                self.state = INITIAL 
                break

        while (self.state in (INITIAL, ACTIVE) ):
            
            ### Common polling for INITIAL and ACTIVE
            ## Polls for OFF command
            # check1: coordinate return value of getState (now getstate returns a list)
            command = self.commander.getState()
            ## Scans for moving object/human 
            self.seeHuman = self.motionSensor.getReadings()
            ## If sees human or receives off command
            if (self.seeHuman or (self.command==0)):
                self.state = IDLE
                break

            ### Case statements

            ## INITIAL state
            if (self.state==INITIAL):
                ## Initial state, get distance readings and use it calculate UV time parameter
                self.dist   = self.distanceSensor.getReadings()
                self.onTime = controlLamp.distance_to_On_time(self.dist, self.timeTheta)
                self.state = ACTIVE

            ## ACTIVE state
            if (self.state == ACTIVE):
                ## Checks if light is on, 
                ## if off (just transitioned from INITIAL to ACTIVE), turn on
                if (self.lampON==0):
                    self.lamp_turnOn()          ## Turn on lamp
                    self.warning_turnOn()       ## Turn on warning
                    self.timer.start()          ## Starts timer
                    self.commander.confirmState(self.lampON) ## Tells commander that light is turned on

                else:
                    time_elapsed = self.timer.timeElapsed()
                    if (time_elapsed >= self.onTime):
                        ## Time is up
                        self.lamp_turnOff()     ## Turn off lamp
                        self.warning_turnOff()  ## Turn off warning 
                        self.timer.stop()       ## Turn off timer
                        self.commander.confirmState(self.lampON) ## Tells commander that light is off (i.e. disinfection is complete)

            else:
                    ## Wrong state: outputs error (should not occur)
                    print("Wrong state")
                    return False
        return True

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
        
