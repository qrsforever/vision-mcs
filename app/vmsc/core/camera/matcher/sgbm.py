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
import open3d as o3d


class StereoMatcherSGBM(cv2.StereoSGBM):
    """
    """

    def __init__(self, min_disp=0, num_disp=320, speckle_range=5, window_size=11):
        self.matcher = cv2.StereoSGBM_create(
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
        # 真实视差值应该是该值除以16, 映射后再乘以16(毫米级真实位置)
        return self.matcher.compute(rect_img1, rect_img2).astype(np.float32) / 16.0

    def reconstruct(self, img_disp0, img_rect0, Q, P=None):
        xyz = cv2.reprojectImageTo3D(img_disp0, Q)

        mask_depth = (xyz[:, :, 2] < 5.0) & (xyz[:, :, 2] > 0.1)
        mask_brght = (img_rect0[:, :, 0] > 30) & (img_rect0[:, :, 0] < 250)

        xyz_linear = xyz.reshape((-1, 3))
        colors_linear = img_rect0.reshape((-1, 3))
        mask_linear = (mask_brght & mask_depth).flatten()

        if P is not None:
            xyz_linear = (P.r @ xyz_linear.T).T + P.t

        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(xyz_linear[mask_linear])
        pcd.colors = o3d.utility.Vector3dVector(colors_linear[mask_linear] / 255.0)

        return pcd
