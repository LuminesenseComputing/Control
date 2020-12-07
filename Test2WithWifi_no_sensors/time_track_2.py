import time

class TimeTrack:
    
    # Record the start time.
    # The start time is the time at which the lamp is turned on.
    def __init__(self):
        self.active = False
        self.start = 0
        self.count = 0
        self.period = -1 
        self.TO = False

    def setPeriod(self, period):
        self.period= int(period)
        print ("Set period to ", self.period)
        return 0

    def startTimer(self):
        self.active = True 
        self.start = int(time.time())
        print ("starting timer")
        return 0

    def check(self):
        if (self.active):
            curr = int (time.time())
            # print ("Current time is: ", curr)
            self.count = self.period - (curr - self.start)
            print ("Current time is: ", self.count)
            self.TO = (self.count<=0)
        if (self.TO):
            self.active = False
        return 0

    def reset(self):
        self.count = 0
        self.period = -1
        self.TO = False
        print ("resetting timer")
        return 0

    def isSet(self):
        return not (self.period==-1)

    def pause(self):
        self.active = False
        self.period = self.count



if __name__ == "__main__":

    myTimer = TimeTrack()
    myTimer.setPeriod(10)
    myTimer.startTimer()
    pause_count = 0

    while (not myTimer.TO):
        myTimer.check()
        print(myTimer.count)
        time.sleep(1)
        #if (myTimer.count==5):
        #    myTimer.reset()

        if (myTimer.active and myTimer.count==5 and pause_count==0):
            myTimer.pause()
        if not (myTimer.active):
            print ("timer paused")
            pause_count += 1
            if (pause_count >= 5):
                print ("starting timer ...")
                myTimer.startTimer()
    print("Timeout, exiting...")

