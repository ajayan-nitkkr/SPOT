from Tkinter import *
from view import View
from datacontroller import DataController
import numpy
from PIL import ImageTk,Image
import base64
try:
    # Python2
    # import Tkinter as tk
    from urllib2 import urlopen
except ImportError:
    # Python3
    # import tkinter as tk
    from urllib.request import urlopen
import start_client
import start_local_client
import cv2
import time
from string_values import *


class Controller:
    def __init__(self, master):
        self.view = View(master)
        self.initialize_top_frame_controller(self.view.top_frame)
        self.initialize_btm_frame_controller(self.view.btm_frame)
        # self.datacontroller = DataController(self)
        self.init_client()

    def initialize_top_frame_controller(self, frame):
        print 'initialize topframe controller'
        self.view.value_of_combobox_server = self.view.combobox_server.get()
        self.view.combobox_server.bind("<<ComboboxSelected>>", self.change_server)
        vcmd = frame.register(self.validate_video_path)
        self.view.entry_video_path.configure(validate="key", validatecommand=(vcmd, '%P'))
        self.view.button_process.configure(command=self.process_video_frame)

    # def initialize_center_frame_controller(self, frame):
    #     print 'initialize centerframe controller'
    #     self.view.canvas.bind("<Configure>", self.resize_frame_dimensions)

    def initialize_btm_frame_controller(self, frame):
        print 'initialize btmframe controller'
        self.view.combobox_video_white_hot.bind("<<ComboboxSelected>>", self.change_video_hot)
        self.view.combobox_video_border.bind("<<ComboboxSelected>>", self.change_video_border)
        self.dict_crop_info = {}

    def validate_video_path(self, new_text):
        print 'Video path:', new_text
        # if not new_text:
        #     self.text_video_path = ''
        #     return True

        try:
            self.view.text_video_path = new_text
            return True
        except ValueError as e:
            print 'Value Error:', e
            return False

    def process_video_frame(self):
        if self.view.text_video_path == '':
            print 'Please mention your video path'
        else:
            print 'Processing video at:', self.view.text_video_path
            # video_frame_data = self.datacontroller.preprocess_video()
            # self.get_frame()
            self.view.combobox_video_white_hot.configure(state='readonly')
            self.view.combobox_video_border.configure(state='readonly')
            #adding new code below
            self.preprocess_video()

    def change_server(self, event):
        self.view.value_of_combobox_server = self.view.combobox_server.get()
        print 'Server:', self.view.value_of_combobox_server

    def change_video_hot(self, event):
        self.view.value_of_combobox_video_white_hot = self.view.combobox_video_white_hot.get()
        print 'Video white hot?:', self.view.value_of_combobox_video_white_hot
        self.dict_crop_info[DICT_CROP_VIDEOHOT_KEY] = self.view.value_of_combobox_video_white_hot

    def change_video_border(self, event):
        self.view.value_of_combobox_video_border = self.view.combobox_video_border.get()
        print 'Video borders?:', self.view.value_of_combobox_video_border
        self.dict_crop_info[DICT_CROP_VIDEOBORDER_KEY] = self.view.value_of_combobox_video_border
        if self.view.value_of_combobox_video_border == LABEL_NO:
            self.send_crop_info()

    # def resize_frame_dimensions(self, event):


    ##new methods as per the previous app
    def init_client(self):
        global vh, local_vh
        vh = start_client.get_video_client()
        local_vh = start_local_client.get_client()

    def preprocess_video(self):
        # payload = json.loads(request.get_data().decode('utf-8'))
        print 'reached preprocess_video code (the prev one)!'
        global vh, video_path, local_vh
        # try:
        #     video_path = int(payload['video_path'])
        # except:
        #     video_path = payload['video_path']

        video_path = self.view.text_video_path

        # update video and app path in reomte client
        vh.video_file = self.view.text_video_path
        vh.app_path = self.view.text_video_path

        # update video and app path in local client
        local_vh.update_paths(video_path, None)

        cap = cv2.VideoCapture(video_path)
        # print cap.isOpened()
        # print cv2.imread('frames/first.jpg')
        ret, frame = cap.read()
        curr = int(round(time.time() * 1000))
        # first_img = 'frames/first.jpg'
        # first_img_path = os.path.join('frames/', first_img)
        # cv2.imwrite('frames', frame)
        self.update_canvas_frame(frame)

        # return first_img + '?r=' + str(curr)

    def update_canvas_frame(self, frame):
        print 'get jpg image'
        self.view.canvas.config(width=frame.shape[1], height=frame.shape[0])
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)  # convert colors from BGR to RGBA
        self.view.current_frame = Image.fromarray(cv2image)
        self.view.canvas_photo = ImageTk.PhotoImage(image=self.view.current_frame)
        self.view.canvas.create_image(0, 0, image=self.view.canvas_photo, anchor=NW)
        self.view.master.update() #refresh page to update canvas frame


    def send_crop_info(self):
        global vh, local_vh, server_type
        print("sending crop info..")

        # payload = json.loads(request.get_data().decode('utf-8'))
        self.dict_crop_info[DICT_CROP_CROPTOP_KEY] = 0;
        self.dict_crop_info[DICT_CROP_CROPLEFT_KEY] = 0;
        self.dict_crop_info[DICT_CROP_CROPBOTTOM_KEY] = self.view.current_frame.height;
        self.dict_crop_info[DICT_CROP_CROPRIGHT_KEY] = self.view.current_frame.width;
        crop_info = self.dict_crop_info
        server_type = self.view.value_of_combobox_server

        if server_type == LABEL_LOCAL_SERVER:
            """ TODO :initiate processing for local server """
            print("Initiating requests for local server")
            local_vh.update_crop_info(crop_info)
            start_local_client.start_video_client(self.callback)

        else:
            """ Initiate processing for remote (Azure Advanced) server """
            print("Initiating requests for remote Azure Advanced server")

        print ("event spawn finished")
        # return 'True'

    def callback(self, frame):
        print("updating new frame after callback...")
        self.update_canvas_frame(frame)

