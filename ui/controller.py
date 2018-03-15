from Tkinter import *
from view import View
# from datacontroller import DataController
# import numpy
from PIL import ImageTk,Image
# import base64
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
import os
# import eventlet
# import threading
# from threading import Thread
# import subprocess
import skvideo.io


class Controller:
    def __init__(self, master):
        self.view = View(master)
        self.initialize_top_frame_controller(self.view.top_frame)
        self.initialize_btm_frame_controller(self.view.btm_frame)
        # self.datacontroller = DataController(self)
        self.init_client()
        self.timer_id = 0

    def initialize_top_frame_controller(self, frame):
        self.view.value_of_combobox_server = self.view.combobox_server.get()
        self.view.combobox_server.bind("<<ComboboxSelected>>", self.change_server)
        vcmd = frame.register(self.validate_video_path)
        self.view.entry_video_path.configure(validate="key", validatecommand=(vcmd, '%P'))
        self.view.button_process.configure(command=self.process_video_frame)
        self.view.button_terminate.configure(command=self.terminate_app)

    def initialize_btm_frame_controller(self, frame):
        self.view.combobox_video_white_hot.bind("<<ComboboxSelected>>", self.change_video_hot)
        self.view.combobox_video_border.bind("<<ComboboxSelected>>", self.change_video_border)
        self.dict_crop_info = {}

    def validate_video_path(self, new_text):
        # print 'Video path:', new_text
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
            # adding new code below
            self.preprocess_video()

    def change_server(self, event):
        self.view.value_of_combobox_server = self.view.combobox_server.get()
        print 'Server changed to:', self.view.value_of_combobox_server

    def change_video_hot(self, event):
        self.view.value_of_combobox_video_white_hot = self.view.combobox_video_white_hot.get()
        print 'Video white hot option selected as:', self.view.value_of_combobox_video_white_hot

        # created the below model after debugging the existing web app model
        if self.view.value_of_combobox_video_white_hot == LABEL_NO:
            self.dict_crop_info[DICT_CROP_VIDEOHOT_KEY] = True
        elif self.view.value_of_combobox_video_white_hot == LABEL_YES:
            self.dict_crop_info[DICT_CROP_VIDEOHOT_KEY] = False

    def change_video_border(self, event):
        self.view.value_of_combobox_video_border = self.view.combobox_video_border.get()
        print 'Video border option selected as:', self.view.value_of_combobox_video_border
        self.dict_crop_info[DICT_CROP_VIDEOBORDER_KEY] = self.view.value_of_combobox_video_border

        # set deafault option for video hot if nothing selected there
        if DICT_CROP_VIDEOHOT_KEY not in self.dict_crop_info:
            self.dict_crop_info[DICT_CROP_VIDEOHOT_KEY] = False

        if self.view.value_of_combobox_video_border == LABEL_NO:
            # eventlet.spawn(self.display_loader)
            # eventlet.spawn(self.send_crop_info)
            # self.display_loader()
            self.send_crop_info()
            # self.stop_now = False
            # Thread(target=self.display_loader).start()
            # Thread(target=self.send_crop_info).start()

    def terminate_app(self):
        print('Terminating the SPOT app')
        self.view.master.destroy()

    def popup_terminate(self):
        print('Opening popup window')
        self.view.popwin = Toplevel()
        self.view.popwin.geometry('{}x{}'.format(400, 100))
        self.view.popwin.wm_title("Confirm termination")

        l = Label(self.view.popwin, text="Do you want to terminate the application?")
        l.grid(row=0, column=0)

        b = Button(self.view.popwin, text="Yes", command=self.terminate_app)
        b.grid(row=1, column=0)

        # b = Button(self.view.popwin, text="No", command=self.view.popwin.destroy)
        b = Button(self.view.popwin, text="No", command=self.close_popup_window)
        b.grid(row=1, column=1)

    def close_popup_window(self):
        self.view.popwin.destroy()

    # def display_loader(self, n=0):
    #     print('Displaying loader for now...')
    #     print('pwd:',os.getcwd())
    #     loader_image = 'ui/loader.gif'
    #     self.view.loader_image_path = os.path.join(os.getcwd(), loader_image)
    #     print('loader_image_path:', self.view.loader_image_path)
    #     self.view.canvas_loader_image = PhotoImage(file=self.view.loader_image_path)
    #     self.view.canvas.create_image(0, 0, image=self.view.canvas_loader_image, anchor=NW)
    #     self.view.master.update()
    #     # self.timer_id = self.view.master.after(100, self.display_loader, n + 1)

    def display_loader(self):
        frame = 0
        while self.stop_now is False:
            try:
                # global photo
                # global frame
                # global label
                loader_image = 'ui/loader.gif'
                self.view.loader_image_path = os.path.join(os.getcwd(), loader_image)
                self.view.canvas_loader_image = PhotoImage(
                    file=self.view.loader_image_path,
                    format="gif - {}".format(frame)
                )

                self.view.canvas.create_image(0, 0, image=self.view.canvas_loader_image, anchor=CENTER)
                self.view.master.update()

                frame = frame + 1

            except Exception as e:
                frame = 0
                self.display_loader()
                break

    ##new methods as per the previous app
    def init_client(self):
        global vh, local_vh
        vh = start_client.get_video_client()
        local_vh = start_local_client.get_client()

    def preprocess_video(self):
        # payload = json.loads(request.get_data().decode('utf-8'))
        ###################
        #################
        global vh, video_path, local_vh
        # try:
        #     video_path = int(payload['video_path'])
        # except:
        #     video_path = payload['video_path']

        video_path = self.view.text_video_path

        # change path as per requirement to display live webcam frame
        if video_path == '0' or video_path == '1':
            video_path = int(video_path)

        # update video and app path in remote client
        # vh.video_file = self.view.text_video_path
        # vh.app_path = self.view.text_video_path

        # update video and app path in local client
        local_vh.update_paths(video_path, None)

        cap = cv2.VideoCapture(0)
        print cap.isOpened()

        # print cv2.imread('frames/first.jpg')
        if cap.isOpened():
            ret, frame = cap.read()
            if frame is not None:
                self.update_canvas_frame(frame)
            else:
                print ('No frame received!')
        else:
            ret = False
        # curr = int(round(time.time() * 1000))
        # first_img = 'frames/first.jpg'
        # first_img_path = os.path.join('frames/', first_img)
        # cv2.imwrite('frames', frame)

        if video_path is '0' or '1':
            cap.release()

        # return first_img + '?r=' + str(curr)

    def update_canvas_frame(self, frame):
        self.view.canvas.config(width=frame.shape[1], height=frame.shape[0])
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)  # convert colors from BGR to RGBA
        self.view.current_frame = Image.fromarray(cv2image)
        self.view.canvas_photo = ImageTk.PhotoImage(image=self.view.current_frame)
        self.view.canvas.create_image(0, 0, image=self.view.canvas_photo, anchor=NW)

        if self.timer_id > 0:
            self.view.master.after_cancel(self.timer_id)
            self.view.canvas.delete(ALL)

        self.view.master.update() # refresh page to update canvas frame

    def send_crop_info(self):
        global vh, local_vh, server_type
        print("sending crop info..")
        # self.display_loader()

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

        print ("event finished")
        # return 'True'

    def callback(self, frame):
        print("updating new frame after callback from machine learning library...")
        self.stop_now = True
        self.update_canvas_frame(frame)

