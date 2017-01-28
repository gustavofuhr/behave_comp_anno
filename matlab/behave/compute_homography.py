import cv2
import numpy as np


im_points = np.asarray([[453,250],[416,317],[63,327],[44,155],[125,158],[259,152],[249,130],[158,113]])
print('im_points', im_points)
print('im_points.shape', im_points.shape)
gp_points = np.asarray([[913,-358],[926,-454],[348,-876],[-148,-290],[0,-253],[346,-120],[270,0],[0,0]])
print('gp_points', gp_points)
print('gp_points.shape', gp_points.shape)

H, _ = cv2.findHomography(im_points, gp_points, 0)
print('Extracted Homography', H)