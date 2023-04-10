#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file mcs.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-01-09 22:29

import yaml
import cv2
import numpy as np  # noqa
import os.path as osp

from vmcs.utils.logger import EasyLoggerMP as logger
from vmcs.utils.visual import View3D
from vmcs.core.camera import CameraParam, StereoPair
from vmcs.core.const import StereoPos
from vmcs.core.camera.matcher import StereoMatcherSGBM, StereoMatcherRAFT


DEBUG_INFO = False
STEREO_MATCHER = 'SGBM'


class MultiCameraSystem(object):
    '''
    '''

    def __init__(self, matcher_type='sgbm', matcher_args={}):
        self.cameras = {}
        self.camera_pairs = {}
        self.reference_camera = ''
        if matcher_type == 'sgbm':
            self.matcher = StereoMatcherSGBM(**matcher_args)
        elif matcher_type == 'raft':
            self.matcher = StereoMatcherRAFT(**matcher_args)
        else:
            raise

    def load_and_init(self, yaml_path, pairs, reference_camera):
        with open(yaml_path, 'r') as f:
            self.calibration_parameters = yaml.load(f, Loader=yaml.FullLoader)

        # parse cameras
        for cam, params in self.calibration_parameters['sensors'].items():
            extrinsics = params['extrinsics']
            intrinsics = params['intrinsics']
            self.cameras[cam] = CameraParam(cam, intrinsics, extrinsics)

        if DEBUG_INFO:
            for camera in self.cameras.values():
                logger.info(camera)

        # cameras pairs
        self.reference_camera = reference_camera
        for cam1, cam2 in pairs:
            self.camera_pairs[(cam1, cam2)] = StereoPair(self.cameras[cam1], self.cameras[cam2])

        if DEBUG_INFO:
            for pair in self.camera_pairs.values():
                logger.info(pair)

    def remap_images(self, multiviews):
        rect_imgs = {}
        view_imgs = {}
        for cam, view in multiviews.items():
            if isinstance(view, str):
                assert osp.exists(view), f'not exist image path: {view}'
                view = cv2.imread(view)
            view_imgs[cam] = view
        for (cam1, cam2), cam_pair in self.camera_pairs.items():
            rect_img1 = cv2.remap(view_imgs[cam1], *cam_pair.get_rect_map(pos=StereoPos.L), cv2.INTER_LANCZOS4)
            rect_img2 = cv2.remap(view_imgs[cam2], *cam_pair.get_rect_map(pos=StereoPos.R), cv2.INTER_LANCZOS4)
            rect_imgs[(cam1, cam2)] = (rect_img1, rect_img2)
        return rect_imgs

    def reconstruct_points_3d(self, images, draw=False):
        if draw:
            vis = View3D()
        world_xyz_points = []
        pose_refer_world = self.cameras[self.reference_camera].pose_cam_world
        for (cam1, cam2), cam_pair in self.camera_pairs.items():
            rect_img1, _, disparity = cam_pair.stereo_disparity(images[cam1], images[cam2], self.matcher)
            pose_world_rect = self.cameras[cam1].pose_cam_world.I @ cam_pair.pose_rect_cam.I
            pose_refer_rect = pose_refer_world @ pose_world_rect
            world_xyz, color_map = self.matcher.reconstruct(disparity, rect_img1, cam_pair.Q, P=pose_refer_rect)
            if draw:
                vis.add_point_cloud(world_xyz, color_map, outlier=(20, 1.5))
            world_xyz_points.append(world_xyz)
        if draw:
            for camera in self.cameras.values():
                pose_refer_cam = pose_refer_world @ camera.pose_cam_world.I
                vis.add_construct_camera(
                        0.175, camera.w, camera.h, camera.fx, camera.cx, camera.cy,
                        pose_refer_cam.r, pose_refer_cam.t)
            vis.show(origin=(0, 0, 0))
        return world_xyz_points


if __name__ == "__main__":

    curdir = osp.abspath(osp.dirname(__file__))
    asset_dir = f'{curdir}/../../../asset'
    test_image = '001.png'
    # test_image = '1679644864764592896.png'
    test_dir = f'{curdir}/../../../test'
    images_root = f'{asset_dir}/camera'
    # images_root = f'{test_dir}/camera/out'

    mcs = MultiCameraSystem()
    # mcs = MultiCameraSystem(
    #         matcher_type='raft',
    #         matcher_args={'ckpt_path': f'{asset_dir}/models/raftstereo-eth3d.pth'})
    camera_pairs = [('cam1', 'cam2'), ('cam2', 'cam3'), ('cam4', 'cam2')]
    mcs.load_and_init(f'{images_root}/calibration_result.yaml', camera_pairs, 'cam2')

    images = {cam: '%s/%s/%s' % (images_root, cam, test_image) for cam in mcs.cameras.keys()}
    mcs.reconstruct_points_3d(images, draw=True)
