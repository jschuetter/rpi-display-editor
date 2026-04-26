'''
RPi Display Editor
main.py
Created 15 Feb 2026

This application is designed to be a lightweight desktop editor for developing modules for my Raspberry Pi LED matrix display project.
'''

import sys

from src.Editor import Editor

SRC_DIR = "./src/"


# Code from PyQt tutorial at
# https://doc.qt.io/qtforpython-6/gettingstarted.html#create-your-first-qt-application-with-qt-widgets
if __name__ == "__main__":
    sys.path.append(SRC_DIR)

    app = Editor()