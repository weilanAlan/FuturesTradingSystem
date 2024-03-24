from PyQt5.Qt import *
from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg

color_table = {'line_desc': 'green'}

#  成交量
class VolItem(pg.GraphicsObject):
    def __init__(self, data):
        pg.GraphicsObject.__init__(self)
        self.data = data
        self.generatePicture()

    def generatePicture(self):
        self.picture = QtGui.QPicture()
        p = QtGui.QPainter(self.picture)
        w = 0.25
        for (t, open, close, vol) in self.data:
            if open > close:
                p.setPen(pg.mkPen(color_table['line_desc']))
                p.setBrush(pg.mkBrush(color_table['line_desc']))
                p.drawRect(QtCore.QRectF(t - w, 0, w * 2, vol))
            else:
                p.setPen(pg.mkPen('r'))
                p.drawLines(QtCore.QLineF(QtCore.QPointF(t - w, 0), QtCore.QPointF(t - w, vol)),
                            QtCore.QLineF(QtCore.QPointF(t - w, vol), QtCore.QPointF(t + w, vol)),
                            QtCore.QLineF(QtCore.QPointF(t + w, vol), QtCore.QPointF(t + w, 0)),
                            QtCore.QLineF(QtCore.QPointF(t + w, 0), QtCore.QPointF(t - w, 0)))
        p.end()

    def paint(self, p, *args):
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QtCore.QRectF(self.picture.boundingRect())