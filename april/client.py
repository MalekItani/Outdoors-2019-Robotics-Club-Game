from OpenCVSockets import OpenCVClientSocket as CS
import cv2
from imutils.video import VideoStream as VS
import numpy as np
import time


host = '127.0.0.1'  # TODO: Change this

def test():
    cam = VS(usePiCamera=0)
    cam.stream.stream.set(cv2.CAP_PROP_FPS, 32)
    cam.start()
    time.sleep(1)
    while 1:
        frame = cam.read()
        # print(frame)
        cv2.imshow('Frame', frame)
        if cv2.waitKey(1) & 0xff == ord('q'):
            break
    camera.stop()
    cv2.destroyAllWindows()

def main():
    cam = VS(usePiCamera=0)
    cam.stream.stream.set(cv2.CAP_PROP_FPS, 90)
    # print(cam.stream.camera._get_shutter_speed())
    # cam.stream.camera._set_shutter_speed(2000) # Take an image once every 2ms
    cam.start()
    stream = CS(host=host, port=12345)
    while 1:
        frame = cam.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # TODO: Find a way to get Grayscale images directly from PiCam
        stream.sendFrame(frame)
        if cv2.waitKey(1) & 0xff == ord('q'):
            break
    camera.stop()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    # main()
    test()
