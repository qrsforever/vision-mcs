#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file raft.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-02-28 21:36

import torch
from raftstereo.core.raft_stereo import RAFTStereo
from raftstereo.core.utils.utils import InputPadder
from . import StereoMatcher
import time


class RaftArgs(object):
    def __init__(self):
        self.save_numpy = False
        self.mixed_precision = False
        self.valid_iters = 32
        self.hidden_dims = [128]*3
        self.corr_implementation = "reg"
        self.shared_backbone = False
        self.corr_levels = 4
        self.corr_radius = 4
        self.n_downsample = 2
        self.slow_fast_gru = True
        self.n_gru_layers = 3


class StereoMatcherRAFT(StereoMatcher):
    def __init__(self, ckpt_path='RAFT-Stereo/models/raftstereo-eth3d.pth'):
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.args = RaftArgs()
        self.model = torch.nn.DataParallel(RAFTStereo(self.args), device_ids=[self.device])
        self.model.load_state_dict(torch.load(ckpt_path, map_location=self.device))

        self.model = self.model.module
        self.model.to(self.device)
        self.model.eval()

    def match(self,rect_img1, rect_img2):
        with torch.no_grad():
            image1 = torch.from_numpy(rect_img1).permute(2, 0, 1).float()[None].to(self.device)
            image2 = torch.from_numpy(rect_img2).permute(2, 0, 1).float()[None].to(self.device)
            padder = InputPadder(image1.shape, divis_by=32)
            image1, image2 = padder.pad(image1, image2)
            t = time.time()
            _, flow_up = self.model(image1, image2, iters=self.args.valid_iters, test_mode=True)
            print(time.time() - t)

            disp = -flow_up.cpu().numpy().squeeze()

            return disp

    def reconstruct(self, disparity, rect_img1, Q, P=None):
        return super().reconstruct(disparity, rect_img1, Q, P)
