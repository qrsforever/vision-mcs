#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file sgbm.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-02-28 21:37


import math
import cv2
import numpy as np


class StereoMatcherSGBM(object):
    """
    """

    def __init__(self, min_disp=0, num_disp=320, speckle_range=5, window_size=11):
        self.matcher = cv2.StereoSGBM.create(
                minDisparity=min_disp,
                numDisparities=num_disp,
                uniquenessRatio=5,
                speckleRange=speckle_range,
                disp12MaxDiff=1,
                P1=8 * 3 * window_size**2,
                P2=32 * 3 * window_size**2)

    def _measure_disparity(matches):
        # matches 在计算视差之前，计算出出合适的max_disp, min_disp
        # TODO
        dxs = np.int0([matches[i,1,0] - matches[i,0,0] for i in range(len(matches))])
        q1, q3 = np.quantile(dxs, [.25, .75])
        iqr = q3 - q1
        min_disp = math.floor(q1 - 1.5 * iqr)
        max_disp = math.ceil(q3 + 1.5 * iqr)
        return min_disp, max_disp

    def match(self, rect_img1, rect_img2):
        # TODO
        # if rect_img1.ndim == 2:
        #     img_channels = 1
        # else:
        #     img_channels = 3
        # 视差图的每个像素值(CV_16S)由一个16bit表示,其中低位的4位存储的是视差值得小数部分,
        # 真实视差值应该是该值除以16
        return self.matcher.compute(rect_img1, rect_img2).astype(np.float32) / 16.0

    def reconstruct(self, disparity, rect_img1, Q, P=None):
        world_xyz = cv2.reprojectImageTo3D(disparity, Q)

        mask_depth = (world_xyz[:, :, 2] < 5.0) & (world_xyz[:, :, 2] > 0.1)
        mask_brght = (rect_img1[:, :, 0] > 30) & (rect_img1[:, :, 0] < 250)
        mask_point = (mask_brght & mask_depth).flatten()

        world_xyz = world_xyz.reshape((-1, 3))
        color_img = rect_img1.reshape((-1, 3))
        world_xyz, color_img = world_xyz[mask_point], color_img[mask_point]

        if P is not None:
            world_xyz = (P.r @ world_xyz.T).T + P.t
        return world_xyz, color_img
