'''
Matrix.py
Created 15 Feb 2026

PyQt widget class definition for emulating LED matrix behavior
'''

import os
from copy import deepcopy
from bdfparser import Font
from PIL import Image
import numpy as np

from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtGui import QPainter, QColor, QBrush, QPen
from PySide6.QtCore import Qt, QSize, QRect, QPoint

class MatrixWidget(QWidget):
    def __init__(self, px_size=12, pitch=3, rows=32, cols=64, parent=None):
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
        pen = QPen("red")
        pen.setWidth(3)
        painter.setPen(pen)
        painter.setBrush(QBrush(QColor(0, 0, 0, 0)))
        painter.drawRect(0, 0, self.width(), self.height())
        

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
    def __init__(self, px_size=12, pitch=3, parent=None):
        super().__init__(px_size=px_size, pitch=pitch, parent=parent)
        # List of widgets currently displaying
        # First element is None to represent background layer
        self.widgets = [ None ]
        # Index of currently selected widget
        self.selected_idx = None
        # Store pixel values of widgets, with layer 0 being background
        self._layers = [ deepcopy(self._colors) ]
        # Accept drop events
        self.setAcceptDrops(True)
        # QRect defining matrix bounds
        self.bb = QRect(0, 0, self.cols, self.rows)
        
        # List of listener instances for selected widget updates
        self.selected_listeners = []

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
        disp_bb = self._mat_to_disp(widget.mat_bb)
        widget.setGeometry(disp_bb)
        widget.setMinimumSize(widget.size())
        # widget.move(disp_bb.topLeft())
        widget.update()
        self.update_colors()

    def set_selected(self, idx):
        '''
        Sets selected widget index
        '''
        self.get_selected().show_box = False
        self.selected_idx = idx
        self.get_selected().show_box = True
        self.trigger_selected_update()
        self.update()

    def get_selected(self):
        '''
        Returns selected widget
        '''
        return self.widgets[self.selected_idx]
    
    def subscribe_selected_updates(self, callback):
        '''
        Subscribes a callback method from another object to be called
        when selected widget is updated
        
        :param callback: Method to execute on updates
        '''
        self.selected_listeners.append(callback)

    def unsubscribe_selected_updates(self, callback):
        '''
        Unsubscribes a callback method from another object to be called
        when selected widget is updated
        
        :param callback: Method to execute on updates
        '''
        self.selected_listeners.remove(callback)
    
    def trigger_selected_update(self, *args, **kwargs): 
        '''
        Calls listeners for selected widget update
        '''
        for listener in self.selected_listeners:
            listener(*args, **kwargs)
            

    #region draw_methods

    def _draw_array(self, widget):
        '''
        Draw widget onto array object with matrix dimensions
        
        :param widget: widget to draw (attributes specify location)
        :return np.array:
        '''
        output_array = np.full((len(self._colors), len(self._colors[0])), QColor("invalid"))
        # Handle array bounds
        draw_rect = self.bb.intersected(widget.mat_bb)
        # Define widget intersection
        wbm_top = max(0, -widget.mat_bb.top())
        wbm_left = max(0, -widget.mat_bb.left())
        widget_bitmap = widget.draw()[
            wbm_top : min(widget.mat_bb.height(), self.rows - widget.mat_bb.top()),
            wbm_left : min(widget.mat_bb.width(), self.cols - widget.mat_bb.left())
        ]
        
        output_array[
            draw_rect.top() : draw_rect.bottom() + 1,
            draw_rect.left() : draw_rect.right() + 1, 
            ] = widget_bitmap
        
        # Update widget display box
        # widget.disp_bb = self._mat_to_disp(widget.mat_bb)
        widget.setGeometry(self._mat_to_disp(widget.mat_bb))
        # widget.move(self._mat_to_disp(widget.mat_bb).topLeft())
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
        if bounding_rect is not None: 
            row_range = range(
                max(0, bounding_rect.top()), 
                min(self.rows, bounding_rect.bottom())
                )
            col_range = range(
                max(0, bounding_rect.left()), 
                min(self.cols, bounding_rect.right())
                )
        for layer in (self._layers):
            for row in row_range:
                for col in col_range:
                    color = layer[row][col]
                    if color is None: 
                        # Construct invalid color -- so it's ignored
                        color = QColor()
                    if color.isValid():
                        self._colors[row][col] = color

    def fill(self, color):
        '''
        Override parent fill 
        
        :param color: String or QColor object representing the fill color
        '''
        qcolor = color if isinstance(color, QColor) else QColor(color)
        self._layers[0] = np.full((len(self._colors), len(self._colors[0])), qcolor)

    #endregion
    #region drag_methods

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
        e.source().dragging = False
        e.accept()
    
    def dragMoveEvent(self, e):
        '''
        Logic to execute when widget is dragged around on the matrix
        '''
        pos = e.pos()
        widget = e.source()
        translate = pos - widget.drag_start # Calculate translation
        w_idx = self.widgets.index(widget)
        self.set_selected(w_idx)
        # Update position attributes of widget itself
        src_bb = widget.mat_bb  # Store original position of matrix
        # Convert display coordinates to matrix coordinates
        translate_mat = self._disp_pos_to_mat(translate)
        widget.mat_bb.moveTo(translate_mat)
        # Update corresponding draw layer
        self._layers[w_idx] = self._draw_array(widget)
        # Update matrix
        # Find bounding box of source + destination
        update_bb = src_bb.united(widget.mat_bb)
        # self.update_colors(update_bb)
        # self.update(update_bb)
        self.update_colors()
        self.update()

        # ADD GUI UPDATE EVENT TRIGGER HERE
        self.trigger_selected_update()

    def update_widget(self, w): 
        '''
        Manually update selected widget
        '''
        # Update corresponding draw layer
        w_idx = self.widgets.index(w)
        self._layers[w_idx] = self._draw_array(w)
        # Update matrix
        self.update_colors()
        self.update()

    def update_selected(self): 
        '''
        Same as update_widget, but implicitly uses selected widget
        '''
        self._layers[self.selected_idx] = self._draw_array(self.get_selected())
        # Update matrix
        self.update_colors()
        self.update()

    def move_widget_up(self, idx):
        '''
        Moves the widget at the specified index up one (if possible)
        '''
        if idx < 0 or idx >= len(self.widgets):
            raise IndexError("Widget index out of range")
        elif idx <= 1: 
            # Do nothing if already at start of list
            # Ignore None object at position 0 (represents background)
            return
        
        self.widgets.insert(idx-1, self.widgets.pop(idx))
        self._layers.insert(idx-1, self._layers.pop(idx))
        if idx == self.selected_idx: 
            self.selected_idx = idx-1
        elif idx-1 == self.selected_idx: 
            self.selected_idx = idx
        self.trigger_selected_update()
        self.update_colors()
        self.update()

    def move_widget_down(self, idx):
        '''
        Moves the widget at the specified index down one (if possible)
        '''
        if idx < 0 or idx >= len(self.widgets):
            raise IndexError("Widget index out of range")
        elif idx == len(self.widgets) - 1: 
            # Do nothing if already at end of list
            return
        
        self.widgets.insert(idx+1, self.widgets.pop(idx))
        self._layers.insert(idx+1, self._layers.pop(idx))
        if idx == self.selected_idx: 
            self.selected_idx = idx+1
        elif idx+1 == self.selected_idx: 
            self.selected_idx = idx
        self.trigger_selected_update()
        self.update_colors()
        self.update()

    #endregion
#endregion