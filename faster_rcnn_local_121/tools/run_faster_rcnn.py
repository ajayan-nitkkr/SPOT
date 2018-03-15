"""
import _init_paths
import tensorflow as tf
from fast_rcnn.config import cfg
from fast_rcnn.test import im_detect
from fast_rcnn.nms_wrapper import nms
from utils.timer import Timer
import matplotlib.pyplot as plt
import numpy as np
import os, sys, cv2
import argparse
import time
from networks.factory import get_network
import preprocess
from filter_boxes import filter_detections
"""
# --------------------------------------------------------
# Tensorflow Faster R-CNN
# Licensed under The MIT License [see LICENSE for details]
# Written by Zheqi he, Xinlei Chen, based on code from Ross Girshick
# --------------------------------------------------------
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

#import _init_paths
from . import _init_paths
from model.test import test_net
from model.test import im_detect
from model.config import cfg, cfg_from_file, cfg_from_list
from model.nms_wrapper import nms
from datasets.factory import get_imdb
import argparse
import pprint
import time, os, sys
import cv2
import numpy as np

import tensorflow as tf
from nets.vgg16 import vgg16

#import preprocess
from utils.timer import Timer

CLASSES = ('__background__', 'poacher', 'animal')
NETS = {'vgg16': ('vgg16_faster_rcnn_iter_70000.ckpt',)}
DATASETS = {'pascal_voc': ('voc_2007_trainval',)} 

current_milli_time = lambda: int(round(time.time() * 1000))

def vis_detections(im, class_name, dets, display, thresh=0.5):
    """Draw detected bounding boxes."""
    inds = np.where(dets[:, -1] >= thresh)[0]
    if len(inds) == 0:
        return im

    overlay = im.copy()
    returnIm = im.copy()
    for i in inds:
        bbox = dets[i, :4]
        score = dets[i, -1]

        if display == 'poacher':
            if class_name == 'poacher':
                cv2.rectangle(overlay, \
                              (bbox[0], bbox[1]), (bbox[2], bbox[3]), \
                              (255,0,0), -1)
        elif display == 'animal':
            if class_name == 'animal':
                cv2.rectangle(overlay, \
                              (bbox[0], bbox[1]), (bbox[2], bbox[3]), \
                              (0,255,0), -1)
        else:
            if class_name == 'poacher':
                cv2.rectangle(overlay, \
                              (bbox[0], bbox[1]), (bbox[2], bbox[3]), \
                              (255,0,0), -1)
            else:
                cv2.rectangle(overlay, \
                              (bbox[0], bbox[1]), (bbox[2], bbox[3]), \
                              (0,255,0), -1)
    returnIm = cv2.addWeighted(overlay, 0.2, im, 1-0.2, 0)
    return returnIm


def process(sess, net, im):
    """Detect object classes in an image using pre-computed object proposals."""

    timer = Timer()
    timer.tic()
    # Detect all object classes and regress object bounds
    scores, boxes = im_detect(sess, net, im)
    timer.toc()
#    print ('Detection took {:.3f}s for '
#           '{:d} object proposals').format(timer.total_time, boxes.shape[0])
    return scores, boxes

def parse_args():
    """Parse input arguments."""
    parser = argparse.ArgumentParser(description='Faster R-CNN demo')
    parser.add_argument('--gpu', dest='gpu_id', help='GPU device id to use [0]',
                        default=0, type=int)
    parser.add_argument('--cpu', dest='cpu_mode',
                        help='Use CPU mode (overrides --gpu)',
                        action='store_true')
    parser.add_argument('--net', dest='demo_net', help='Network to use [vgg16]',
                        default='vgg16')

    args = parser.parse_args()

    return args

def capture_and_tag(sess, net, preprocessDict, video, q, sleepTime, display, callback_controller, cap):
    """ Capture frames from video and tag bounding boxes """
    print("Capturing image frames..")
    print("[Press ctrl + C to quit]")

    crop = preprocessDict['crop']
    invert = preprocessDict['invert']
    cropLeft = preprocessDict['cropLeft']
    cropRight = preprocessDict['cropRight']
    cropTop = preprocessDict['cropTop']
    cropBottom = preprocessDict['cropBottom']

    # TODO (Ajay): Have to check with Liz why these two VideoCapture objects were made here
    # Capture frames from video
    # cap = cv2.VideoCapture(video)
    ret, frame = cap.read()

    # Clear bottom text from frame
    # cap = cv2.VideoCapture(video)
    try:
#        cv2.namedWindow('annotations', cv2.WINDOW_AUTOSIZE)
        prev_bb = None
        file_path = 'results/'
        i = 0
        while(True):
            # Capture frame-by-frame, skip 1 frame
            cap.grab()
            for _ in range(1):
                cap.grab()
                ret, frame = cap.retrieve()
                # callback_controller(frame)

                # Exit if frames are over - no more input
                if frame is None:
                    raise KeyboardInterrupt
		
                # Process frames
                if invert:
                    frame = 255 - frame

                # callback_controller(frame)

                scores_all, boxes_all = process(sess, net, frame)

                # Filter predicted boxes based on bounding boxes from previous frame
                boxes = boxes_all; scores = scores_all
                prev_bb = boxes

                # Display the resulting frame
                #if cv2.waitKey(0) & 0xFF == ord('q'):
                ##if cv2.waitKey(10) & 0xFF == ord('q'):
                ##    break
                    
                # Visualize detections for each class

                NMS_THRESH = 0.3
                for cls_ind, cls in enumerate(CLASSES[1:]):
                    cls_ind += 1  # because we skipped background

                    cls_boxes = boxes[:, 4 * cls_ind:4 * (cls_ind + 1)]
                    cls_scores = scores[:, cls_ind]
                    dets = np.hstack((cls_boxes, \
                        cls_scores[:, np.newaxis])).astype(np.float32)
                    keep = nms(dets, NMS_THRESH)
                    dets = dets[keep, :]
                    if crop:
                        newDets = np.zeros((1,5), dtype=dets.dtype)
                        for det in dets:
                            x1 = det[0]
                            y1 = det[1]
                            x2 = det[2]
                            y2 = det[3]
                            if (x1 < cropLeft) or \
                               (y1 < cropTop) or \
                               (cropRight < x2) or \
                               (cropBottom < y2):
                                continue
                            else:
                                newDets = np.vstack((newDets, det))
                    else:
                        newDets = dets

                    # callback_controller(frame)

                    frame = vis_detections(frame, cls, newDets[1:], display, thresh=cfg.TEST.CONF_THRESH)
                    # file_name = file_path+str(i)+'.jpg'
                    # cv2.imwrite(file_name, frame)
                    # print('image about to be added to queue')
                    # q.put(file_name)

                    # adding new code below (Ajay)
                    callback_controller(frame)

                    time.sleep(sleepTime)
                    
                    # print('image added to queue')
                    i += 1
#                cv2.imshow('annotations', frame)
#                cv2.waitKey(1)


    except KeyboardInterrupt:
        print("-- Stopped successfully --")

        # When everything done, release the capture
        cap.release()
        cv2.destroyAllWindows()
        sess.close()
        sys.exit(1)		

def main(preprocessDict, video, q, sleepTime, display, callback_controller, cap):
    cfg.TEST.HAS_RPN = True  # Use RPN for proposals

    #args = parse_args()

    modelLocation = os.path.join(cfg.ROOT_DIR, 'trained_model', 'vgg16_faster_rcnn_iter_70000.ckpt')

    # init session
    sess = tf.Session(config=tf.ConfigProto(allow_soft_placement=True))

    # load network
    #net = get_network(args.demo_net)
    if True:#args.demo_net == 'vgg16':
        net = vgg16(batch_size=1)
    #'3' is number of classes!! change if necessary!!
    net.create_architecture(sess, "TEST", 3,
                          tag='default', anchor_scales=[8, 16, 32])

    # load model
    #saver = tf.train.Saver(write_version=tf.train.SaverDef.V1)
    saver = tf.train.Saver()
    saver.restore(sess, modelLocation)
    print('\n\nLoaded network {:s}'.format(modelLocation))

    # capture video and tag
    capture_and_tag(sess, net, preprocessDict, video, q, sleepTime, display, callback_controller, cap)
    #plt.show()

if __name__ == '__main__':

    pass
#    video = cfg.TEST.INPUT_VIDEO
#    main(video, preprocessDict)
