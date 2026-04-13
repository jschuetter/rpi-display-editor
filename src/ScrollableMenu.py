'''
ScrollableMenu.py
1 Mar 2026

Definition for ScrollableMenu class - to simplify/abstract design of overall app.
This class is intended to be used for creating sidebar menus
'''

from PySide6.QtWidgets import QWidget, QLayout, QGridLayout, QBoxLayout, QHBoxLayout, QVBoxLayout, QScrollArea
# from PySide6.QtGui import QPainter, QColor, QBrush, QPen
# from PySide6.QtCore import Qt, QSize, QRect, QPoint

class ScrollableMenu(QScrollArea):
    ALLOWED_LAYOUTS = (QGridLayout, QBoxLayout, QHBoxLayout, QVBoxLayout)
    def __init__(self, layout=QVBoxLayout, min_width = None, min_height = None, parent=None):
        '''
        Class constructor
        
        :param layout: Layout type for the menu. May be QGridLayout, QBoxLayout, QHBoxLayout, or QVBoxLayout. Defaults to QVBoxLayout.
        '''
        super().__init__(parent)
        if layout not in self.ALLOWED_LAYOUTS: 
            raise ValueError("layout attr must be one of " + self.ALLOWED_LAYOUTS)
        # Create constituent widgets
        self.container = QWidget()
        self.container.setLayout(layout())
        if min_width: 
            self.container.setMinimumWidth(min_width)
        else: 
            self.container.setMinimumWidth(self.sizeHint().width())
        if min_height: 
            self.container.setMinimumHeight(min_height)
        else: 
            self.container.setMinimumHeight(self.sizeHint().height())
        
        # Set up basic layout
        self.setWidget(self.container)

    def addWidget(self, item: QWidget, *args):
        '''
        Pass addItem calls to layout attr with additional args
        (e.g. for QGridLayout)
        '''
        self.container.layout().addWidget(item, *args)
        self.container.adjustSize()

    def addLayout(self, item: QLayout, *args):
        '''
        Pass addItem calls to layout attr with additional args
        (e.g. for QGridLayout)
        '''
        self.container.layout().addLayout(item, *args)
        self.container.adjustSize()

    def removeWidget(self, item, *args):
        '''
        Pass removeWidget calls to layout attr with additional args
        '''
        self.container.layout().removeWidget(item, *args)
        item.removeLater()
        self.container.adjustSize()

    def empty(self):
        '''
        Remove all child widgets
        '''
        clearLayout(self.container.layout())
        
def clearLayout(layout):
    '''
    Clears a layout of all child widgets (and deletes them)
    Helper definition for recursion in empty()
    '''
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()
        else: 
            # Item is a layout
            clearLayout(item.layout())