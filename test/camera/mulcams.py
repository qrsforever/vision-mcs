#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file mulcams.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-03-13 16:01


import cv2
import os
import threading
import time # noqa

from copy import deepcopy
from vmcs.core.camera import VideoCapture
from vmcs.utils.shell import utils_syscall, utils_mkdir
from vmcs.utils.logger import EasyLogger as logger
from vmcs.utils.timer import TimerCycle


# from raspberry.relaylam import test_relaylam_open, test_relaylam_close
# from raspberry.freqled import test_freqled_open, test_freqled_close
# from raspberry.eventele import test_ele_event


if __name__ == "__main__":
    # 通过USB-Hub定位相机编号(暂时没有获取相机的UID方法)
    # XW200: XW200 (usb-0000:00:14.0-5.1):
    # 	/dev/video0
    # 	/dev/video1
    # 	/dev/media0
    results = utils_syscall('v4l2-ctl --list-devices')
    logger.info(results)
    cameras = {}
    curridx = 0 
    flag = False
    for line in results.split('\n'):
        if 'XW200' in line:
            # curridx = int(line[line.rfind('.') + 1: -2])
            curridx += 1
            flag = True
        elif '/dev/' in line and flag:
            if curridx not in cameras.keys():
                cameras[curridx] = line.strip()
                if len(cameras) == 4:
                    break
        else:
            flag = False
    logger.info(cameras)
    vcaps = {}
    for idx, source in cameras.items():
        cam = 'cam%d' % idx
        cap = VideoCapture(source, cam)
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        cap.set(cv2.CAP_PROP_FPS, 10) # TODO XW200 not work for < 30
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920) # v4l2-ctl --device=/dev/video0 --list-formats-ext
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        vcaps[cam] = cap
        utils_mkdir('./out/%s' % cam)

    for cap in vcaps.values():
        logger.info(cap)

    class RecInfo:
        count = 0
        frames = {}
        lock = threading.Lock()

    rec = RecInfo

    def _save_images(channel):
        # test_relaylam_open()
        with rec.lock:
            _frames = deepcopy(rec.frames)
        img = (1 + time.time()) * 1e9
        for name, frame in _frames.items():
            cv2.imwrite('./out/%s/%d.png' % (name, img), frame)
        rec.count += 1
        # test_relaylam_close()
        logger.info(f'{os.getpid()}-{threading.currentThread().ident}: save [{rec.count}]')

    timer = TimerCycle(2.0, _save_images, args=(0,))
    timer.start()
    # test_ele_event(_save_images)
    # test_freqled_open(1000, 90)
    while True:
        _frames = {}
        for cam, cap in vcaps.items():
            ret, frame = cap.read()
            if ret:
                _frames[cam] = frame
        with rec.lock:
            rec.frames = _frames

        for name, frame in _frames.items():
            cv2.imshow(name, frame)

        key = cv2.waitKey(10) & 0xFF
        if key == ord('s'):
            img = (1 + time.time()) * 1e9
            for name, frame in _frames.items():
                cv2.imwrite('./out/%s/%d.png' % (name, img), frame)
                rec.count += 1
        elif key == ord('q'):
            logger.info(f'{os.getpid()}-{threading.current_thread().ident}: quit')
            break

    for cap in vcaps.values():
        cap.release()
    cv2.destroyAllWindows()
    timer.cancel()
    # test_freqled_close()

# multical calibrate --name calibration --output_path . --image_path . --boards aprilgrid_6x6.yaml
# --fix_aspect --allow_skew --distortion_model standard --motion_model rolling --num_threads 6 --seed 666
# --iter 100 --loss linear --outlier_quantile 0.65 --outlier_threshold 5.0
