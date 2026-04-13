'''
DragElement.py
Created 15 Feb 2026

PyQt widget class definition for drag-and-drop widgets
'''

import os
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
        Empty in base class - no additional parameters to report
        '''
        return {
            'name': self.name,
            'x': self.mat_bb.left(),
            'y': self.mat_bb.top()
        }

    def from_params(self, param_dict):
        '''
        Update params based on dict (same schema as params())
        '''
        self.name = param_dict['name']
        self.mat_bb.moveTopLeft(
            param_dict['x'],
            param_dict['y']
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
    def __init__(self, name, x, y, text, font_path, color, parent=None):
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
        bitmap_str = None
        for char in self.text:
            bitmap_str = self.font_.glyph(char).draw() if bitmap_str is None else bitmap_str.concat(self.font_.glyph(char).draw())
        self.bitmap = bitmap_str.todata()
        self.mat_bb = QRect(x, y, len(self.bitmap[0]), len(self.bitmap))

    def params(self): 
        '''
        Return custom param dict
        '''
        return {
            'name': self.name,
            'x': self.mat_bb.left(),
            'y': self.mat_bb.top(),
            'text': self.text,
            'font': self.font_path,
            'color': self.color.rgb()
        }
    
    def from_params(self, param_dict):
        '''
        Update params based on dict (same schema as params())
        '''
        self.name = param_dict['name']
        self.mat_bb.moveTopLeft(QPoint(
            int(param_dict['x']),
            int(param_dict['y'])
        ))
        self.text = param_dict['text']
        self.font_path = param_dict['font']
        self.font_ = Font(self.font_path)
        self.color = QColor.fromString(param_dict['color'])

    def draw(self):
        '''
        Output widget bitmap array
        '''
        bitmap_str = None
        for char in self.text:
            bitmap_str = self.font_.glyph(char).draw() if bitmap_str is None else bitmap_str.concat(self.font_.glyph(char).draw())
        self.bitmap = np.array(bitmap_str.todata(2))

        output_array = np.where(self.bitmap == 1, self.color, None)
        return output_array

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
            'name': self.name,
            'x': self.mat_bb.left(),
            'y': self.mat_bb.top(),
            'path': self.img_path,
            'width': self.w,
            'height': self.h
        }
    
    def from_params(self, param_dict):
        '''
        Update params based on dict (same schema as params())
        '''
        self.name = param_dict['name']
        self.mat_bb.moveTopLeft(QPoint(
            int(param_dict['x']),
            int(param_dict['y'])
        ))
        self.w = int(param_dict['width'])
        self.h = int(param_dict['height'])
        self.img_path = param_dict['path']
        self.img_array = self.process_image_from_path()