from Tkinter import Tk
import os
import sys
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))
from ui.controller import Controller


def initialize_ui():
    root = Tk()
    print 'starting the app...'

    # global controller
    controller = Controller(root)

    root.mainloop()


initialize_ui()




