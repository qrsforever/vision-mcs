import open3d as o3d
import numpy as np

scale = 50

line = np.linspace(0, scale, scale+1, dtype=np.float64)

points = []
colors = []
for x in line:
    for y in line:
        for z in line:
            points.append([x,y,z])
            colors.append([x/scale, y/scale, z/scale])

pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(points)
pcd.colors = o3d.utility.Vector3dVector(colors)


def look_at_view(vis):
    ctr = vis.get_view_control()
    ctr.set_lookat(np.array([0, 0, 0]))
    return True


def front_view(vis):
    ctr = vis.get_view_control()
    ctr.set_front(np.array([0, 0, 1]))
    return True


def up_view(vis):
    ctr = vis.get_view_control()
    ctr.set_up(np.array([0, 1, 0]))
    return True


def zoom_view(vis):
    ctr = vis.get_view_control()
    ctr.set_zoom(1)
    return True


key_callback = {}
key_callback[ord("L")] = look_at_view
key_callback[ord("F")] = front_view
key_callback[ord("U")] = up_view
key_callback[ord("Z")] = zoom_view

o3d.visualization.draw_geometries_with_key_callbacks([pcd],key_callback)
