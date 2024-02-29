from PyQt5 import QtCore, QtGui, QtWidgets
import sys
from matplotlib.pylab import date2num
import pyqtgraph as pg
import akshare as ak
import pandas as pd


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(30, 10, 731, 521))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 30))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.verticalLayout.addWidget(chart())

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))


class CandlestickItem(pg.GraphicsObject):
    def __init__(self, data):
        pg.GraphicsObject.__init__(self)
        self.data = data  ## data: time, open, close, min, max
        self.generatePicture()

    def generatePicture(self):
        self.picture = QtGui.QPicture()
        p = QtGui.QPainter(self.picture)
        p.setPen(pg.mkPen('w'))
        w = (self.data[1][0] - self.data[0][0]) / 3.
        for (t, open, close, min, max) in self.data:
            p.drawLine(QtCore.QPointF(t, min), QtCore.QPointF(t, max))
            if open > close:
                p.setBrush(pg.mkBrush('g'))
            else:
                p.setBrush(pg.mkBrush('r'))
            p.drawRect(QtCore.QRectF(t - w, open, w * 2, close - open))
        p.end()

    def paint(self, p, *args):
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QtCore.QRectF(self.picture.boundingRect())


def chart():
    # 所有金融期货(中金所主力合约)具体合约
    cffex_text = ak.match_main_contract(symbol="cffex")
    cffex_text = cffex_text.split(',')
    print(cffex_text)
    df = ak.futures_zh_minute_sina(symbol=cffex_text[2], period="1")
    df_new = pd.DataFrame(df, columns=['datetime', 'open', 'close', 'low', 'high'])
    df_new.columns = ['time', 'open', 'close', 'min', 'max']
    # 转换为日期格式
    df_new['time'] = pd.to_datetime(df_new['time'])
    # 将日期列作为行索引
    df_new.set_index("time", inplace=True)
    print("df_new:")
    print(df_new)
    df_new = df_new.loc["2024-02-24 14:00:00": "2024-02-29 14:00:00", :]
    print("df_new:")
    print(df_new)

    data_list = []
    axis = []
    for time, row in df_new.iterrows():
        # 将时间转换为数字
        # date_time = time.strftime("%Y-%m-%d %H:%M:%S", datetime)
        t = date2num(time)
        # t = dict(enumerate(datetime))
        open, close, min, max = row['open'], row['close'], row['min'], row['max']
        datas = (t, open, close, min, max)
        data_list.append(datas)
        axis.append(t)
    # print(axis)
    axis_dict = dict(enumerate(axis))
    item = CandlestickItem(data_list)
    plt = pg.PlotWidget()
    # print(plt.getAxis('bottom'))
    plt.addItem(item)
    plt.showGrid(x=True, y=True)
    return plt


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()  # 创建窗体对象
    ui = Ui_MainWindow()  # 创建PyQt设计的窗体对象
    ui.setupUi(MainWindow)  # 调用PyQt窗体的方法对窗体对象进行初始化设置
    MainWindow.show()  # 显示窗体,使控件可见(默认是隐藏)
    sys.exit(app.exec_())  # 程序关闭时退出进程