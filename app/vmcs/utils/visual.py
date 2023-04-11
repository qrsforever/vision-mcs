#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file visual.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-03-07 18:39

import open3d as o3d
import numpy as np


class View3D(object):
    def __init__(self):
        self.geometries = []
        self.vis = o3d.visualization.VisualizerWithKeyCallback()
        self.vis.register_key_callback(ord("L"), self.look_at_view)
        self.vis.register_key_callback(ord("F"), self.front_view)
        self.vis.register_key_callback(ord("U"), self.up_view)
        self.vis.register_key_callback(ord("Z"), self.zoom_view)

    def add_point_cloud(self, points, colors, outlier=(0, 0)):
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points)
        pcd.colors = o3d.utility.Vector3dVector(colors / 255.0)
        if outlier[0] > 0 and outlier[1] > 0:
            pcd, _ = pcd.remove_statistical_outlier(nb_neighbors=outlier[0], std_ratio=outlier[1])
        self.geometries.append(pcd)

    def add_lineset(self, points, colors, lines):
        line_set = o3d.geometry.LineSet()
        line_set.points = o3d.utility.Vector3dVector(points)
        line_set.lines = o3d.utility.Vector2iVector(lines)
        line_set.colors = o3d.utility.Vector3dVector(colors)
        self.geometries.append(line_set)

    def show(self, origin=None, size=0.15):
        if len(self.geometries) > 0:
            self.vis.create_window()
            if origin is not None:
                self.vis.add_geometry(o3d.geometry.TriangleMesh.create_coordinate_frame(size=size, origin=origin))
            for geo in self.geometries:
                self.vis.add_geometry(geo)
            self.vis.run()
            self.vis.clear_geometries()
            self.vis.destroy_window()
            pcd_combined = o3d.geometry.PointCloud()
            for pcd in self.geometries:
                if type(pcd) == o3d.geometry.PointCloud:
                    pcd_combined += pcd
            o3d.io.write_point_cloud('out-4.ply', pcd_combined)

        self.geometries = []

    @staticmethod
    def look_at_view(vis):
        ctr = vis.get_view_control()
        ctr.set_lookat(np.array([0, 0, 0]))
        return True

    @staticmethod
    def front_view(vis):
        ctr = vis.get_view_control()
        ctr.set_front(np.array([0, 0, 1]))
        return True

    @staticmethod
    def up_view(vis):
        ctr = vis.get_view_control()
        ctr.set_up(np.array([0, 1, 0]))
        return True

    @staticmethod
    def zoom_view(vis):
        ctr = vis.get_view_control()
        ctr.set_zoom(1)
        return True

    def add_construct_camera(self, scale, w, h, f, cx, cy, r, t):
        w = w / f
        h = h / f
        cx = cx / f
        cy = cy / f
        offset_cx = cx - w / 2.0
        offset_cy = cy - h / 2.0

        points = [
                [offset_cx, offset_cy, 0],
                [offset_cx, offset_cy, 1],
                [-0.5 * w, -0.5 * h, 1],
                [0.5 * w, -0.5 * h, 1],
                [0.5 * w, 0.5 * h, 1],
                [-0.5 * w, 0.5 * h, 1],
                [-0.5 * w, -0.5 * h, 1],
                [0, 0, 1]]
        lines = [[0, 1], [2, 3], [3, 4], [4, 5], [5, 6], [0, 2], [0, 3], [0, 4], [0, 5], [2, 4], [3, 5]]
        points = np.array(points) * scale
        points = (r @ points.T).T + t
        colors = [[0, 255, 0] for _ in range(len(lines))]
        self.add_lineset(points, colors, lines)
