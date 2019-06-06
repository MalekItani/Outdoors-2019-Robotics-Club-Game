from OpenCVSockets import OpenCVServerSocket as SS
import cv2
from imutils.video import WebcamVideoStream as WVS
import apriltag as ap
import os
import numpy as np
import config
import time
from threading import Thread
import traceback
import config as cfg


demo_searchpath = [os.path.join(os.path.dirname(__file__), '../build/lib'),os.path.join(os.getcwd(), '../build/lib')]
det = ap.Detector(searchpath=demo_searchpath)

def detect_and_locate_position(img):
    detections, dimg = det.detect(img, return_image = True)
    if len(detections) > 0:
        return tuple(detections[0].center.astype(np.uint32)), img
    return None, img

class ThreadedStream(SS):
    def __init__(self, port, chunkSize=2048, numClients=1):
        SS.__init__(self, port, chunkSize=chunkSize, numClients=numClients)
        self.center = None
        self.frame = None
        self.stopped = True
        self.dimg = None
	
    def start(self):
        self.stopped = False
        self.t = Thread(target=self.update)
        self.t.daemon = True
        self.t.start()
        return self

    def get(self):
        return self.center, self.frame, self.dimg

    def update(self, inverted = 1):
        while True:
            try:
                if self.stopped:
                    self.close()
                    return
                # otherwise, read the next frame from the stream
                self.frame = self.receiveFrame(mode=cv2.IMREAD_GRAYSCALE)
                self.center, self.dimg = detect_and_locate_position(self.frame)
                if self.center is not None:
                    if inverted:
                        self.center = (self.center[0], self.frame.shape[0] - self.center[1])
            except Exception as e:
                print(traceback.print_tb(e.__traceback__))

    def stop(self):
        self.stopped = True

    def close(self):
        SS.close(self)
        self.t.kill()


window_height = 1000
window_width = 2000


def scale(frame, point):
    return (point[0]*window_width/frame.shape[1], point[1]*window_height/frame.shape[0])


def begin_mouse_control(cursor):
    t = Thread(target=_begin_mouse_control, args=(cursor,))
    t.daemon = True
    t.start()


def _begin_mouse_control(cursor):
    config.send_ip()
    stream = ThreadedStream(port=12345).start()
    # stream = SS(12345)
    try:
        frame = None
        while frame is None:
            # frame = stream.receiveFrame()
            center, frame, dimg = stream.get()
        while 1:
            
            # frame = stream.receiveFrame()
            center, frame, dimg = stream.get()
            if center is not None:
                # frame = cv2.circle(frame, center, 10, (255,0,0), 3)
                x, y = scale(frame, center)
                # t1 = time.time()
                cursor.center=np.array([window_width - x-250,window_height - y -150])
                # t2 = time.time()
            # cv2.imshow('Frame', frame)
            if cv2.waitKey(1) & 0xff == ord('q'):
                break
    except Exception as err:
         traceback.print_tb(err.__traceback__)
    finally:
        stream.close()


def adjust_gamma(image, gamma=1.0):
    table = np.array([((i / 255.0) ** gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
    return cv2.LUT(image, table)


def main():
    pass

def cursor_test():
    camera = WVS(src=0).start()
    while 1:
        frame = camera.read()
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        center = detect_and_locate_position(img)  # Make sure frame is grayscale
        if center is not None:
            frame = cv2.circle(frame, center, 10, (255,0,0), 1)
            frame = cv2.circle(frame, center, 5, (255,0,0), 1)
        frame = frame[...,::-1]
        cv2.imshow('Frame', frame)
        if cv2.waitKey(1) & 0xff == ord('q'):
            break

def apriltag_test():
    camera = WVS(src=0).start()
    while 1:
        frame = camera.read()
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        detections, dimg = det.detect(img, return_image = True)
        cv2.imshow('Original', frame)
        cv2.imshow('Detection', dimg)
        if cv2.waitKey(1) & 0xff == ord('q'):
            break
    camera.stop()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    #cursor_test()
    #apriltag_test()
    # main()
    _mouse_control()
