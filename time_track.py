import time

class TimeTrack:
    
    # Record the start time.
    # The start time is the time at which the lamp is turned on.
    def __init__(self):
        self.start = int(time.time())

    # Calculate the time elapsed.
    # The time elapsed is the amount of time the lamp has been on.
    def timeElapsed(self):
        current = int(time.time())
        elapsed = current - self.start
        return elapsed

    # Stop the timer and record the total time the lamp has been on in the time_track.txt file.
    def stop(self):
        f = open("time_track.txt", "r+")
        initial = int(f.readline())
        final = initial + self.timeElapsed()
        f.seek(0)
        f.truncate()
        f.write(str(final))
        f.close
