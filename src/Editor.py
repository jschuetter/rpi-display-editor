'''
Editor.py
1 Mar 2026

Holds source code for editor GUI
'''

import sys
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtWidgets import QApplication, QWidget, QLayoutItem, QGridLayout, QHBoxLayout, QLabel

from src.Matrix import MatrixWidget, MatrixEmulatorWidget
from src.Draggable import TextWidget, ImgWidget
from src.ScrollableMenu import ScrollableMenu

class Editor(QApplication): 
    def __init__(self):
        super().__init__([])
        # Store selected widget
        self.selected = None 

        # Create application layout
        self.container = QWidget()
        self.appLayout = QGridLayout(self.container)

        # Add matrix emulator
        self.matrix = MatrixEmulatorWidget()
        self.matrix.fill('blue')
        img = ImgWidget(15, 0, "./cloudy-day.png", 15, 15)
        self.matrix.add_widget(img)

        # Add editor menus
        self.layersMenu = ScrollableMenu()

        self.propertiesMenu = ScrollableMenu()
        self.posLabel = QLabel("Pos: ")
        self.propertiesMenu.addWidget(self.posLabel)

        self.addMenu = ScrollableMenu(QHBoxLayout)

        self.appLayout.addWidget(self.layersMenu, 0, 0)
        self.appLayout.addWidget(self.matrix, 0, 1)
        self.appLayout.addWidget(self.propertiesMenu, 0, 2)
        self.appLayout.addWidget(self.addMenu, 1, 1)

        # DEBUG TESTING
        self.matrix.selected_idx = -1

        self.container.show()

        sys.exit(self.exec())

    def update_props(self):
        '''
        Update properties window based on state of matrix
        '''
        sw = self.matrix.get_selected()
        sw_pos = sw.mat_bb.topLeft()
        self.posLabel.setText(f"Pos: {sw_pos.x()}, {sw_pos.y()}")
        print(f"Pos: {sw_pos.x()}, {sw_pos.y()}")