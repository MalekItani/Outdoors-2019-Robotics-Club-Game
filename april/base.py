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
import pyautogui


demo_searchpath = [os.path.join(os.path.dirname(__file__), '../build/lib'),os.path.join(os.getcwd(), '../build/lib')]
det = ap.Detector(searchpath=demo_searchpath)

def detect_and_locate_position(img):
    detections, dimg = det.detect(img, return_image = True)
    if len(detections) > 0:
        return tuple(detections[0].center.astype(np.uint32)), img
    return None, img


window_height = 768
window_width = 1366

def begin_mouse_control():
    t = Thread(target=_begin_mouse_control)
    t.daemon = True
    t.start()


def _begin_mouse_control():
    x, y = scale(frame, center)
    pyautogui.moveTo(x, y)

def scale(frame, point):
    return (point[0]*window_height/frame.shape[0], point[1]*window_width/frame.shape[1])


def adjust_gamma(image, gamma=1.0):
    table = np.array([((i / 255.0) ** gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
    return cv2.LUT(image, table)


def main():
    config.send_ip()
    stream = ThreadedStream(port=12345).start()
    try:
        frame = None
        while frame is None:
            center, frame, dimg = stream.get()
        while 1:
            center, frame, dimg = stream.get()
            if center is not None:
                frame = cv2.circle(frame, center, 10, (255,0,0), 3)
                x, y = scale(frame, center)
                pyautogui.moveTo(x, y)
            cv2.imshow('Frame', frame)
            if cv2.waitKey(1) & 0xff == ord('q'):
                break
    except Exception as err:
         traceback.print_tb(err.__traceback__)
    finally:
        stream.stop()

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
    # camera = WVS(src=1)
    # time.sleep(1)
    # camera.stream.set(cv2.CAP_PROP_EXPOSURE, 40)
    # camera.start()
    # time.sleep(1)
    camera = cv2.VideoCapture(1)
    # camera.set(3,1280)
    # camera.set(4,1024)
    camera.set(15, 0.1)
    time.sleep(1)
    while 1:
        frame = camera.read()[1]
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        detections, dimg = det.detect(img, return_image = True)
        cv2.imshow('Original', frame)
        cv2.imshow('Detection', dimg)
        if cv2.waitKey(1) & 0xff == ord('q'):
            break
    camera.stop()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # cursor_test()
    apriltag_test()
    # main()
