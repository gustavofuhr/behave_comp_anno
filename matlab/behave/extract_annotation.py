# this script shows the annotation of a clip and the corresponding ground truth
import xml.etree.ElementTree as ET
import cv2
import json
import numpy as np
import copy


from parse_behave import ParseBehave



sequences = [0, 1, 2, 3, 4, 5, 6]
for s in sequences:
    pb = ParseBehave()
    pb.parse(s)
