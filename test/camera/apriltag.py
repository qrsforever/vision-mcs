#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file apriltag.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-03-20 15:47


import cv2
from apriltags_eth import make_default_detector

COLUMNS = 6
SIZE = 3.52 / 100
SPACING = 1.056 / 100

img = cv2.resize(cv2.imread('1679033209275314432.png'), (640, 480))


def get_tag_corners_for_id(tag_id):
    # col: x row: y
    # ll lr
    # ul ur
    a = SIZE
    b = SPACING
    tag_row, tag_col = (tag_id) // COLUMNS, (tag_id) % COLUMNS
    left = bottom = lambda i: i * (a + b)
    right = top = lambda i: (i + 1) * a + (i) * b
    return [(left(tag_col), bottom(tag_row)),
            (right(tag_col), bottom(tag_row)),
            (right(tag_col), top(tag_row)), (left(tag_col), top(tag_row))]


detector = make_default_detector()
ids = detector.extract_tags(img)
ids.sort(key=lambda x: x.id)
for tag in ids:
    if tag.id in (0, 2, 7, 9):
        print(get_tag_corners_for_id(tag.id))
        print(tag.id, tag.corners)
        for corner in tag.corners:
            x, y = corner 
            img = cv2.circle(img, (int(x), int(y)), 2, (0, 0, 255), -1)
            break

cv2.imwrite('out.png', img)

# from aprilgrid import AprilGrid
# import cv2
# 
# grid = AprilGrid(7, 6, 2.0/100, 0.5/100)
# 
# im = cv2.imread('/tmp/april.png')
# res = grid.compute_observation(im)
# 
# for image_point, tgt_point in zip(res.image_points, res.target_points):
#     x = int(image_point[0])
#     y = int(image_point[1])
#     tx = tgt_point[0]
#     ty = tgt_point[1]
#     print tgt_point
#     cv2.circle(im, (x, y), 5, (255 - tx/0.1205*200, 255, ty/0.1406*200), -1)
# 
# cv2.imwrite('/tmp/out.png', im)
