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
from PySide6.QtCore import Qt, QSize, QMimeData, QRect

class DragWidget(QWidget):
    '''
    Parent class for various widget types 
    '''
    def __init__(self, parent=None):
        super().__init__(parent)
        # self.x = x
        # self.y = y
        self.mat_bb = QRect()  # Bounding box for matrix emulator
        self.disp_bb = QRect()  # Bounding box for GUI display
        self.show_box = True
        # Generate random color for bounding box
        self.color = QColor.fromHsl(rand.randint(0, 360), 100, 60)
        # Bounding box attributes
        # self.bb = QRect()
        # Set default min. size
        # self.setMinimumSize(self.bb)

    def mousePressEvent(self, e):
        '''
        Handler for drag events        
        '''
        if e.button() == Qt.LeftButton:
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
        pen = QPen(self.color)
        pen.setWidth(5)
        painter.setPen(pen)
        painter.setBrush(QBrush(QColor(0, 0, 0, 0)))  # Transparent fill
        painter.drawRect(self.disp_bb)

class TextWidget(DragWidget):
    def __init__(self, x, y, text, font_path, color, parent=None):
        '''
        Docstring for __init__
        
        :param x: x-coordinate of text
        :param y: y-coordinate of widget
        :param text: text string of widget
        :param font_path: path to font file
        :param color: color of text, as string or QColor
        '''
        super().__init__(x, y, parent)
        self.font = Font(font_path)
        self.color = color if isinstance(color, QColor) else QColor(color)
        self.text = text
        bitmap_str = None
        for char in self.text:
            bitmap_str = self.font.glyph(char).draw() if bitmap_str is None else bitmap_str.concat(self.font.glyph(char).draw())
        self.bitmap = bitmap_str.todata()
        self.mat_bb = QRect(x, y, len(self.bitmap[0]), len(self.bitmap))

    def draw(self):
        '''
        Output widget bitmap array
        '''
        bitmap_str = None
        for char in self.text:
            bitmap_str = self.font.glyph(char).draw() if bitmap_str is None else bitmap_str.concat(self.font.glyph(char).draw())
        self.bitmap = bitmap_str.todata()

        output_array = np.where(self.bitmap == 1, self.color, None)
        return output_array

class ImgWidget(DragWidget):
    def __init__(self, x, y, path, w=None, h=None, parent=None):
        '''
        Docstring for __init__
        
        :param x: x-coordinate of text
        :param y: y-coordinate of widget
        :param path: path to image file
        :param w: width to scale the image (optional)
        :param h: height to scale the image (optional)
        '''
        super().__init__(parent)
        img = Image.open(path)
        if w is not None and h is not None:
            img.thumbnail((w, h), Image.LANCZOS)
        elif w is not None and h is None:
            img.thumbnail((w, w), Image.LANCZOS)
        elif w is None and h is not None:
            img.thumbnail((h, h), Image.LANCZOS)
        
        img_array_t = np.array(img)  # temp image array
        # Process image array into QColor values
        out = np.empty(img_array_t.shape[:2], dtype=object)
        for i in range(img_array_t.shape[0]):
            for j in range(img_array_t.shape[1]):
                out[i, j] = QColor(*img_array_t[i, j])

        self.img_array = out
        print(self.img_array.shape)
        self.mat_bb = QRect(x, y, self.img_array.shape[1], self.img_array.shape[0])

    def draw(self): 
        '''
        Output widget bitmap array
        '''
        return self.img_array