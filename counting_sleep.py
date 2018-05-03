import cv2
import numpy as numpy
import time
import signal
import json
import datetime
from picamera.array import PiRGBArray
from picamera import PiCamera

class SleepTracker():
    def __init__(self, delay_sec=10):
        self.delay = delay_sec
        self.camera = PiCamera()
        self.rawCapture = PiRGBArray(self.camera)
        self.keyframe = None
        self.keyframe_timestamp = None

        self.last_frame = None
        self.frame = None
        self.frame_timestamp = None
        self.running = True

        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self,signum, frame):
        self.running = False

    def run(self):
        self.running = True
        print("Starting Camera...")
        time.sleep(1)

        filename = datetime.datetime.fromtimestamp(time.time()).strftime('logs/%Y_%m_%d_%H:%M:%S.txt')
        print(filename)
        log = open(filename, 'a+')

        buffer = []
        self.updateKeyFrame()
        self.updateFrame()
        
        while self.running:
            self.updateFrame()
            if self.isIterationDone():
                #print(json.dumps(buffer))
                log.write(json.dumps(buffer))
                log.write("\n")
                buffer = []
                self.updateKeyFrame()
                #print("keyframe")
            else:
                last_diff_sum, diff_sum = self.compareImages()
                buffer.append({"time":str(int(self.frame_timestamp)), "last_frame_diff": str(last_diff_sum), "keyframe_diff": str(diff_sum)})
                #print(diff_sum)
                time.sleep(1)
        log.close()
        print("Exited Gracefully")


    def updateKeyFrame(self):
        self.keyframe = self.getImage()
        self.keyframe_timestamp = time.time()

    def updateFrame(self):
        self.last_frame = self.frame
        self.frame = self.getImage()
        self.frame_timestamp = time.time()

    def getImage(self):
        self.camera.capture(self.rawCapture, format="bgr")
        image = self.rawCapture.array
        self.rawCapture.truncate(0)
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    def isIterationDone(self):
        return (self.frame_timestamp - self.keyframe_timestamp > self.delay)

    def compareImages(self):
        last_diff = cv2.absdiff(self.last_frame, self.frame)
        last_diff_sum = last_diff.sum()
        diff = cv2.absdiff(self.keyframe, self.frame)
        diff_sum = diff.sum()
        return last_diff_sum, diff_sum



if __name__=="__main__":
    
    sleep_tracker = SleepTracker()
    sleep_tracker.run()


