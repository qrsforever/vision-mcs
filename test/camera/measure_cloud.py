#!/usr/bin/python3
# -*- coding: utf-8 -*-

import open3d as o3d
import numpy as np


def get_angle(p1, p2):
    '''
    Calculates the angles between 2 points in 3D space (angle between depth data)
    point format: (x,y,z)

    Formula(x1*x2 + y1*y2 + z1*z2)/sqrt( (x1^2 + y1^2 + z1^2) * (x2^2 +y2^2 + z2^2))
    '''
    num = (p1[0]*p2[0] + p1[1]*p2[1] + p1[2] *p2[2])
    den = (np.sqrt( (p1[0]**2 + p1[1]**2 + p1[2]**2) * (p2[0]**2 + p2[1]**2 + p2[2]**2) ) )
    return np.arccos((num/den))


def triangulate_dist(d1, d2, angle):
    ''' 
    余玄定理
    Calculates the the unknown side of a triagle given 2 sides and the angle between. 
 
    Angle is in Radians

    Formula: sqrt(a^2 + c^2 - 2ac*cos(angle))
    '''
    return np.sqrt( d1**2 + d2**2 - (2 * d1 * d2) * np.cos(angle) )


def euclid_dist(p1, p2):
    return np.sqrt((p1[0] - p2[0])**2 +
                (p1[1] - p2[1])**2 + 
                (p1[2] - p2[2])**2
                )

def pick_points(pcd):
    print("")
    print(
        "1) Please pick at least two correspondences using [shift + left click]"
    )
    print("   Press [shift + right click] to undo point picking")
    print("2) Afther picking points, press q for close the window")

    print("Left click and drag to rotate around point.")
    print("Shift Left click and drag to rotate the screen left or right")
    print("Ctrl Left Click to pan")
    print()
    vis = o3d.visualization.VisualizerWithEditing()
    vis.create_window()
    vis.add_geometry(pcd)
    vis.run()  # user picks points
    vis.destroy_window()
    print("")
    #returns the inices of the users picked points
    return vis.get_picked_points()


def manual_measure(point_cloud):
    '''
    Creates an interface. Shift click the points you want to measure. Distance is calculated between each point selected. 
    
    Distance returned is in meters, though it prints out in both cm and m. 
    '''
    total_distance = 0
    distance_segments = []

    #picked points return the index of the points picked in the cloud
    picked_points = pick_points(point_cloud)
    print(picked_points)
    
    #convert pointcloud to array of points
    np_cloud = np.asarray(point_cloud.points)

    #for every pair of points, calculate the distance
    for point in range(len(picked_points)-1):

        p1 = np_cloud[picked_points[point]]
        p2 = np_cloud[picked_points[point+1]]
        print(p1, p2)
        
        # triangulate the distance between the two points
        # angle = get_angle(p1, p2)
        # distance = triangulate_dist(p1[2], p2[2], angle)
        distance = euclid_dist(p1, p2)
    
        print("Section " + str(point+1) + ": " + str(distance) + " meters")
        
        distance_segments.append(distance)
        total_distance += distance

    print(str(total_distance * 100) + " centimeters")
    print(str(total_distance) + " meters")
    return total_distance, distance_segments, (p1, p2)


def measure_dist(vis):
    pts = vis.get_picked_points()
    if len(pts) > 1:
        point_a = getattr(pts[1], 'coord')
        point_b = getattr(pts[0], 'coord')
        dist=np.sqrt((point_a[0] - point_b[0])**2 + (point_a[1] - point_b[1])**2 + (point_a[2] - point_b[2])**2)
        print(f"Point_A: {point_a}")
        print(f"Point_B: {point_b}")
        print(f"Distance: {dist}")
    else:
        print("Select atleast 2 points to calculate Dist")

if __name__ == "__main__":
    calculated_distance = []#meters
    set_distance = [] #feet
    length = [] #cm
    body_part = []#string description
    file_name =[] #string name for capture number and camera
    note = []#notes about what the camera sees
    
    print("Starting...")

    try:
        cloud = o3d.io.read_point_cloud('./out-4.ply')
        # while True:
        #     length = manual_measure(cloud)
        #     print("Stopping...")

        vis = o3d.visualization.VisualizerWithVertexSelection()
        vis.create_window()
        vis.add_geometry(cloud)
        vis.register_selection_changed_callback(lambda : measure_dist(vis))
        vis.run()
        vis.destroy_window()
    except Exception:
        pass
