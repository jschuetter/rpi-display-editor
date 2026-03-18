'''
Editor.py
1 Mar 2026

Holds source code for editor GUI
'''

import sys
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtWidgets import QApplication, QWidget, QLayoutItem, QGridLayout, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit

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
        self.app_layout = QGridLayout(self.container)

        # Add matrix emulator
        self.matrix = MatrixEmulatorWidget(px_size=8, pitch=2)

        # DEV TESTING WIDGETS
        self.matrix.fill('blue')
        img = ImgWidget(15, 0, "./cloudy-day.png", 15, 15)
        self.matrix.add_widget(img)
        self.selected = img

        # Add editor menus
        self.layers_menu = ScrollableMenu(QVBoxLayout, 200)

        # Properties Menu
        self.properties_menu = ScrollableMenu(QVBoxLayout, 1000)
        # Widget position
        self.propmenu_pos = QWidget()
        self.propmenu_pos.setFixedWidth(100)
        self.propmenu_pos.setLayout(QHBoxLayout())
        self.propmenu_pos.layout().addWidget(QLabel("Pos: "))
        self.prop_pos_x = QLineEdit()
        self.prop_pos_y = QLineEdit()
        self.prop_pos_x.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.prop_pos_y.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.propmenu_pos.layout().addWidget(self.prop_pos_x)
        self.propmenu_pos.layout().addWidget(self.prop_pos_y)
        self.properties_menu.addWidget(self.propmenu_pos)

        self.add_menu = ScrollableMenu(QHBoxLayout, None, 200)

        self.app_layout.addWidget(self.layers_menu, 0, 0)
        self.app_layout.addWidget(self.matrix, 0, 1)
        self.app_layout.addWidget(self.properties_menu, 0, 2)
        self.app_layout.addWidget(self.add_menu, 1, 1)

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
        self.prop_pos_x.setText(str(sw_pos.x()))
        self.prop_pos_y.setText(str(sw_pos.y()))
        # self.propsLabel.setText('\n'.join(vars(sw)))
        # print(vars(sw))