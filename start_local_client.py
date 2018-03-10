from Queue import Queue, Full
from os.path import join
import cv2
import time
import faster_rcnn_local_121.tools.run_faster_rcnn 
import os
import shutil
try:
    import configparser
except:
    import ConfigParser as configparser

class LocalVideoClient(object):

    def __init__(self):
        self.crop_info = None
        self.video_path = None
        self.app_path = None

        self.q = Queue()

        Config = configparser.ConfigParser()
        Config.read("config.ini")
        self.sleep_time = float(Config.get('Server', 'sleep_time'))
        self.display = Config.get('Server', 'display')

    def update_paths(self, video_path, app_path):
        self.video_path = video_path
        self.app_path = app_path

    def update_crop_info(self, crop_info):
        self.crop_info = crop_info
        print(self.crop_info)

    def run(self):
        """ 
            Process the video at video_path
            Add the resulting annotated images in self.q, refer start_client.py: annotate_image()

        """
        shutil.rmtree('results')
        os.mkdir('results')
        print(" Starting processing video at " + str(self.video_path) + " on local server")
        print(self.crop_info)
        faster_rcnn_local_121.tools.run_faster_rcnn.main(self.crop_info, self.video_path, self.q, self.sleep_time, self.display)
        #self.test_results() ## FOR TESTING PURPOSE

    def test_results(self):
        i = 0
        cap = cv2.VideoCapture(self.video_path)
        while i < 200:
            ret, frame = cap.read()
            file_name = 'results/result_local_' + str(i) + '.jpg'
            file_path = join(self.app_path, file_name)
            cv2.imwrite(file_path, frame)
            self.q.put(file_name)
            time.sleep(2)
            i += 1
    
local_vh = LocalVideoClient()

def get_client():
    global local_vh
    return local_vh

def start_video_client():
    print("start video client")
    global local_vh
    local_vh.run()

