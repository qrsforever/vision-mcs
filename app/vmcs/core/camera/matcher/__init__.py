#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file __init__.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-02-28 21:30


import cv2

from abc import ABC, abstractmethod


class StereoMatcher(ABC):
    @abstractmethod
    def match(self, rect_img1, rect_img2):
        pass

    @abstractmethod
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


from .sgbm import StereoMatcherSGBM
from .raft import StereoMatcherRAFT

__all__ = [StereoMatcherSGBM, StereoMatcherRAFT]
