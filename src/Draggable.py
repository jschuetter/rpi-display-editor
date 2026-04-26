'''
DragElement.py
Created 15 Feb 2026

PyQt widget class definition for drag-and-drop widgets
'''

import os
from pathlib import Path
from bdfparser import Font
from PIL import Image
import numpy as np
import random as rand

from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QDrag, QColor, QPainter, QPen, QBrush
from PySide6.QtCore import Qt, QSize, QMimeData, QRect, QPoint

class DragWidget(QWidget):
    '''
    Parent class for various widget types 
    '''
    BOX_COLOR = QColor(255, 145, 0)
    def __init__(self, name, parent=None):
        super().__init__(parent)
        self.name = name
        self.mat_bb = QRect()  # Bounding box for matrix emulator
        self.show_box = False
        # Drag properties
        self.dragging = False
        self.drag_start = QPoint()

    def params(self): 
        '''
        Return custom param dict
        Should include all mandatory arguments for __init__(), in order
        Must have format 'key': {'value', 'type'}
        '''
        return {
            'name': {
                'value': self.name,
                'type': 'str',
            },
            'x': {
                'value': self.mat_bb.left(),
                'type': 'int',
            },
            'y': {
                'value': self.mat_bb.top(),
                'type': 'int',
            },
        }

    def from_params(self, param_dict):
        '''
        Update params based on dict (same schema as params())
        '''
        self.name = param_dict['name']['value']
        self.mat_bb.moveTopLeft(
            param_dict['x']['value'],
            param_dict['y']['value']
        )

    @classmethod
    def init_params(cls, param_dict):
        '''
        Instantiate object on params dict
        '''
        return cls(
            param_dict['name']['value'],
            param_dict['x']['value'],
            param_dict['y']['value'],
        )

    def mousePressEvent(self, e):
        '''
        Handler for drag events        
        '''
        if e.button() == Qt.LeftButton:
            # Set attributes
            self.dragging = True
            self.drag_start = e.pos()
            
            drag = QDrag(self)
            mimeData = QMimeData()
            drag.setMimeData(mimeData)
            drag.exec_(Qt.MoveAction)

    def draw(self):
        '''
        Template method for subclasses - by default, do nothing
        Should output bitmap array (position-agnostic) of widget
        '''
        pass

    def paintEvent(self, event):
        '''
        Override default paintEvent() method
        Custom paint event to show box around widget when selected
        '''
        # If show_box is False, skip draw
        if not self.show_box: 
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(self.BOX_COLOR)
        pen.setWidth(5)
        painter.setPen(pen)
        painter.setBrush(QBrush(QColor(0, 0, 0, 0)))  # Transparent fill
        painter.drawRect(0, 0, self.width(), self.height())

class TextWidget(DragWidget):
    FONTS_PATH = './rpi-display-src/fonts'
    
    def __init__(self, name, x, y, text, font_path=os.path.join(FONTS_PATH, 'basic/4x6.bdf'), color="#ffffff", parent=None):
        '''
        Docstring for __init__
        
        :param x: x-coordinate of text
        :param y: y-coordinate of widget
        :param text: text string of widget
        :param font_path: path to font file
        :param color: color of text, as string or QColor
        '''
        super().__init__(name, parent)
        self.font_path = font_path
        self.font_ = Font(font_path)
        self.color = color if isinstance(color, QColor) else QColor(color)
        self.text = text
        self.bitmap = None
        self.update_bitmap()
        self.mat_bb = QRect(int(x), int(y), len(self.bitmap[0]), len(self.bitmap))

    def update_bitmap(self): 
        '''
        Update bitmap attribute using current attribute values
        '''
        bitmap_str = None
        for char in self.text:
            bitmap_str = self.font_.glyph(char).draw() if bitmap_str is None else bitmap_str.concat(self.font_.glyph(char).draw())
        self.bitmap = bitmap_str.todata(2)
        return self.bitmap
    
    def update_bb(self): 
        '''
        Update bounding box based on current bitmap
        '''
        self.mat_bb.setHeight(len(self.bitmap))
        self.mat_bb.setWidth(len(self.bitmap[0]))
        return (self.mat_bb.width(), self.mat_bb.height())

    def params(self): 
        '''
        Return custom param dict
        '''
        return {
            'name': {
                'value': self.name,
                'type': 'str',
            },
            'x': {
                'value': self.mat_bb.left(),
                'type': 'int',
            },
            'y': {
                'value': self.mat_bb.top(),
                'type': 'int',
            },
            'text': {
                'value': self.text,
                'type': 'str',
            },
            'font': {
                'value': self.font_path,
                'type': 'enum',
                'options': self.get_fonts_list(),
            },
            'color': {
                'value': self.color.name(),
                'type': 'str',
            }
        }
    
    def from_params(self, param_dict):
        '''
        Update params based on dict (same schema as params())
        '''
        self.name = param_dict['name']['value']
        self.text = param_dict['text']['value']
        self.font_path = os.path.join(self.FONTS_PATH, param_dict['font']['value'])
        self.font_ = Font(self.font_path)
        self.color = QColor.fromString(param_dict['color']['value'])
        self.update_bitmap()
        self.update_bb()
        self.mat_bb.moveTopLeft(QPoint(
            int(param_dict['x']['value']),
            int(param_dict['y']['value'])
        ))
    
    @classmethod
    def init_params(cls, param_dict):
        '''
        Instantiate object on params dict
        '''
        return cls(
            param_dict['name']['value'],
            param_dict['x']['value'],
            param_dict['y']['value'],
            param_dict['text']['value'],
            param_dict['font']['value'],
            param_dict['color']['value'],
        )

    def draw(self):
        '''
        Output widget bitmap array
        '''
        bitmap_str = None
        for char in self.text:
            bitmap_str = self.font_.glyph(char).draw() if bitmap_str is None else bitmap_str.concat(self.font_.glyph(char).draw())
        self.bitmap = np.array(bitmap_str.todata(2))
        self.update_bb()

        output_array = np.where(self.bitmap == 1, self.color, None)
        return output_array
    
    def get_fonts_list(self): 
        '''
        Get list of font paths from specified directory
        '''
        font_path = Path(self.FONTS_PATH)
        font_files = font_path.rglob("*.bdf")
        return [os.path.relpath(f, font_path) for f in font_files]

class ImgWidget(DragWidget):
    def __init__(self, name, x, y, path, width=None, height=None, parent=None):
        '''
        Docstring for __init__
        
        :param x: x-coordinate of text
        :param y: y-coordinate of widget
        :param path: path to image file
        :param w: width to scale the image (optional)
        :param h: height to scale the image (optional)
        '''
        super().__init__(name, parent)
        self.img_path = path
        self.w = width
        self.h = height

        self.img_array = self.process_image_from_path()
        self.mat_bb = QRect(x, y, self.img_array.shape[1], self.img_array.shape[0])

    def process_image_from_path(self):
        '''
        Process image into array object
        '''
        img = Image.open(self.img_path)
        if self.w is not None and self.h is not None:
            img.thumbnail((self.w, self.h), Image.LANCZOS)
        elif self.w is not None and self.h is None:
            img.thumbnail((self.w, self.w), Image.LANCZOS)
        elif self.w is None and self.h is not None:
            img.thumbnail((self.h, self.h), Image.LANCZOS)
        
        img_array_t = np.array(img)  # temp image array
        # Process image array into QColor values
        out = np.empty(img_array_t.shape[:2], dtype=object)
        for i in range(img_array_t.shape[0]):
            for j in range(img_array_t.shape[1]):
                out[i, j] = QColor(*img_array_t[i, j])
        
        return out

    def draw(self): 
        '''
        Output widget bitmap array
        '''
        return self.img_array
    
    def params(self): 
        '''
        Return custom param dict
        '''
        return {
            'name': {
                'value': self.name,
                'type': 'str',
            },
            'x': {
                'value': self.mat_bb.left(),
                'type': 'int',
            },
            'y': {
                'value': self.mat_bb.top(),
                'type': 'int',
            },
            'path': {
                'value': self.img_path,
                'type': 'str',
            },
            'width': {
                'value': self.w,
                'type': 'str',
            },
            'height': {
                'value': self.h,
                'type': 'str',
            },
        }
    
    def from_params(self, param_dict):
        '''
        Update params based on dict (same schema as params())
        '''
        self.name = param_dict['name']['value']
        self.mat_bb.moveTopLeft(QPoint(
            int(param_dict['x']['value']),
            int(param_dict['y']['value'])
        ))
        self.w = int(param_dict['width']['value'])
        self.h = int(param_dict['height']['value'])
        self.img_path = param_dict['path']['value']
        self.img_array = self.process_image_from_path()
        
    @classmethod
    def init_params(cls, param_dict):
        '''
        Instantiate object on params dict
        '''
        return cls(
            param_dict['name']['value'],
            int(param_dict['x']['value']),
            int(param_dict['y']['value']),
            param_dict['path']['value'],
            param_dict['width']['value'],
            param_dict['height']['value'],
        )