#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file capture.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-03-13 12:24


import cv2
import time
import threading
from vmcs.utils.logger import EasyLoggerMP as logger

CAP_RUNNING = 1
CAP_STOPING = 2


class VideoCapture(object):

    def __init__(self, source, name='cam'):
        self.cap = cv2.VideoCapture(source)
        assert self.cap.isOpened()
        self.source = source
        self.name = name
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        self.lock = threading.Lock()
        self.t = threading.Thread(target=self._update, daemon=True)
        self.status = CAP_RUNNING
        self.t.start()

    def set(self, key, value):
        self.cap.set(key, value)

    def get(self, key):
        return self.cap.get(key)

    def _update(self):
        while self.status == CAP_RUNNING:
            with self.lock:
                ret = self.cap.grab()
                if not ret:
                    time.sleep(0.3)
                    # logger.warning('grab empty')
                    # raise RuntimeError(f'{self.source} grab error.')
            time.sleep(0.01) # TODO let other thread get chance to acquire lock
        self.cap.release()

    def read(self):
        with self.lock:
            ret, frame = self.cap.retrieve()
        return ret, frame

    def isOpened(self):
        return self.cap.isOpened()

    def release(self):
        self.status = CAP_STOPING
        time.sleep(0.2)

    def __str__(self):
        def decode_fourcc(v):
            v = int(v)
            return "".join([chr((v >> 8 * i) & 0xFF) for i in range(4)])
        w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        f = int(self.cap.get(cv2.CAP_PROP_FPS))
        c = decode_fourcc(self.cap.get(cv2.CAP_PROP_FOURCC))
        b = int(self.cap.get(cv2.CAP_PROP_BUFFERSIZE))
        return f'{self.name}({self.source}): {w}x{h}/{f} {b} {c}'


if __name__ == "__main__":
    cap = VideoCapture(2)
    if cap.isOpened():
        cap.set(cv2.CAP_PROP_FPS, 10) # XW200: XW200 not work
        ret, frame = cap.read()
        if ret:
            logger.info(frame.shape)
        logger.info(cap)
        cap.release()
