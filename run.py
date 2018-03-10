#from Tkinter import Tk
# import sys
# sys.path.insert(0, r'/from/root/directory/src')

#from src.final.ui.controller import Controller

from Tkinter import Tk
import os
import sys
# sys.path.insert(0, r'D:\Research\teamcore_project\project-AI_for_conservation\python-workspace-AI_for_conservation/src')
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))
# from ui.controller import Controller
from ui.controller import Controller


def initialize_ui():
    root = Tk()
    print 'start app'

    global controller
    controller = Controller(root)

    root.mainloop()


initialize_ui()




