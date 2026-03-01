'''
Editor.py
1 Mar 2026

Holds source code for editor GUI
'''

import sys
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtWidgets import QApplication, QWidget, QLayoutItem, QGridLayout, QHBoxLayout, QVBoxLayout, QLabel

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
        self.layersMenu = ScrollableMenu(QVBoxLayout, 200)

        self.propertiesMenu = ScrollableMenu(QVBoxLayout, 200)
        self.posLabel = QLabel("Pos: ")
        # self.propsLabel = QLabel()
        self.propertiesMenu.addWidget(self.posLabel)
        # self.propertiesMenu.addWidget(self.propsLabel)

        self.addMenu = ScrollableMenu(QHBoxLayout, None, 200)

        self.appLayout.addWidget(self.layersMenu, 0, 0)
        self.appLayout.addWidget(self.matrix, 0, 1)
        self.appLayout.addWidget(self.propertiesMenu, 0, 2)
        self.appLayout.addWidget(self.addMenu, 1, 1)

        # DEBUG TESTING
        self.matrix.selected_idx = -1
        self.matrix.subscribe_selected_updates(self.update_props)

        self.container.show()

        sys.exit(self.exec())

    def update_props(self):
        '''
        Update properties window based on state of matrix
        '''
        sw = self.matrix.get_selected()
        sw_pos = sw.mat_bb.topLeft()
        self.posLabel.setText(f"Pos: {sw_pos.x()}, {sw_pos.y()}")
        # self.propsLabel.setText('\n'.join(vars(sw)))
        # print(vars(sw))