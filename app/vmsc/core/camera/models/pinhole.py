#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file pinhole.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-01-09 21:46

import cv2


class PinHoleModel(object):
    '''

    '''

    def stereo_rectify(self,
            camera_matrix1, dist_coeffs1,
            camera_matrix2, dist_coeffs2,
            image_size, R, T, flags,
            R1=None, R2=None, P1=None, P2=None, Q=None,
            new_image_size=None, balance=None, fov_scale=None, model=None):
        pass

    def undistort_rectify(self, camera_matrix, dist_coeffs, R, new_camera_matrix, image_size, m1type):
        return cv2.initUndistortRectifyMap(
                camera_matrix,
                dist_coeffs, R,
                new_camera_matrix,
                image_size, m1type)

    def undistort_points(self, points, camera_matrix, dist_coeffs, R=None, P=None):
        return cv2.undistortPoints(points, camera_matrix, dist_coeffs, R=R)


class PinHoleRadTanModel(PinHoleModel):
    pass
