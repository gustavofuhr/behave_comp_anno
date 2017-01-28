# this script shows the annotation of a clip and the corresponding ground truth
import xml.etree.ElementTree as ET
import cv2
import json
import numpy as np
import scipy.io as sio

from anno_util import *

seq_xml_bbox = {
    0: './behave_xmls/1-11200.xml',
    1: './behave_xmls/11500-17450_new.xml',
    2: './behave_xmls/18000-23700.xml',
    3: './behave_xmls/24300-35200_revised.xml',
    4: './behave_xmls/35450-47160.xml',
    5: './behave_xmls/47300-58400.xml',
    6: './behave_xmls/59800-66750.xml'
}

MARKUP_FILENAME = 'markup_fixed.txt'

H = np.matrix([[3.70563591e+00,4.52639906e+00,-1.11021848e+03],
                [1.07944747e+00,-6.37893089e+00,5.33054923e+02],
                [8.39500942e-04,2.06817444e-03,1.00000000e+00]])

class ParseBehave:



    def __init__(self):
        pass

    def get_frame(self, frame_number):
        sfilename = '{0}{1:08d}.jpg'.format(self.root_folder, frame_number)
        print(sfilename)
        return cv2.imread(sfilename)

    def parse(self, sequence_number, show_annotation = False):
        self.sequence_number = sequence_number
        self.root_folder = '/home/gfuhr/phd/datasets/behave/seq{0:02d}/'.format(sequence_number)

        xml_filename = seq_xml_bbox[sequence_number]

        loc_anno = self.parse_behave_xml_bbox(xml_filename)

        frames = list(loc_anno.keys())
        min_frame = min(frames)
        max_frame = max(frames)

        print('max_frame', max_frame)
        interaction_anno = self.parse_behave_interaction(MARKUP_FILENAME, min_frame, max_frame)

        # finallly take the annotation of collective
        collective_anno = self.parse_behave_collective('collective_anno.json', sequence_number)

        if show_annotation:
            self.show_annotation(loc_anno, interaction_anno, collective_anno)
        else:
            self.save_annotation(loc_anno, interaction_anno, collective_anno)

    def parse_behave_collective(self, json_filename, seq_number):

        with open(json_filename) as data_file:
            raw_events = json.load(data_file)

            seq_id = 'Seq{0:02d}'.format(seq_number)
            if seq_id not in raw_events:
                print('Warning: Not a single event for this sequence')
            else:
                collective = {}
                for anno in raw_events[seq_id]:
                    bframe = anno['begin_frame']
                    eframe = anno['end_frame']
                    event  = anno['event']
                    for fr in range(bframe, eframe+1):
                        collective[fr] = event

        return collective


    def parse_behave_interaction(self, filename, min_frame, max_frame):
        with open(filename, 'r') as file:
            lines = file.read().splitlines()[1:]

            interaction_frames = {}
            for l in lines:
                # print("line", l)
                group, fstart, fend, interaction = l.split(';')

                fstart = int(fstart)
                if fstart > max_frame:
                    break

                groups = group.strip().split(' ')
                group_start = []
                group_end = []
                group_start = json.loads(groups[0])
                if len(groups) > 1:
                    group_end = json.loads(groups[1])

                inter = {}
                if len(group_end) == 0:
                    # here, i am assuming that if there is only a group start the
                    # interaction is symmetric
                    inter = {}
                    for g1 in group_start:
                        for g2 in group_start:
                            if g1 != g2:
                                inter = add_interaction(inter, g1, g2, translate_interaction(interaction))
                                inter = add_interaction(inter, g2, g1, translate_interaction(interaction))
                else:
                    for g1 in group_start:
                        for g2 in group_end:
                            tin = translate_interaction(interaction)
                            inter = add_interaction(inter, g1, g2, tin)
                            # following will be treated afterwards
                            # if tin == 'following':
                            #     inter = add_interaction(inter, g2, g1, 'being_followed')

                repeat_interaction(interaction_frames, int(fstart), int(fend), inter)

            return interaction_frames

    def parse_behave_xml_bbox(self, filename):
        """
        This function extracts the bounding boxes of the people
        in a sequence

        IMPORTANT: It requires a modified version of the XML
        """
        tree = ET.parse(filename)
        root = tree.getroot()

        anno = {}

        people_boxes = root.findall('data/sourcefile/object')
        for p in people_boxes:
            bboxes = p.findall('attribute/bbox')
            person_id = p.get('id')
            for b in bboxes:
                minframe, maxframe = b.get('framespan').split(':')
                minframe, maxframe = int(minframe), int(maxframe)

                x = int(b.get('x'))
                y = int(b.get('y'))
                w = int(b.get('width'))
                h = int(b.get('height'))
                if h > 5:
                    for i in range(minframe,maxframe+1):
                        # if i == 22632:
                        #     print('h ',h)
                        bb_anno = {
                            'id': person_id,
                            'bbox': [x, y, w, h],
                            'gpoint': get_groundpoint(H, [x+w/2,y+h])
                        }
                        if i in anno:
                            anno[i].append(bb_anno)
                        else:
                            anno[i] = [bb_anno]
        return anno

    def show_annotation(self, loc_anno, interaction_anno, collective_anno):

        SAVE_FRAMES = True

        frames = list(loc_anno.keys())
        frames.sort() # sorts in place

        colors = [(0,0,233),(0,233,0),(233,0,0),(233,233,0),(0,233,233),(233,0,233),(233,233,233),(33,33,33)]
        font = cv2.FONT_HERSHEY_SIMPLEX
        for fr in frames:
            img = self.get_frame(fr)

            def gpoint_from_id(loc_anno, id):
                for bb in loc_anno:
                    if bb['id'] == id:
                        pt = gpoint2image(H, bb['gpoint'])
                        return (int(pt[0]), int(pt[1]))

                print('Did not found location of id',id)
                return []

            for bb in loc_anno[fr]:
                x,y,w,h = bb['bbox']
                cv2.rectangle(img, (x,y), (x+w,y+h), colors[int(bb['id'])])

                im_point = gpoint2image(H, bb['gpoint'])
                cv2.circle(img, (int(im_point[0]), int(im_point[1])), 4, colors[int(bb['id'])], -1)

                cv2.putText(img,bb['id'],(x-10,y-10), font, 1, colors[int(bb['id'])], 2, cv2.LINE_AA)

            if fr in interaction_anno:
                for t1 in interaction_anno[fr]:
                    for t2 in interaction_anno[fr][t1]:
                        sinteraction = abbreviate_interaction(interaction_anno[fr][t1][t2])
                        # print('t1', t1)
                        # print('t2', t2)
                        im_point1 = gpoint_from_id(loc_anno[fr], str(t1))
                        im_point2 = gpoint_from_id(loc_anno[fr], str(t2))
                        cv2.line(img, im_point1, im_point2, (200, 200, 200), 2)

                        im_point3 = (int((im_point1[0]+im_point2[0])/2.0)-10, int((im_point1[1]+im_point2[1])/2.0)+20)

                        cv2.putText(img, sinteraction, im_point3, font, 0.5, (50,200,20), 1)

            if fr in collective_anno:
                # print('collective', collective_anno[fr])
                cv2.putText(img, collective_anno[fr], (10, img.shape[0]-30), font, 1.2, (20,20,200), 2, cv2.LINE_AA)


            # write the frame number
            cv2.putText(img, "Frame: {0}".format(fr), (10,40), font, 1, (20,200,20), 2, cv2.LINE_AA)
            if SAVE_FRAMES:
                cv2.imwrite('out/seq{0}/{1:05d}.jpg'.format(self.sequence_number, fr), img)
            cv2.imshow("bbox", img)
            cv2.waitKey(10)

    def get_all_ids(self, loc_anno):
        ids = []
        for fr in loc_anno:
            for bb in loc_anno[fr]:
                iid = int(bb['id'])
                if iid not in ids:
                    ids.append(iid)

        return ids

    def save_annotation(self, loc_anno, interaction_anno, collective_anno):
        frames = list(loc_anno.keys())
        frames.sort() # sorts in place

        mframe = min(frames)
        anno = {'n_frames': max(frames)-mframe+1,
                'positions': [],
                'interactions': [],
                'min_frame': min(frames),
                'collective_behaviour': np.zeros((max(frames)-mframe+1,), dtype=np.object)}

        all_ids = self.get_all_ids(loc_anno)
        print('min_frame', min(frames))
        print('all_ids', all_ids)


        # initialize empty structure
        for iid in range(max(all_ids)+1):
            anno['positions'].append({'data': []})

        for fr in range(max(frames)-mframe+1):
            for ii in range(max(all_ids)+1):
                anno['positions'][ii]['data'].append({'gpoint': np.array([])})
            anno['interactions'].append(np.array([]))



        # exit(1)
        colors = [(0,0,233),(0,233,0),(233,0,0),(233,233,0),(0,233,233),(233,0,233),(233,233,233),(33,33,33)]
        font = cv2.FONT_HERSHEY_SIMPLEX
        for fr in frames:
            # img = self.get_frame(fr)

            def gpoint_from_id(loc_anno, id):
                for bb in loc_anno:
                    if bb['id'] == id:
                        pt = gpoint2image(H, bb['gpoint'])
                        return (int(pt[0]), int(pt[1]))

                print('Did not found location of id',id)
                return []

            def empty_interaction_matrix(n_ids):
                ret = np.zeros((n_ids,n_ids), dtype=np.object)
                ret[:] = ''
                return ret

            for bb in loc_anno[fr]:
                x,y,w,h = bb['bbox']
                # cv2.rectangle(img, (x,y), (x+w,y+h), colors[int(bb['id'])])

                im_point = gpoint2image(H, bb['gpoint'])
                # cv2.circle(img, (int(im_point[0]), int(im_point[1])), 4, colors[int(bb['id'])], -1)

                # cv2.putText(img,bb['id'],(x-10,y-10), font, 1, colors[int(bb['id'])], 2, cv2.LINE_AA)

                # print('id', int(bb['id']) )
                # print('fr', fr-mframe)
                anno['positions'][int(bb['id'])]['data'][fr-mframe]['gpoint'] = np.asarray([bb['gpoint']])


            if fr in interaction_anno:
                interaction_matrix = empty_interaction_matrix(max(all_ids)+1)
                for t1 in interaction_anno[fr]:
                    for t2 in interaction_anno[fr][t1]:
                        sinteraction = abbreviate_interaction(interaction_anno[fr][t1][t2])
                        # print('t1', t1)
                        # print('t2', t2)
                        im_point1 = gpoint_from_id(loc_anno[fr], str(t1))
                        im_point2 = gpoint_from_id(loc_anno[fr], str(t2))
                        # cv2.line(img, im_point1, im_point2, (200, 200, 200), 2)

                        im_point3 = (int((im_point1[0]+im_point2[0])/2.0)-10, int((im_point1[1]+im_point2[1])/2.0)+20)

                        # cv2.putText(img, sinteraction, im_point3, font, 0.5, (50,200,20), 1)

                        # print('id', t1)
                        # print('id', t2)
                        # print('fr', fr-mframe)

                        interaction_matrix[t1][t2] = interaction_anno[fr][t1][t2]

                anno['interactions'][fr-mframe] = interaction_matrix


            if fr in collective_anno:
                anno['collective_behaviour'][fr-mframe] = collective_anno[fr]
            # write the frame number
            # cv2.putText(img, "Frame: {0}".format(fr), (10,40), font, 1, (20,200,20), 2, cv2.LINE_AA)
            # cv2.imshow("bbox", img)
            # cv2.waitKey(10)

        sio.savemat('seq{0:02d}_crude.mat'.format(self.sequence_number), {'anno': anno})
