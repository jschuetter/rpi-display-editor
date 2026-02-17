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
from PySide6.QtCore import Qt, QSize, QRect, QPoint

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
                painter.drawEllipse(QRect(x, y, d, d))  # Note: could change to rect grid here

    def _cell_rect(self, row, col):
        '''
        Return the QRect object for the given cell coordinate
        
        :param row: row index of cell
        :param col: col index of cell
        '''
        d = self.px_size
        s = self.pitch
        x = col * (d + s)
        y = row * (d + s)
        return QRect(x, y, d, d)
    
    #region draw_methods

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
        self.update(self._cell_rect(row, col))  # Update only changed area

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

    #endregion

#region emulator
class MatrixEmulatorWidget(MatrixWidget):
    '''
    Extension of MatrixWidget that can store draggable widget objects for live updates
    '''
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        # List of widgets currently displaying
        # First element is None to represent background layer
        self.widgets = [ None ]
        # clone of MatrixWidget._colors with list of pixel color values
        # representing layers bottom-to-top
        self._layers = [ self._colors ]
        # Accept drop events
        self.setAcceptDrops(True)

    def add_widget(self, widget):
        '''
        Add widget to matrix emulator interface
        - Add to widget list
        - Add color layer
        
        :param widget: Widget to add
        '''
        self.widgets.append(widget)
        self._layers.append(self._draw_array(widget))
        widget.setParent(self)
        self.update_colors()

    def _draw_array(self, widget):
        '''
        Draw widget onto array object with matrix dimensions
        
        :param widget: widget to draw (attributes specify location)
        :return np.array:
        '''
        output_array = np.full((len(self._colors), len(self._colors[0])), None)
        print(widget.draw().shape)
        # print(widget.mat_bb.top(), widget.mat_bb.bottom()+1,
        #     widget.mat_bb.left(), widget.mat_bb.right()+1, )
        output_array[
            widget.mat_bb.top():widget.mat_bb.bottom()+1,
            widget.mat_bb.left():widget.mat_bb.right()+1, 
            ] = widget.draw()
        
        # Update widget display box
        widget.disp_bb = self._mat_to_disp(widget.mat_bb)
        widget.update()

        return output_array
    
    def _mat_to_disp(self, mat_bb: QRect):
        '''
        Convert matrix bounding box to display bounding box
        
        :param mat_bb: QRect object in matrix coordinate system
        '''
        x = mat_bb.x() * (self.px_size + self.pitch)
        y = mat_bb.y() * (self.px_size + self.pitch)
        w = mat_bb.width() * (self.px_size + self.pitch)
        h = mat_bb.height() * (self.px_size + self.pitch)
        return QRect(x, y, w, h)
        
    def _disp_pos_to_mat(self, disp_pt: QPoint):
        '''
        Convert coordinate point in display coordinates to matrix coordinates
        
        :param disp_pt: QPoint in display coordinates to convert to matrix coordiantes
        :type disp_pt: QPoint
        '''
        x = disp_pt.x() / (self.px_size + self.pitch)
        y = disp_pt.y() / (self.px_size + self.pitch)
        return QPoint(x, y)

    def update_colors(self, bounding_rect: QRect = None):
        '''
        Update matrix color matrix based on widgets

        :param bounding_rect: QRect object containing the area to update
        '''
        row_range = range(self.rows)
        col_range = range(self.cols)
        if bounding_rect: 
            row_range = range(
                max(0, bounding_rect.top()), 
                max(self.rows, bounding_rect.bottom())
                )
            col_range = range(
                max(0, bounding_rect.left()), 
                max(self.cols, bounding_rect.right())
                )
        for row in row_range:
            for col in col_range:
                # Select color value from highest layer
                layer_idx = 0
                color = None
                while color is None and layer_idx > -(len(self._layers)):
                    layer_idx -= 1
                    color = self._layers[layer_idx][row][col]
                    
                if color is None or not isinstance(color, QColor):
                    raise ValueError(f"Invalid color value at row {row}, col {col}")
                self._colors[row][col] = color

    def update_widget(self, widget_idx):
        '''
        Re-draw widget's color layer
        
        :param widget_idx: Index of widget to update
        '''
        self._layers[widget_idx] = self.widgets[widget_idx].draw()

    def dragEnterEvent(self, e):
        '''
        Override default dragEnterEvent - accept drag
        '''
        e.accept()

    def dropEvent(self, e):
        '''
        Accept drop event
        No need to do anything here - everything is handled in dragMoveEvent
        '''
        e.accept()
    
    def dragMoveEvent(self, e):
        '''
        Logic to execute when widget is dragged around on the matrix
        '''
        pos = e.pos()
        widget = e.source()
        w_idx = self.widgets.index(widget)
        print(f"Move event: {w_idx} to {pos}")
        # Update position attributes of widget itself
        src_bb = widget.mat_bb  # Store original position of matrix
        # Convert display coordinates to matrix coordinates
        mat_pos = self._disp_pos_to_mat(pos)
        widget.mat_bb.moveTo(mat_pos)
        # Update corresponding draw layer
        self._layers[w_idx] = self._draw_array(widget)
        print(w_idx)
        # Update matrix
        # Find bounding box of source + destination
        update_bb = src_bb.united(widget.mat_bb)
        print(update_bb)
        # self.update_colors(update_bb)
        # self.update(update_bb)
        self.update_colors()
        self.update()