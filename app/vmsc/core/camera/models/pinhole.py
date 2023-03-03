#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file pinhole.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-01-09 21:46

import cv2
import numpy as np


class PinHoleModel(object):
    '''

    '''

    def __init__(self, lazy=False):
        if lazy:
            # stereoRectify(
            # cameraMatrix1, distCoeffs1, cameraMatrix2, distCoeffs2, imageSize,
            # R, T[, R1[, R2[, P1[, P2[, Q[, flags[, alpha[, newImageSize]]]]]]]])
            # -> R1, R2, P1, P2, Q, validPixROI1, validPixROI2
            # also do: R1, R2, P1, P2, Q, *_ = cv2.stereoRectify()
            self.stereo_rectify = lambda *argv, **kwargs: cv2.stereoRectify(*argv, **kwargs)[:5]

    def stereo_rectify(
            self,
            camera_matrix1, dist_coeffs1,
            camera_matrix2, dist_coeffs2,
            image_size, R, T, flags,
            newImageSize=None, balance=None, fov_scale=None):

        '''
        Args:
            R 两个相机坐标系统的旋转矩阵(2 to 1)
            T 两个相机坐标系统的平移矩阵(2 to 1)
        Returns:
            R1: 第1个相机校正旋转矩阵(3x3)
            R2: 第2个相机校正旋转矩阵(3x3)
            P1: 第1个相机校正投影矩阵(3x4)
            P2: 第2个相机校正投影矩阵(3x4)
            Q: 重投影矩阵(4x4)
        '''

        # https://zhuanlan.zhihu.com/p/348846552
        # 平移向量/旋转角度向量
        tvec = T.astype(np.float64).reshape((3, 1))
        rvec, _ = cv2.Rodrigues(R.astype(np.float64))  # 模表示旋转角度

        rvec *= -0.5  # 旋转左右相机使它们的基坐标系平行(但不一定共面）
        r_r, _ = cv2.Rodrigues(rvec)

        t = r_r @ tvec  # 重新计算新基下的平移向量
        uu = np.array([1 if t[0, 0] > 0 else -1, 0, 0]).reshape((3, 1))

        #               ^  e3  叉乘得到垂直e1,e2平面的法向量
        #               │
        #               │            ^   相机2平分后的平移向量(t)
        #        ───────┼───────────/ e2
        #       ╱       │          ╱
        #      ╱        │         ╱
        #     ╱                  ╱ theta
        #    ╱─────────────────────> e1 相机1坐标系(1,0,0)
        ww = np.cross(t, uu, axis=0)
        nw = np.linalg.norm(ww)
        if nw > 0.0:
            # 左右相机各自旋转, 将原左(右)相机的X轴于平移向量t重合, 即绕这两个向量的法向量旋转
            # 通过每一角度对应的模长计算旋转角度
            # 模表示旋转角度
            ww *= np.arccos(np.abs(t[0]) / np.linalg.norm(t)) / nw

        wr, _ = cv2.Rodrigues(ww)

        # 同行
        ri1 = wr @ r_r.T
        R1 = ri1.astype(np.float64)
        ri2 = wr @ r_r
        R2 = ri2.astype(np.float64)
        tnew = ri2 @ tvec

        balance = min(max(balance, 0), 1) if balance is not None else 0.0

        def _calculate_projection(K, D, R):  # {{{
            w, h = image_size

            _points = np.expand_dims(np.array(
                [[w / 2, 0],
                 [w, h / 2],
                 [w / 2, h],
                 [0, h / 2]], dtype=np.float64), 1)

            points = np.squeeze(self.undistort_points(_points, K, D, R=R))
            cn = np.mean(points, axis=0).flatten()

            aspect_ratio = K[0, 0] / K[1, 1]

            cn[1] *= aspect_ratio
            points[:, 1] *= aspect_ratio

            minx = points[:, 0].min()
            maxx = points[:, 0].max()
            miny = points[:, 1].min()
            maxy = points[:, 1].max()

            f1 = w * 0.5 / (cn[0] - minx)
            f2 = w * 0.5 / (maxx - cn[0])
            f3 = h * 0.5 * aspect_ratio / (cn[1] - miny)
            f4 = h * 0.5 * aspect_ratio / (maxy - cn[1])

            fmin = min(f1, min(f2, min(f3, f4)))
            fmax = max(f1, max(f2, max(f3, f4)))

            f = balance * fmin + (1.0 - balance) * fmax

            f *= 1.0 / fov_scale if fov_scale is not None and fov_scale > 0 else 1.0

            new_f = np.array((f, f))
            new_c = -cn * f + np.array((w, h * aspect_ratio)) * 0.5

            new_f[1] /= aspect_ratio
            new_c[1] /= aspect_ratio

            if newImageSize is not None:
                rx = newImageSize[0] / image_size[0]
                ry = newImageSize[1] / image_size[1]

                new_f[0] *= rx
                new_f[1] *= ry
                new_c[0] *= rx
                new_c[1] *= ry

            P = np.array([[new_f[0], 0, new_c[0]],
                        [0, new_f[1], new_c[1]],
                        [0, 0, 1]])
            return P  # }}}

        new_k1 = _calculate_projection(camera_matrix1, dist_coeffs1, R1)
        new_k2 = _calculate_projection(camera_matrix2, dist_coeffs2, R2)

        fc_new = min(new_k1[1, 1], new_k2[1, 1])
        cc_new = np.array([[new_k1[0, 2], new_k1[1, 2]], [new_k2[0, 2], new_k2[1, 2]]])

        if flags & cv2.CALIB_ZERO_DISPARITY == cv2.CALIB_ZERO_DISPARITY:
            cc_new[0, :] = (cc_new[0, :] + cc_new[1, :]) * 0.5
            cc_new[1, :] = cc_new[0, :]
        else:
            cc_new[0, 1] = (cc_new[0, 1] + cc_new[1, 1]) * 0.5
            cc_new[1, 1] = cc_new[0, 1]

        P1 = np.array([[fc_new, 0, cc_new[0, 0], 0],
                       [0, fc_new, cc_new[0, 1], 0],
                       [0, 0, 1, 0]], dtype=np.float64)

        P2 = np.array([[fc_new, 0, cc_new[1, 0], tnew[0][0] * fc_new],  # baseline * focal length;,
                       [0, fc_new, cc_new[1, 1], 0],
                       [0, 0, 1, 0]], dtype=np.float64)

        Q = np.array([[1, 0, 0, -cc_new[0, 0]],
                       [0, 1, 0, -cc_new[0, 1]],
                       [0, 0, 0, fc_new],
                       [0, 0, -1. / tnew[0][0], (cc_new[0, 0] - cc_new[1, 0]) / tnew[0][0]]], dtype=np.float64)

        return R1, R2, P1, P2, Q

    def undistort_rectify_map(self, camera_matrix, dist_coeffs, R, new_camera_matrix, image_size, m1type):
        return cv2.initUndistortRectifyMap(
                camera_matrix,
                dist_coeffs, R,
                new_camera_matrix,
                image_size, m1type)

    def undistort_points(self, points, camera_matrix, dist_coeffs, R=None, P=None):
        return cv2.undistortPoints(points, camera_matrix, dist_coeffs, R=R)


class PinHoleRadTanModel(PinHoleModel):
    pass
