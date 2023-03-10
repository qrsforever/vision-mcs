#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file raft.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-02-28 21:36

import torch
import cv2
import open3d as o3d

from raftstereo.core.raft_stereo import RAFTStereo
from raftstereo.utils.utils import InputPadder


class RaftArgs():
    def __init__(self):
        self.restore_ckpt="modules/RAFT-Stereo/models/raftstereo-eth3d.pth"
        self.save_numpy=False
        self.mixed_precision=False
        self.valid_iters = 32
        self.hidden_dims = [128]*3
        self.corr_implementation="reg"
        self.shared_backbone=False
        self.corr_levels=4
        self.corr_radius=4
        self.n_downsample=2
        self.slow_fast_gru=False
        self.n_gru_layers=3


class RaftStereoMatcher:
    def __init__(self):
        self.DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.args = RaftArgs()
        self.model = torch.nn.DataParallel(RAFTStereo(self.args), device_ids=[self.DEVICE])
        self.model.load_state_dict(torch.load(self.args.restore_ckpt, map_location =self.DEVICE))

        self.model = self.model.module
        self.model.to(self.DEVICE)
        self.model.eval()

    def match(self,image1_in,image2_in):
        with torch.no_grad():
            image1 = torch.from_numpy(image1_in).permute(2, 0, 1).float()[None].to(self.DEVICE)
            image2 = torch.from_numpy(image2_in).permute(2, 0, 1).float()[None].to(self.DEVICE)
            padder = InputPadder(image1.shape, divis_by=32)
            image1, image2 = padder.pad(image1, image2)

            _, flow_up = self.model(image1, image2, iters=self.args.valid_iters, test_mode=True)

            disp0 = -flow_up.cpu().numpy().squeeze()

            return disp0

    def reconstruct(self,img_disp0,img_rect0, Q, P=None):
        # reproject disparity to 3D
        xyz = cv2.reprojectImageTo3D(img_disp0, Q)

        # construct validity masks based on distance and brightness
        mask_depth = (xyz[:,:,2]<5.0) & (xyz[:,:,2]>0.1)
        mask_brght = (img_rect0>30) & (img_rect0<250)

        # create linear point and color lists
        xyz_linear = xyz.reshape((-1,3))
        colors_linear = img_rect0.reshape((-1,3))
        mask_linear = (mask_brght[:, :, 0] & mask_depth).flatten()

        # Apply pose transform, if we get one
        if P is not None:
            xyz_linear = (P.r @ xyz_linear.T).T + P.t

        # create open3d geometry
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(xyz_linear[mask_linear])
        pcd.colors = o3d.utility.Vector3dVector(colors_linear[mask_linear]/255.0)

        return pcd
