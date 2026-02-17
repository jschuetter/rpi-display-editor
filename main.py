'''
RPi Display Editor
main.py
Created 15 Feb 2026

This application is designed to be a lightweight desktop editor for developing modules for my Raspberry Pi LED matrix display project.
'''

import sys
from PySide6 import QtCore, QtWidgets, QtGui

from src.Matrix import MatrixWidget, MatrixEmulatorWidget
from src.Draggable import TextWidget, ImgWidget

SRC_DIR = "./src/"


# Code from PyQt tutorial at
# https://doc.qt.io/qtforpython-6/gettingstarted.html#create-your-first-qt-application-with-qt-widgets
if __name__ == "__main__":
    sys.path.append(SRC_DIR)

    app = QtWidgets.QApplication([])

    matrix = MatrixEmulatorWidget()
    matrix.fill('blue')
    img = ImgWidget(15, 0, "./cloudy-day.png", 15, 15)
    matrix.add_widget(img)
    # matrix.draw_text(0, 0, "Hello, world!", "rpi-display-src/fonts/basic/4x6.bdf", "yellow")
    # matrix.draw_img("./cloudy-day.png", 15, 0, 15, 15)
    # widget.resize(800, 600)
    matrix.show()

    sys.exit(app.exec())