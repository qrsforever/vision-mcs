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

    def _find_features(self, img, nfeatures=500):
        orb = cv2.ORB_create(nfeatures=nfeatures)
        kp = orb.detect(img, None)
        kp, des = orb.compute(img, kp)
        return kp, des

    def match(self, rect_img1, rect_img2, fast=True):
        if not fast:
            if rect_img1.ndim == 2:
                nchannels = 1
            else:
                nchannels = 3

            feat1_kp, feat1_des = self._find_features(rect_img1, 1000)
            feat2_kp, feat2_des = self._find_features(rect_img2, 1000)
            matches = cv2.BFMatcher(cv2.NORM_HAMMING).knnMatch(feat1_des, feat2_des, k=2)
            good = []
            for m,n in matches:
                if m.distance < 0.75 * n.distance:
                    good.append(m)

            good = sorted(good, key=lambda x:x.distance)
            points = []
            for match in sorted(good, key=lambda x:x.distance):
                idx1, idx2 = match.queryIdx, match.trainIdx
                points.append(abs(np.int0(feat2_kp[idx2].pt[0]) - np.int0(feat1_kp[idx1].pt[0])))
            q1, q3 = np.quantile(points, [.25, .75])
            iqr = q3 - q1
            min_disp = math.floor(q1 - 1.5 * iqr)
            max_disp = math.ceil(q3 + 1.5 * iqr)
            num_disp = max_disp - min_disp + 1
            num_disp = ((num_disp + 15) // 16) * 16
            self.matcher.setMinDisparity(min_disp)
            self.matcher.setNumDisparities(num_disp)
            self.matcher.setP1(8 * nchannels * 11**2)
            self.matcher.setP1(32 * nchannels * 11**2)
        # 视差图的每个像素值(CV_16S)由一个16bit表示,其中低位的4位存储的是视差值得小数部分,
        # 真实视差值应该是该值除以16
        return self.matcher.compute(rect_img1, rect_img2).astype(np.float32) / 16.0

    def reconstruct(self, disparity, rect_img1, Q, P=None):
        world_xyz = cv2.reprojectImageTo3D(disparity, Q)
        mask_depth = (world_xyz[:, :, 2] < 5.0) & (world_xyz[:, :, 2] > 0.1)
        mask_brght = (rect_img1[:, :, 0] > 30) & (rect_img1[:, :, 0] < 250)
        mask_point = (mask_brght & mask_depth).flatten()

        world_xyz = world_xyz.reshape((-1, 3))
        color_map = rect_img1.reshape((-1, 3))
        world_xyz, color_map = world_xyz[mask_point], color_map[mask_point]

        if P is not None:
            world_xyz = (P.r @ world_xyz.T).T + P.t
        return world_xyz, color_map
