from PyQt5.Qt import *
from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg


class SegmenttickItem(pg.GraphicsObject):
    def __init__(self, data):
        pg.GraphicsObject.__init__(self)
        self.data = data
        self.generatePicture()

    def generatePicture(self):
        self.picture = QtGui.QPicture()
        p = QtGui.QPainter(self.picture)
        for (t, val) in self.data:
            if val > 0.0:
                p.setPen(pg.mkPen('r'))
                p.drawLine(QtCore.QPointF(t, 0), QtCore.QPointF(t, val))
            else:
                p.setPen(pg.mkPen('g'))
                p.drawLine(QtCore.QPointF(t, 0), QtCore.QPointF(t, val))
        p.end()

    def paint(self, p, *args):
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QtCore.QRectF(self.picture.boundingRect())