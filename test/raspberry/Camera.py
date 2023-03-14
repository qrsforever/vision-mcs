#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file Camera.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-02-16 20:11

import cv2
import threading
import subprocess


# v4l2-ctl -d /dev/video0 -l

NAME_TO_FLAG = {
    "brightness": "cv2.CAP_PROP_BRIGHTNESS",
    "contrast": "cv2.CAP_PROP_CONTRAST",
    "saturation": "cv2.CAP_PROP_SATURATION",
    "hue": "cv2.CAP_PROP_HUE",
    "white_balance_temperature_auto": "cv2.CAP_PROP_AUTO_WB",
    "gain": "cv2.CAP_PROP_GAIN",
    "exposure_auto": "cv2.CAP_PROP_AUTO_EXPOSURE",
    "exposure_absolute": "cv2.CAP_PROP_EXPOSURE",
}

#                      brightness 0x00980900 (int)    : min=-64 max=64 step=1 default=0 value=1
#                        contrast 0x00980901 (int)    : min=0 max=95 step=1 default=32 value=40
#                      saturation 0x00980902 (int)    : min=0 max=128 step=1 default=64 value=50
#                             hue 0x00980903 (int)    : min=-64 max=64 step=1 default=0 value=50
#  white_balance_temperature_auto 0x0098090c (bool)   : default=1 value=1
#                           gamma 0x00980910 (int)    : min=100 max=300 step=1 default=100 value=100
#                            gain 0x00980913 (int)    : min=0 max=100 step=1 default=0 value=60
#            power_line_frequency 0x00980918 (menu)   : min=0 max=2 default=1 value=1
#       white_balance_temperature 0x0098091a (int)    : min=2800 max=6500 step=1 default=4600 value=4600 flags=inactive
#                       sharpness 0x0098091b (int)    : min=1 max=7 step=1 default=2 value=2
#          backlight_compensation 0x0098091c (int)    : min=0 max=3 step=1 default=1 value=1
#                   exposure_auto 0x009a0901 (menu)   : min=0 max=3 default=3 value=1
#               exposure_absolute 0x009a0902 (int)    : min=1 max=5000 step=1 default=157 value=120
#          exposure_auto_priority 0x009a0903 (bool)   : default=0 value=1
# ]


class Camera(object):
    def __init__(self, source, resolution=(640, 480)):
        self._source = source
        self._capture = None
        self.is_running = False
        self.width, self.height = resolution
        self.grabbed, self.frame = False, None
        self.read_lock, self.read_thread = threading.Lock(), None
        self.properties = {}

    def parse_ctrls(self):
        ret = subprocess.Popen(
                f'v4l2-ctl --device /dev/video{self._source} --list-ctrls',
                shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
        if not ret.returncode:
            for line in ret.stdout.readlines():
                p, q = line.split(':')
                p, q = p.strip(), q.strip()
                psegs = p.split(' ')
                qsegs = q.split(' ')
                props = {'min': 0, 'max': 1, 'step': 1}
                if psegs[-1] == '(int)':
                    for i, name in enumerate(['min', 'max', 'step', 'default', 'value']):
                        props[name] = int(qsegs[i].split('=')[1])
                elif psegs[-1] == '(menu)':
                    for i, name in enumerate(['min', 'max', 'default', 'value']):
                        props[name] = int(qsegs[i].split('=')[1])
                else: # bool
                    props['default'] = int(qsegs[0].split('=')[1])
                    props['value'] = int(qsegs[1].split('=')[1])
                self.properties[psegs[0]] = props

    def set(self, key, value):
        try:
            cmd = f'v4l2-ctl --device /dev/video{self._source} --set-ctrl {key}={value}'
            print(cmd)
            subprocess.check_output(cmd, shell=True).strip().decode()
        except subprocess.CalledProcessError:
            return None

    def get(self, key):
        try:
            cmd = f'v4l2-ctl --device /dev/video{self._source} --get-ctrl {key}'
            print(cmd)
            return subprocess.check_output(cmd, shell=True).strip().decode()
        except subprocess.CalledProcessError:
            return None

    def start(self):
        if self.is_running:
            return
        self.grabbed, self.frame = self._capture.read()
        if self.grabbed:
            self.is_running = True
            self.read_thread = threading.Thread(target=self._update_frame)
            self.read_thread.start()

    def stop(self):
        if self.is_running:
            self.is_running = False
            if self._capture:
                self._capture.release()
            if self.read_thread:
                self.read_thread.join()
        self._capture, self.read_thread = None, None

    def _update_frame(self):
        while self.is_running:
            grabbed, frame = self._capture.read()
            with self.read_lock:
                self.grabbed = grabbed
                self.frame = frame

    def read(self):
        with self.read_lock:
            grabbed = self.grabbed
            frame = self.frame.copy()
        return grabbed, frame

    def open(self):
        _capture = cv2.VideoCapture(self._source)
        if not _capture.isOpened():
            raise RuntimeError(f'Cannot open {self._source}')

        _capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        _capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        _capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M','J','P','G')) # solve: read/grab block
        _capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        self.width = int(_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = int(_capture.get(cv2.CAP_PROP_FPS))

        self._capture = _capture
        self.start()
        return self._capture.read()[1].shape

    def close(self):
        self.stop()

    def info(self):
        print(self.properties)


if __name__ == "__main__":
    camera = Camera(0)
    camera.parse_ctrls()
    camera.info()
    camera.open()

    wintitle = 'test'
    cv2.namedWindow(wintitle)
    for key, args in camera.properties.items():
        cv2.createTrackbar(key, wintitle, args['value'], args['max'], lambda v, k=key: camera.set(k, v))
        cv2.setTrackbarMin(key, wintitle, args['min'])
        #  cv2.setTrackbarPos(key, wintitle, args['default'])
    try:
        while True:
            ret, frame = camera.read()
            if ret:
                cv2.imshow(wintitle, frame)
            key = cv2.waitKey(2)
            if key & 0xFF == ord('q') or key & 0xFF == 27:
                break

    except KeyboardInterrupt:
        pass
    finally:
        camera.close()
        cv2.destroyAllWindows()
