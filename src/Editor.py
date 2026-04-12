'''
Editor.py
1 Mar 2026

Holds source code for editor GUI
'''

import sys
from PySide6 import QtCore
from PySide6.QtCore import Qt, QPoint, Slot
from PySide6.QtWidgets import QApplication, QWidget, QLayoutItem, QGridLayout, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont

from src.Matrix import MatrixWidget, MatrixEmulatorWidget
from src.Draggable import TextWidget, ImgWidget
from src.ScrollableMenu import ScrollableMenu

class Editor(QApplication): 
    def __init__(self):
        super().__init__([])
        # Create application layout
        self.container = QWidget()
        self.applayout = QGridLayout(self.container)

        # Add matrix emulator
        self.matrix = MatrixEmulatorWidget(px_size=8, pitch=2)

        # DEV TESTING WIDGETS
        self.matrix.fill('blue')
        img = ImgWidget("cloud-icon", 15, 0, "./cloudy-day.png", 15, 15)
        self.matrix.add_widget(img)
        text = TextWidget("hello-world", 32, 0, "Hello, World!", "./rpi-display-src/fonts/basic/4x6.bdf", "white")
        self.matrix.add_widget(text)

        # Add editor menus
        ## Layers menu
        self.layers_menu = ScrollableMenu(QVBoxLayout, 400)

        ## Properties Menu
        self.properties_menu = ScrollableMenu(QVBoxLayout)

        # Widget name
        self.prop_name = QLineEdit()
        self.prop_name.editingFinished.connect(self.push_props)
        self.properties_menu.addWidget(QLabel("Name: "))
        self.properties_menu.addWidget(self.prop_name)

        # Widget position
        self.propmenu_pos = QWidget()
        self.propmenu_pos.setFixedWidth(100)
        self.propmenu_pos.setLayout(QHBoxLayout())
        self.propmenu_pos.layout().addWidget(QLabel("Pos: "))
        self.prop_pos_x = QLineEdit()
        self.prop_pos_y = QLineEdit()
        self.prop_pos_x.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.prop_pos_y.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.prop_pos_x.editingFinished.connect(self.push_props)
        self.prop_pos_y.editingFinished.connect(self.push_props)
        self.propmenu_pos.layout().addWidget(self.prop_pos_x)
        self.propmenu_pos.layout().addWidget(self.prop_pos_y)
        self.properties_menu.addWidget(self.propmenu_pos)

        ## Widget add menu
        self.add_menu = ScrollableMenu(QHBoxLayout, None, 200)

        self.applayout.addWidget(self.layers_menu, 0, 0)
        self.applayout.addWidget(self.matrix, 0, 1)
        self.applayout.addWidget(self.properties_menu, 0, 2)
        self.applayout.addWidget(self.add_menu, 1, 1)

        # DEBUG TESTING
        self.matrix.selected_idx = -1
        self.matrix.subscribe_selected_updates(self.pull_props)
        self.matrix.subscribe_selected_updates(self.update_layers)

        self.container.showMaximized()

        sys.exit(self.exec())

    @Slot(str)
    def push_props(self): 
        '''
        Push properties defined in editor properties menu to
        currently selected widget
        '''
        sw = self.matrix.get_selected()
        sw.name = self.prop_name.text()
        x = self.prop_pos_x.text()
        y = self.prop_pos_y.text()
        x = 0 if x == '' else int(x)
        y = 0 if y == '' else int(y)

        sw.mat_bb.moveTopLeft(QPoint(x, y))
        self.matrix.update_selected()

        
    def pull_props(self):
        '''
        Update properties window based on state of matrix
        '''
        sw = self.matrix.get_selected()
        self.prop_name.setText(sw.name)
        sw_pos = sw.mat_bb.topLeft()
        self.prop_pos_x.setText(str(sw_pos.x()))
        self.prop_pos_y.setText(str(sw_pos.y()))

    def update_layers(self): 
        '''
        Update layers menu with current widget list
        '''
        self.layers_menu.empty()
        for w_idx in range(1, len(self.matrix.widgets)): # Start loop at 1 to ignore background widget(?)
            widget = self.matrix.widgets[w_idx]
            list_item = LayersItem(widget.name, self.matrix, w_idx)
            
            if w_idx == self.matrix.selected_idx: 
                pass

            self.layers_menu.addWidget(list_item)

class LayersItem(QWidget):
    FONT = QFont("Arial", 11)
    BTN_WIDTH = 30
    def __init__(self, name, matrix, idx, parent=None):
        super().__init__(parent)
        self.mat = matrix
        self.w_idx = idx
        self.setLayout(QHBoxLayout())
        self.label = QLabel(name)
        self.label.setFont(self.FONT)
        self.setMinimumHeight(self.FONT.pointSize())

        self.up_btn = QPushButton('↑')
        self.up_btn.clicked.connect(lambda: self.mat.move_widget_up(self.w_idx))
        self.up_btn.setMinimumWidth(self.BTN_WIDTH)

        self.down_btn = QPushButton('↓')
        self.down_btn.clicked.connect(lambda: self.mat.move_widget_down(self.w_idx))
        self.down_btn.setMinimumWidth(self.BTN_WIDTH)

        self.layout().addWidget(self.label)
        self.layout().addStretch(20)
        self.layout().addWidget(self.up_btn)
        self.layout().setStretch(2, 1)
        self.layout().addWidget(self.down_btn)
        self.layout().setStretch(3, 1)

    def mousePressEvent(self, e):
        '''
        Update matrix selected_idx when clicked
        '''
        if e.button() == Qt.LeftButton:
            self.mat.set_selected(self.w_idx)

    def paintEvent(self, event):
        '''
        Override default paintEvent() method
        Custom paint event to show box around widget when selected
        '''
        # If not selected, skip draw
        if not self.w_idx == self.mat.selected_idx: 
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(QColor(255,145,0))
        pen.setWidth(3)
        painter.setPen(pen)
        painter.setBrush(QBrush(QColor(0, 0, 0, 0)))  # Transparent fill
        painter.drawRect(0, 0, self.width(), self.height())