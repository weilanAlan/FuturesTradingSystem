import pyqtgraph
from PyQt5.Qt import *
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from matplotlib.pylab import date2num
import pyqtgraph as pg
import akshare as ak
import pandas as pd
import mplfinance as mpf
from cycler import cycler  # 用于定制线条颜色
import matplotlib as mpl  # 用于设置曲线参数
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from finalPractice.datadisplay import Ui_MainWindow

# 设置全局变量：合约名称
contract = 'IF2403'

class MyWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyWindow, self).__init__(parent)
        self.setupUi(self)
        self.verticalLayout_kline.addWidget(self.kLineChart())
        # df = ak.futures_zh_minute_sina(symbol=contract, period="1")
        # self.verticalLayout_kline.addWidget(self.draw_kline(df))
        self.comboBox_contract.currentIndexChanged.connect(self.select_contract)

    # 下拉框选择新的合约后触发
    def select_contract(self):
        global contract
        contract = self.comboBox_contract.currentText()
        for i in range(self.verticalLayout_kline.count()):
            self.verticalLayout_kline.itemAt(i).widget().deleteLater()
        self.verticalLayout_kline.addWidget(self.kLineChart())
        # df = ak.futures_zh_minute_sina(symbol=contract, period="1")
        # self.verticalLayout_kline.addWidget(self.draw_kline(self, df))

    def kLineChart(self):
        # 所有金融期货(中金所主力合约)具体合约
        # cffex_text = ak.match_main_contract(symbol="cffex")
        # cffex_text = cffex_text.split(',')
        # print(cffex_text)
        df = ak.futures_zh_minute_sina(symbol=contract, period="1")
        df_new = pd.DataFrame(df, columns=['datetime', 'open', 'close', 'low', 'high'])
        df_new.columns = ['time', 'open', 'close', 'min', 'max']
        # 转换为日期格式
        df_new['time'] = pd.to_datetime(df_new['time'])
        # 将日期列作为行索引
        df_new.set_index("time", inplace=True)
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



'''
    # 返回符合mplfinance要求的数据
    def getDf(self, df):
        df_new = pd.DataFrame(df, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
        df_new.columns = ['date', 'Open', 'High', 'Low', 'Close', 'Volume']
        # 转换为日期格式
        df_new['date'] = pd.to_datetime(df_new['date'])
        # 将日期列作为行索引
        df_new.set_index("date", inplace=True)
        # print(df_new)
        # print(df_new.axes)
        return df_new

    # 画K线图
    def draw_kline(self, df):
        kwargs = dict(
            type='candle',  # type:绘制图形的类型(candle, renko, ohlc, line)
            # mav=(5, 10, 30),  # mav(moving average):均线类型,此处设置5,10,30日线
            # volume=True,  # volume:布尔类型，设置是否显示成交量，默认False
            title='\n candle_line:%s' % (contract),  # title:设置标题
            ylabel='OHLC Candles',  # y_label:设置纵轴主标题
            # ylabel_lower='Shares\nTraded Volume',  # y_label_lower:设置成交量图一栏的标题
            figratio=(15, 10),  # figratio:设置图形纵横比
            figscale=5)  # figscale:设置图形尺寸(数值越大图像质量越高)
        mc = mpf.make_marketcolors(
            up='red',  # up:设置K线线柱颜色，up意为收盘价大于等于开盘价
            down='green',  # down:与up相反，这样设置与国内K线颜色标准相符
            edge='i',  # edge:K线线柱边缘颜色(i代表继承自up和down的颜色)，下同。详见官方文档)
            wick='i',  # wick:灯芯(上下影线)颜色
            # volume='in',  # volume:成交量直方图的颜色
            inherit=True)  # inherit:是否继承，选填
        s = mpf.make_mpf_style(
            gridaxis='both',  # gridaxis:设置网格线位置
            gridstyle='-.',  # gridstyle:设置网格线线型
            y_on_right=False,  # y_on_right:设置y轴位置是否在右
            marketcolors=mc)
        # 设置均线颜色
       # mpl.rcParams['axes.prop_cycle'] = cycler(
       #     color=['dodgerblue', 'deeppink',
       #            'navy', 'teal', 'maroon', 'darkorange',
        #           'indigo'])
        # 设置线宽
        mpl.rcParams['lines.linewidth'] = .5
        # 图形绘制
        # show_nontrading:是否显示非交易日，默认False
        return mpf.plot(self.getDf(df),
                 **kwargs,
                 style=s,
                 show_nontrading=False)


'''


# K线图控件
class CandlestickItem(pg.GraphicsObject):
    def __init__(self, data):
        pg.GraphicsObject.__init__(self)
        self.data = data  ## data: time, open, close, min, max
        self.generatePicture()

    def generatePicture(self):
        self.picture = QtGui.QPicture()
        p = QtGui.QPainter(self.picture)
        p.setPen(pg.mkPen('d'))
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



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.show()  # 显示窗体,使控件可见(默认是隐藏)
    sys.exit(app.exec_())  # 程序关闭时退出进程
