'''
Editor.py
1 Mar 2026

Holds source code for editor GUI
'''

import sys
import inspect
from PySide6 import QtCore
from PySide6.QtCore import Qt, QPoint, Slot
from PySide6.QtWidgets import QApplication, QWidget, \
    QGridLayout, QHBoxLayout, QVBoxLayout, \
    QLabel, QLineEdit, QPushButton, QDialog, QComboBox
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
        self.layers_menu = ScrollableMenu(QVBoxLayout, 400, 500)

        ## Properties Menu
        self.properties_menu = ScrollableMenu(QVBoxLayout, None, 500)

        ## Widget add menu
        self.add_menu = ScrollableMenu(QHBoxLayout, None, 200)
        for w in (TextWidget, ImgWidget):
            self.add_menu.addWidget(AddWidgetItem(self, w))

        self.applayout.addWidget(self.layers_menu, 0, 0)
        self.applayout.addWidget(self.matrix, 0, 1)
        self.applayout.addWidget(self.properties_menu, 0, 2)
        self.applayout.addWidget(self.add_menu, 1, 1)

        # DEBUG TESTING
        self.matrix.subscribe_selected_updates(self.pull_props)
        self.matrix.subscribe_selected_updates(self.update_layers)
        self.matrix.subscribe_selected_updates(self.update_props)
        self.matrix.set_selected(1)

        self.container.showMaximized()

        sys.exit(self.exec())

    @Slot(str)
    def push_props(self): 
        '''
        Push properties defined in editor properties menu to
        currently selected widget
        '''
        sw = self.matrix.get_selected()
        sw.from_params({
            key: value.currentText() if type(value) == QComboBox else value.text() 
             for key, value in self.properties_inputs.items()
        })
        params = {
            key: value.currentText() if type(value) == QComboBox else value.text() 
             for key, value in self.properties_inputs.items()
        }

        self.matrix.update_selected()

        
    def pull_props(self):
        '''
        Update properties window based on state of matrix
        '''
        sw = self.matrix.get_selected()
        self.update_props()

    def update_props(self):
        '''
        Update properties menu with current widget list
        '''
        self.properties_menu.empty()
        self.properties_params = self.matrix.get_selected().params()
        self.properties_inputs = {}

        for key, obj in self.properties_params.items(): 
            input_layout = QHBoxLayout()
            input_layout.addWidget(QLabel(f"{key}: "))
            if obj['type'] == 'enum': 
                input = QComboBox()
                if 'options' not in obj: 
                    raise ValueError(f'Parameter {key} of type \'enum\' is missing options list.')

                for opt in obj['options']:
                    input.addItem(opt)
                input.currentIndexChanged.connect(self.push_props)
            else: 
                input = QLineEdit(str(obj['value']))
                input.editingFinished.connect(self.push_props)
            input_layout.addWidget(input)
            self.properties_inputs[key] = input
            self.properties_menu.addLayout(input_layout)
        self.prop_err_lbl = QLabel()
        self.properties_menu.addWidget(self.prop_err_lbl)

    def update_layers(self): 
        '''
        Update layers menu with current widget list
        '''
        self.layers_menu.empty()
        for w_idx in range(len(self.matrix.widgets)-1, 0, -1): # Iterate backward, stop loop at 1 to ignore background widget(?)
            widget = self.matrix.widgets[w_idx]
            list_item = LayersItem(widget.name, self.matrix, w_idx)
            
            if w_idx == self.matrix.selected_idx: 
                pass

            self.layers_menu.addWidget(list_item)

class LayersItem(QWidget):
    '''
    Custom item class for entries in Layers panel
    '''
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

class AddWidgetItem(QPushButton):
    '''
    Custom item class for entries in Add Widget panel
    Param editor_obj stores reference to Editor instance
    for adding widget on acceptw
    '''
    def __init__(self, editor_obj, widget, text=None, icon=None, parent=None):
        if text is None:
            # Default text is widget class name
            text = widget.__name__
            
        if icon: 
            super().__init__(icon, text, parent)
        else: 
            super().__init__(text, parent)

        self.editor = editor_obj
        self.widget = widget
        self.clicked.connect(self.create_modal)

        self.modal = None
        self.widget_args = []

    @Slot(int)
    def create_modal(self):
        '''
        Initialize widget creation modal
        '''
        self.modal = QDialog(self.parent())
        self.param_inputs = []
        modal_layout = QVBoxLayout()
        params = inspect.signature(self.widget.__init__).parameters
        for p_key, p in params.items(): 
            if p_key in ('self', 'parent'): # Skip self & parent params
                continue
            input_layout = QHBoxLayout()
            input_layout.addWidget(QLabel(f"{p_key}: "))
            if p.default != inspect.Parameter.empty:
                input = QLineEdit(p.default)
            else: 
                input = QLineEdit()
            input_layout.addWidget(input)
            self.param_inputs.append(input)
            modal_layout.addLayout(input_layout)
        self.err_lbl = QLabel()
        modal_layout.addWidget(self.err_lbl)

        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.modal.reject)
        accept_btn = QPushButton("Accept")
        accept_btn.clicked.connect(self.verify_and_accept)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(accept_btn)
        modal_layout.addLayout(btn_layout)

        self.modal.setLayout(modal_layout)
        self.modal.open()

    @Slot(int)
    def verify_and_accept(self): 
        '''
        Verify provided arguments; 
        give feedback if needed
        '''
        self.widget_args = []
        for input in self.param_inputs:
            if type(input) == QComboBox: 
                self.widget_args.append(input.currentText())
            else: 
                self.widget_args.append(input.text())
        try: 
            new_widget = self.widget(*self.widget_args)
            self.editor.matrix.add_widget(new_widget)
            self.editor.matrix.set_selected(-1)
            self.modal.accept()
            return 1
        except Exception as e: 
            self.err_lbl.setText(str(e))
            return -1