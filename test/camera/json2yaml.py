#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file json2yaml.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-03-24 16:31


# import sys
import os
import json
import yaml
import numpy as np
import cv2


if __name__ == "__main__":

    # if len(sys.argv) != 2:
    #     raise "input json file"
    # json_path = sys.argv[1]
    json_path = './out/calibration.json'
    file_name = os.path.basename(json_path)
    with open(json_path, 'r') as fr:
        jdata = json.load(fr)
    # print(jdata)

    # with open(f'{file_name}.yml', 'w') as fw:
    #     yaml.dump(jdata, fw)

    sensors = {}
    cameras = jdata['cameras']
    campose = jdata['camera_poses']

    for cam, params in cameras.items():
        if cam not in sensors.keys():
            intrinsics = {'parameters': {}, 'type': 'PinholeRadTan'}
            sensors[cam] = {
                'intrinsics': intrinsics,
                'extrinsics': {},
            }
        intrinsics = sensors[cam]['intrinsics']
        intrinsics['parameters']['image_size'] = params['image_size']
        K = np.array(params['K'])
        D = np.array(params['dist'])
        intrinsics['parameters']['cx'] = float(K[0][2])
        intrinsics['parameters']['cy'] = float(K[1][2])
        intrinsics['parameters']['fx'] = float(K[0][0])
        intrinsics['parameters']['fy'] = float(K[1][1])
        intrinsics['parameters']['k1'] = float(D[0][0])
        intrinsics['parameters']['k2'] = float(D[0][1])
        intrinsics['parameters']['p1'] = float(D[0][2])
        intrinsics['parameters']['p2'] = float(D[0][3])
        # intrinsics['parameters']['k3'] = float(D[0][4])
        # print(json.dumps(sensors[cam], indent=4))

    for pair, params in campose.items():
        if '_to_' not in pair:
            extrinsics = sensors[pair]['extrinsics']
        else:
            extrinsics = sensors[pair[:pair.index('_to_')]]['extrinsics']
        R, T = np.array(params['R']), np.array(params['T'])
        angles, _ = cv2.Rodrigues(R)
        extrinsics['axis_angle'] = [float(x) for x in np.squeeze(angles)]
        extrinsics['translation'] = [float(x) for x in T]
    with open('out/calibration_result.yaml', 'w') as fw:
        yaml.dump({"sensors": sensors}, fw)
