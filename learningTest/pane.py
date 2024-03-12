from PyQt5.Qt import *
from learningTest.plotwidget_test import Ui_MainWindow
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from pyqtgraph import PlotWidget


class Pane(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.plot_sth()

    def plot_sth(self):
        self.graphicsView.plot([1, 2, 3, 4, 5], pen='r', symbol='o')


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Pane()
    window.show()  # 显示窗体,使控件可见(默认是隐藏)
    sys.exit(app.exec_())  # 程序关闭时退出进程