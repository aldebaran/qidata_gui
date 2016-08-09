# -*- coding: utf-8 -*-

from PySide.QtGui import QGraphicsItem, QPen, QColor, QGraphicsRectItem
from PySide.QtCore import Signal, QObject, Qt

class MetadataRectItem(QGraphicsRectItem, QObject):
    """
    Item to show the position of an object on an image.
    """

    # ───────
    # Signals

    isSelected = Signal()
    isMoved = Signal(list)
    isResized = Signal(list)
    suppressionRequired = Signal()

    # ──────────
    # Contructor

    def __init__(self, coordinates, parent=None):
        """
        QiDataObjectRectItem constructor

        :param coordinates:  Object position
        :param parent:  Parent of this widget
        """
        x_min, y_min = coordinates[0]
        x_max, y_max = coordinates[1]
        QGraphicsRectItem.__init__(self, x_min, y_min, x_max-x_min, y_max-y_min)
        QObject.__init__(self, parent)
        self.setFlags(QGraphicsItem.ItemIsFocusable)
        self.setPen(QPen(QColor(255,0,0)))

    # ───────
    # Methods

    def select(self):
        """
        Focus this specific item.

        Calling this method will trigger the isSelected signal.
        """
        # This will trigger `focusInEvent` and the corresponding slot will be called
        self.setFocus()

    # ─────
    # Slots

    def focusInEvent(self, event):
        pen = QPen(QColor(255,255,255)) # Color in white
        pen.setWidth(3) # Increase rectangle width
        self.setPen(pen) # Apply changes
        self.isSelected.emit() # Trigger isSelected signal

    def focusOutEvent(self, event):
        self.setPen(QPen(QColor(255,0,0))) # Color in red

    def keyReleaseEvent(self, event):
        event.accept()

        # Resize the box depending on the hit key
        r = self.rect()
        if event.key() == Qt.Key_Up: # UP
            r.setTop(r.top()-5)
            r.setBottom(r.bottom()+5)
        elif event.key() == Qt.Key_Down: # DOWN
            r.setTop(r.top()+5)
            r.setBottom(r.bottom()-5)
        elif event.key() == Qt.Key_Right: # RIGHT
            r.setLeft(r.left()-5)
            r.setRight(r.right()+5)
        elif event.key() == Qt.Key_Left: # LEFT
            r.setLeft(r.left()+5)
            r.setRight(r.right()-5)
        elif event.key() == Qt.Key_Delete: # DEL
            self.suppressionRequired.emit()
            return

        self.setRect(r)

        # Emit new coordinates
        self.isResized.emit(
            [
                [r.left(), r.top()],
                [r.right(), r.bottom()]
            ])

    def mouseMoveEvent(self, event):
        # Update box position in the scene
        p2 = event.scenePos()
        p1 = event.lastScenePos()
        dx = p2.x()-p1.x()
        dy = p2.y()-p1.y()
        r = self.rect()
        r.setTop(r.top() + dy)
        r.setBottom(r.bottom() + dy)
        r.setLeft(r.left() + dx)
        r.setRight(r.right() + dx)
        self.setRect(r)

    def mousePressEvent(self, event):
        # This give the focus to the item
        if event.button() == Qt.RightButton:
            self.suppressionRequired.emit()
        event.accept()

    def mouseReleaseEvent(self, event):
        # When mouse is released, emit coordinates in case it was moved
        r = self.rect()
        self.isMoved.emit(
            [
                [r.left(), r.top()],
                [r.right(), r.bottom()]
            ])

    def wheelEvent(self, event):
        # Resize the box depending on wheel direction
        r = self.rect()
        step = event.delta() / 120
        r.setTop(r.top()-5*step)
        r.setBottom(r.bottom()+5*step)
        r.setLeft(r.left()-5*step)
        r.setRight(r.right()+5*step)
        self.setRect(r)

        # Emit new coordinates
        self.isResized.emit(
            [
                [r.left(), r.top()],
                [r.right(), r.bottom()]
            ])
