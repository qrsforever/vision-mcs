#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file fisheye.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-01-09 22:14


from .pinhole import PinHoleModel
import cv2


class FishEyeModel(PinHoleModel):
    '''
    '''

    def __init__(self, lazy=False):
        if lazy:
            # stereoRectify(
            # K1, D1, K2, D2, imageSize, R, tvec, flags[, R1[, R2[, P1[, P2[, Q[,
            # newImageSize[, balance[, fov_scale]]]]]]]]) -> R1, R2, P1, P2, Q
            self.stereo_rectify = cv2.fisheye.stereoRectify

    def undistort_rectify_map(self, camera_matrix, dist_coeffs, R, new_camera_matrix, image_size, m1type):
        return cv2.fisheye.initUndistortRectifyMap(
                camera_matrix,
                dist_coeffs, R,
                new_camera_matrix,
                image_size, m1type)

    def undistort_points(self, points, camera_matrix, dist_coeffs, R=None, P=None):
        return cv2.fisheye.undistortPoints(points, camera_matrix, dist_coeffs, R=R)
