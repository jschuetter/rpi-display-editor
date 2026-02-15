'''
Matrix.py
Created 15 Feb 2026

PyQt widget class definition for emulating LED matrix behavior
'''

import os
from bdfparser import Font
from PIL import Image
import numpy as np

from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtGui import QPainter, QColor, QBrush
from PySide6.QtCore import Qt, QSize, QRectF

class MatrixWidget(QWidget):
    def __init__(self, rows=32, cols=64, px_size=12, pitch=3, parent=None):
        super().__init__(parent)
        self.rows = rows
        self.cols = cols
        self.px_size = px_size
        self.pitch = pitch
        self._colors = [[QColor("black") for _ in range(self.cols)] for _ in range(self.rows)]
        self.setMinimumSize(self._calc_size())

    def _calc_size(self):
        '''
        Calculate minimum widget size based on attribute values
        '''
        w = self.cols * self.px_size + (self.cols-1) * self.pitch
        h = self.rows * self.px_size + (self.rows-1) * self.pitch
        return QSize(w, h)

    def sizeHint(self):
        return self._calc_size()
    
    def paintEvent(self, event):
        '''
        Override default paintEvent() method
        '''
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        d = self.px_size
        s = self.pitch
        # Draw matrix row-wise
        for r in range(self.rows):
            y = r * (d + s)
            for c in range(self.cols):
                x = c * (d + s)
                color = self._colors[r][c]
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(color))
                painter.drawEllipse(QRectF(x, y, d, d))  # Note: could change to rect grid here

    def _cell_rect(self, row, col):
        '''
        Return the QRectF object for the given cell coordinate
        
        :param row: row index of cell
        :param col: col index of cell
        '''
        d = self.px_size
        s = self.pitch
        x = col * (d + s)
        y = row * (d + s)
        return QRectF(x, y, d, d)
    
    def set_px(self, row, col, color):
        '''
        Set the color of an individual pixel in the matrix
        
        :param row: row index of cell
        :param col: column index of cell
        :param color: QColor object or string value of color
        '''
        if not (
            0 <= row < self.rows and 
            0 <= col < self.cols
        ):
            raise IndexError("Pixel coord out of range.")
        qcolor = color if isinstance(color, QColor) else QColor(color)
        self._colors[row][col] = qcolor
        self.update(self._cell_rect(row, col).toRect())  # Update only changed area

    def fill(self, color):
        '''
        Fill matrix with color
        
        :param color: String or QColor object representing the fill color
        '''
        qcolor = color if isinstance(color, QColor) else QColor(color)
        for row in range(self.rows):
            for col in range(self.cols): 
                self.set_px(row, col, qcolor)

    def draw_text(self, x, y, text, font_path, color):
        '''
        Draw text to the matrix
        
        :param text: String to print on matrix
        :param font: Path of .bdf font file to print
        :param color: String or QColor value to use for text
        '''
        font = Font(font_path)
        bitmap_str = None
        for char in text:
            bitmap_str = font.glyph(char).draw() if bitmap_str is None else bitmap_str.concat(font.glyph(char).draw())
        matrix_data = bitmap_str.todata()
        for row_n in range(len(matrix_data)):
            row = y + row_n
            row_data = matrix_data[row_n]
            for col_n in range(len(row_data)):
                if row_data[col_n] == '1':
                    col = x + col_n
                    # Ignore overflowing boundaries
                    try:
                        self.set_px(row, col, color)
                    except IndexError:
                        pass

    def draw_img(self, path, x, y, w=None, h=None):
        '''
        Draw an image file to matrix
        
        :param path: path of .bmp file
        :param x: x-coordinate of icon
        :param y: y-coordinate of icon
        :param w: width of image to output
        :param h: height of image to output
        '''
        # if not os.path.splitext(path) == '.bmp':
        #     raise ValueError("Icon file must be in .bmp format")
        
        img = Image.open(path)
        if w is not None and h is not None:
            img.thumbnail((w, h), Image.LANCZOS)
        elif w is not None and h is None:
            img.thumbnail((w, w), Image.LANCZOS)
        elif w is None and h is not None:
            img.thumbnail((h, h), Image.LANCZOS)
        
        # img = img.convert("RGBA")
        img_array = np.array(img)
        for row_n in range(img_array.shape[0]):
            row = img_array[row_n]
            for col_n in range(img_array.shape[1]):
                try:
                    self.set_px(row_n, col_n, QColor(*img_array[row_n][col_n]))
                except IndexError:  # Ignore overflow
                    pass