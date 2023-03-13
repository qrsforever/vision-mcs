#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file mulcams.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-03-13 16:01


import cv2
import time # noqa
from vmcs.core.camera import VideoCapture
from vmcs.utils.shell import utils_syscall
from vmcs.utils.logger import EasyLogger as logger


if __name__ == "__main__":
    # 通过USB-Hub定位相机编号(暂时没有获取相机的UID方法)
    # XW200: XW200 (usb-0000:00:14.0-5.1):
    # 	/dev/video0
    # 	/dev/video1
    # 	/dev/media0
    results = utils_syscall('v4l2-ctl --list-devices')
    cameras = {}
    curridx = -1
    for line in results.split('\n'):
        if 'XW200' in line:
            curridx = int(line[line.rfind('.') + 1: -2])
        elif '/dev/' in line and curridx > 0:
            if curridx not in cameras.keys():
                cameras[curridx] = line.strip()
                if len(cameras) == 4:
                    break
        else:
            curridx = -1
    logger.info(cameras)

    vcaps = {}
    for idx, source in cameras.items():
        cam = 'cam-%d' % idx
        cap = VideoCapture(source, cam)
        # cap.set(cv2.CAP_PROP_FPS, 10) # TODO XW200 not work
        # cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        vcaps[cam] = cap

    for cap in vcaps.values():
        logger.info(cap)

    while True:
        frames = {}
        for cam, cap in vcaps.items():
            ret, frame = cap.read()
            if ret:
                frames[cam] = frame
                cv2.imshow(cam, frame)
        key = cv2.waitKey(10) & 0xFF
        if key == ord('s'):
            for name, frame in frames.items():
                cv2.imwrite(f'./out/{name}.jpg', frame)
        elif key == ord('q'):
            break

    for cap in vcaps.values():
        cap.release()
    cv2.destroyAllWindows()
