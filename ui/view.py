from Tkinter import *
import ttk
import numpy
from PIL import Image, ImageTk
from string_values import *


class View:
    def __init__(self, root):
        # print 'initializing view...'
        self.create_window(root)
        self.create_containers()

    def create_window(self, root):
        self.master = root
        self.master.geometry('{}x{}'.format(1400, 1000))
        self.master.title(LABEL_SPOT)
        self.master.configure(background=COLOR_GRAY)

    def create_containers(self):
        # create all of the main containers
        top_frame_style = ttk.Style()
        top_frame_style.configure('My.TFrame', background=COLOR_GREEN)
        self.top_frame = ttk.Frame(self.master, style='My.TFrame', padding=(10, 3, 10, 3))
        self.center_frame = Frame(self.master, bg=COLOR_GRAY, pady=3)
        btm_frame_style = ttk.Style()
        btm_frame_style.configure('My.TFrame', background=COLOR_GREEN)
        self.btm_frame = ttk.Frame(self.master, style='My.TFrame', padding=(10, 3, 10, 3))

        # layout all of the main containers
        self.top_frame.grid(row=0)
        self.center_frame.grid(row=1, sticky="nsew")
        self.btm_frame.grid(row=2, sticky="nsew")

        self.master.rowconfigure(0, weight=1)
        self.master.rowconfigure(1, weight=10)
        self.master.rowconfigure(2, weight=2)
        self.master.columnconfigure(0, weight=1)

        # create internal containers
        self.create_top_frame_widgets(self.top_frame)
        self.create_center_frame_widgets(self.center_frame)
        self.create_btm_frame_widgets(self.btm_frame)

    def create_top_frame_widgets(self, frame):
        # create frames inside top frame
        server_frame_style = ttk.Style()
        server_frame_style.configure('My.TFrame',background=COLOR_GREEN)
        self.server_frame = ttk.Frame(frame, style='My.TFrame', padding=(3, 3, 3, 3))
        self.video_path_frame = ttk.Frame(frame, style='My.TFrame', padding=(10, 3, 10, 3))

        # create the widgets for the top frame
        self.label_server = Label(self.server_frame, text=LABEL_SERVER, bg=COLOR_GREEN)
        self.combobox_server = ttk.Combobox(self.server_frame, values=(LABEL_LOCAL_SERVER), state="readonly")
        self.label_video_path = Label(self.video_path_frame, text=LABEL_VIDEO_PATH, bg=COLOR_GREEN)
        self.entry_video_path = Entry(self.video_path_frame)
        # TODO: remove below line later, added just for testing
        self.entry_video_path.insert(END, '/tf_serving_deployment/gui/demo.mp4')
        self.button_process = Button(frame, text=LABEL_PROCESS)
        self.button_terminate = Button(frame, text=LABEL_TERMINATE)

        # layout the frames inside the top frame
        self.server_frame.grid(row=0, column=0, sticky="nsew")
        self.video_path_frame.grid(row=0, column=1, sticky="nsew")

        # layout the widgets in the top frame
        self.label_server.grid(row=0, column=0, sticky="nsew")
        self.combobox_server.grid(row=0, column=1, sticky="nsew")
        self.label_video_path.grid(row=0, column=0, sticky="nsew")
        self.entry_video_path.grid(row=0, column=1, sticky="nsew")
        self.button_process.grid(row=0, column=2, sticky="nsew")
        self.button_terminate.grid(row=0, column=3, sticky="nsew")

        # assign different weights to the widgets for relative size in the top frame
        frame.grid_columnconfigure(0, weight=1, uniform="foo")
        frame.grid_columnconfigure(1, weight=3, uniform="foo")
        frame.grid_columnconfigure(2, weight=1, uniform="foo")
        frame.grid_columnconfigure(3, weight=1, uniform="foo")
        self.video_path_frame.grid_columnconfigure(0, weight=1, uniform="foo")
        self.video_path_frame.grid_columnconfigure(1, weight=3, uniform="foo")
        # frame.grid_columnconfigure(4, weight=1, uniform="foo")

        # set default values of widgets
        self.combobox_server.current(0)
        self.text_video_path = ''

    def create_center_frame_widgets(self, frame):
        # layout the frames inside the center frame
        self.left_canvas = Canvas(frame, width=500, height=500, bg=COLOR_GRAY, highlightbackground=COLOR_GRAY)
        self.left_canvas.grid(row=0, column=0)

        self.right_canvas = Canvas(frame, width=500, height=500, bg=COLOR_GRAY, highlightbackground=COLOR_GRAY)
        self.right_canvas.grid(row=0, column=1)

        # assign different weights to the widgets for relative size in the center frame
        frame.grid_columnconfigure(0, weight=1, uniform="foo")
        frame.grid_columnconfigure(1, weight=1, uniform="foo")

    def create_btm_frame_widgets(self, frame):
        # create frames inside top frame
        video_hot_frame_style = ttk.Style()
        video_hot_frame_style.configure('My.TFrame',background=COLOR_GREEN)
        self.video_hot_frame = ttk.Frame(frame, style='My.TFrame', padding=(3, 3, 3, 3))
        self.video_border_frame = ttk.Frame(frame, style='My.TFrame', padding=(3, 3, 3, 3))

        # create the widgets for the bottom frame
        self.label_video_white_hot= Label(self.video_hot_frame, text=LABEL_VIDEO_HOT, bg=COLOR_GREEN)
        self.combobox_video_white_hot = ttk.Combobox(self.video_hot_frame, values=(LABEL_YES, LABEL_NO), state="readonly")
        self.label_video_border = Label(self.video_border_frame, text=LABEL_VIDEO_BORDER, bg=COLOR_GREEN)
        self.combobox_video_border = ttk.Combobox(self.video_border_frame, values=(LABEL_YES, LABEL_NO), state="readonly")

        # layout the frames inside the bottom frame
        self.video_hot_frame.grid(row=0, column=0, sticky="nsew")
        self.video_border_frame.grid(row=1, column=0, sticky="nsew")

        # layout the widgets in the bottom frame
        self.label_video_white_hot.grid(row=0, column=0, sticky="nsew")
        self.combobox_video_white_hot.grid(row=0, column=1, sticky="nsew")
        self.label_video_border.grid(row=1, column=0, sticky="nsew")
        self.combobox_video_border.grid(row=1, column=1, sticky="nsew")

        # assign different weights to the widgets for relative size in the bottom frame
        frame.grid_columnconfigure(0, weight=1, uniform="foo")
        frame.grid_columnconfigure(1, weight=1, uniform="foo")
        self.video_hot_frame.grid_columnconfigure(0, weight=1, uniform="foo")
        self.video_hot_frame.grid_columnconfigure(1, weight=1, uniform="foo")
        self.video_border_frame.grid_columnconfigure(0, weight=1, uniform="foo")
        self.video_border_frame.grid_columnconfigure(1, weight=1, uniform="foo")

        # disable combobox in the beginning
        self.combobox_video_white_hot.configure(state='disabled')
        self.combobox_video_border.configure(state='disabled')
