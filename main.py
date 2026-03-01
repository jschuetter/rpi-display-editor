'''
RPi Display Editor
main.py
Created 15 Feb 2026

This application is designed to be a lightweight desktop editor for developing modules for my Raspberry Pi LED matrix display project.
'''

import sys
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel

from src.Editor import Editor
from src.Matrix import MatrixWidget, MatrixEmulatorWidget
from src.Draggable import TextWidget, ImgWidget
from src.ScrollableMenu import ScrollableMenu

SRC_DIR = "./src/"


# Code from PyQt tutorial at
# https://doc.qt.io/qtforpython-6/gettingstarted.html#create-your-first-qt-application-with-qt-widgets
if __name__ == "__main__":
    sys.path.append(SRC_DIR)

    app = Editor()