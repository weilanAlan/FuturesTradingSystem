from PyQt5.Qt import *
from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg
import akshare as ak
import numpy as np
import pandas as pd
import math
import talib
from typing import Dict, Any
import sys
from pyqtgraph import AxisItem
from finalPractice.datadisplay import Ui_MainWindow

pg.setConfigOption('background', 'k')
pg.setConfigOption('foreground', 'w')

# 设置全局变量：合约名称
contract = 'IF2403'
color_table = {'line_desc': 'green'}


class MyWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyWindow, self).__init__(parent)
        self.setupUi(self)
        # 画k线图、vol、macd、kdj
        graph = PyQtGraphLineWidget()
        graph.set_data(self.getData())
        self.verticalLayout_kline_graph.addWidget(graph)
        # 切换合约
        self.comboBox_contract.currentIndexChanged.connect(self.select_contract)

    # 读取数据
    def getData(self):
        df = ak.futures_zh_minute_sina(symbol=contract, period="1")
        df = pd.DataFrame(df, columns=['datetime', 'close', 'open', 'high', 'low', 'volume'])
        df.columns = ['tradeDate', 'closePrice', 'openPrice', 'highestPrice', 'lowestPrice', 'volume']  # 改列名
        # 计算均线
        close_list = df['closePrice']
        df['ma5'] = talib.MA(close_list, 5)
        df['ma10'] = talib.MA(close_list, 10)
        df['ma20'] = talib.MA(close_list, 20)
        df['ma30'] = talib.MA(close_list, 30)
        df['ma60'] = talib.MA(close_list, 60)
        # 计算指标
        df['DIFF'], df['DEA'], df['MACD'] = talib.MACD(close_list, fastperiod=12, slowperiod=26, signalperiod=9)
        # 计算EMA(12)和EMA(16)
        df['EMA12'] = df['closePrice'].ewm(alpha=2 / 13, adjust=False).mean()
        df['EMA26'] = df['closePrice'].ewm(alpha=2 / 27, adjust=False).mean()
        df['upper'], df['md'], df['lower'] = talib.BBANDS(df['closePrice'], timeperiod=13, nbdevup=2, nbdevdn=2,
                                                          matype=0)
        df['kdj_k'], df['kdj_d'] = talib.STOCH(df['highestPrice'], df['lowestPrice'], df['closePrice'], fastk_period=9,
                                               slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
        df['kdj_j'] = 3 * df['kdj_k'] - 2 * df['kdj_d']
        # 封装数据
        whole_pd_header = ['tradeDate', 'closePrice', 'openPrice', 'highestPrice', 'lowestPrice', 'ma5', 'ma10', 'ma20',
                           'ma30', 'ma60', 'volume', 'DIFF', 'DEA', 'MACD', 'kdj_k', 'kdj_d', 'kdj_j']
        line_data = {
            'title_str': contract,
            # 所有数据
            'whole_header': ['日期', '收盘价', '开盘价', '最高价', '最低价', 'ma5', 'ma10', 'ma20', 'ma30', 'ma60',
                             '持仓量', 'DIFF', 'DEA', 'MACD', 'kdj_k', 'kdj_d', 'kdj_j'],
            'whole_pd_header': whole_pd_header,
            'whole_df': df.loc[:, whole_pd_header],
            # 需要展示的参数
            'required_header': ['日期', '收盘价', '开盘价', '最高价', '最低价', '持仓量'],
            'required_pd_header': ['tradeDate', 'closePrice', 'openPrice', 'highestPrice', 'lowestPrice', 'volume']
        }
        return line_data

    # 下拉框选择新的合约后触发
    def select_contract(self):
        global contract
        contract = self.comboBox_contract.currentText()
        # clear之前画的图
        for i in range(self.verticalLayout_kline_graph.count()):
            self.verticalLayout_kline_graph.itemAt(i).widget().deleteLater()
        graph = PyQtGraphLineWidget()
        graph.set_data(self.getData())
        self.verticalLayout_kline_graph.addWidget(graph)


'''
#  日期横轴控件
class RotateAxisItem(pg.AxisItem):
    def drawPicture(self, p, axisSpec, tickSpecs, textSpecs):
        p.setRenderHint(p.Antialiasing, False)
        p.setRenderHint(p.TextAntialiasing, True)

        #  draw long line along axis
        pen, p1, p2 = axisSpec
        p.setPen(pen)
        p.drawLine(p1, p2)
        p.translate(0.5, 0)  # resolves some damn pixel ambiguity

        #  draw ticks
        for pen, p1, p2 in tickSpecs:
            p.setPen(pen)
            p.drawLine(p1, p2)

        #  draw all text
        p.setPen(self.pen())
        bounding = self.boundingRect().toAlignedRect()
        p.setClipRect(bounding)
        for rect, flags, text in textSpecs:
            # this is the important part
            p.save()
            p.translate(rect.x(), rect.y())
            p.rotate(-30)
            p.drawText(-int(rect.width()), int(rect.height()), int(rect.width()), int(rect.height()), flags, text)
            # restoring the painter is *required*!!!
            p.restore()

'''


# 蜡烛控件
class CandlestickItem(pg.GraphicsObject):
    def __init__(self, data):
        pg.GraphicsObject.__init__(self)
        self.data = data  # data: time, open, close, min, max
        self.generatePicture()

    def generatePicture(self):
        self.picture = QtGui.QPicture()
        p = QtGui.QPainter(self.picture)
        p.setPen(pg.mkPen('d'))
        w = (self.data[1][0] - self.data[0][0]) / 3.
        for (t, open, close, min, max) in self.data:
            p.drawLine(QtCore.QPointF(t, min), QtCore.QPointF(t, max))
            if open < close:
                p.setBrush(pg.mkBrush('r'))
            else:
                p.setBrush(pg.mkBrush('g'))
            p.drawRect(QtCore.QRectF(t - w, open, w * 2, close - open))
        p.end()

    def paint(self, p, *args):
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QtCore.QRectF(self.picture.boundingRect())


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


#  持仓量
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


#  K线图、均线、vol、macd、kdj显示的控件
class PyQtGraphLineWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.init_data()
        self.init_ui()
        pass

    def init_data(self):
        self.color_line = (30, 144, 255)
        self.color_ma_5 = (248, 248, 255)  # 白色
        self.color_ma_10 = (255, 255, 0)  # 纯黄
        self.color_ma_20 = (255, 0, 255)  # 紫红色
        self.color_ma_30 = (0, 128, 0)  # 纯绿
        self.color_ma_60 = (30, 144, 255)  # 道奇蓝
        self.color_up = (220, 20, 60)
        self.color_down = (60, 179, 113)
        self.main_fixed_target_list = []  # 主体固定曲线，不能被删除
        self.whole_df = None  # 所有数据
        self.whole_header = None  # 所有列名（中文版）
        self.required_header = None  # 要展示的参数的列名（中文版）
        self.whole_pd_header = None  # 所有列名
        self.required_pd_header = None  # 要展示的列名
        self.current_whole_data = None  # 所有列的数据，后续要操作
        pass

    def init_ui(self):
        self.title_label = QtWidgets.QLabel('合约名称')
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet('QLabel{font-size:18px;font-weight:bold}')
        self.vol_label = QtWidgets.QLabel('成交量')
        self.vol_label.setAlignment(Qt.AlignLeft)
        self.vol_label.setStyleSheet('QLabel{font-size:18px;font-weight:bold}')

        # k线图
        x = AxisItem(orientation='bottom')  # x轴
        x.setHeight(h=20)
        self.pw = pg.PlotWidget(axisItems={'bottom': x})
        self.pw.setMouseEnabled(x=True, y=False)
        # self.pw.enableAutoRange(x=False,y=True)
        self.pw.setAutoVisible(x=False, y=True)

        # vol
        x2 = AxisItem(orientation='bottom')  # x轴
        x2.setHeight(h=20)
        self.pw2 = pg.PlotWidget(axisItems={'bottom': x2})
        self.pw2.setMouseEnabled(x=True, y=False)
        # self.pw2.enableAutoRange(x=False,y=True)
        self.pw2.setAutoVisible(x=False, y=True)

        # macd&kdj
        self.t = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        # 添加到顶层窗口中
        self.t.addTab(self.tab1, "Tab 1")
        self.t.addTab(self.tab2, "Tab 2")
        self.t.setTabText(0, 'MACD')
        self.t.setTabText(1, 'KDJ')
        x3 = AxisItem(orientation='bottom')  # macd x轴
        x3.setHeight(h=20)
        self.pw3 = pg.PlotWidget(axisItems={'bottom': x3})
        self.pw3.setMouseEnabled(x=True, y=False)
        # self.pw3.enableAutoRange(x=False,y=True)
        self.pw3.setAutoVisible(x=False, y=True)
        x4 = AxisItem(orientation='bottom')  # kdj x轴
        x4.setHeight(h=20)
        self.pw4 = pg.PlotWidget(axisItems={'bottom': x4})
        self.pw4.setMouseEnabled(x=True, y=False)
        # self.pw4.enableAutoRange(x=False,y=True)
        self.pw4.setAutoVisible(x=False, y=True)

        # 将上述三个widget加入布局
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.title_label)  # 0
        self.layout.addWidget(self.pw)  # 1
        self.layout.addWidget(self.vol_label)  # 2
        self.layout.addWidget(self.pw2)  # 3
        self.layout.addWidget(self.t)  # 4
        # 设置比例
        # setStretch(int index, int stretch)
        # 参数1为索引,参数2为比例,单独设置一个位置的比例无效
        self.layout.setStretch(1, 3)
        self.layout.setStretch(3, 1)
        self.layout.setStretch(4, 1)
        # 设置间距
        self.layout.setSpacing(2)
        self.setLayout(self.layout)
        pass

    def set_data(self, data: Dict[str, Any]):
        title_str = data['title_str']
        whole_header = data['whole_header']
        whole_df = data['whole_df']
        whole_pd_header = data['whole_pd_header']
        required_header = data['required_header']
        required_pd_header = data['required_pd_header']

        self.whole_header = whole_header
        self.whole_df = whole_df
        self.whole_pd_header = whole_pd_header
        self.required_header = required_header
        self.required_pd_header = required_pd_header

        self.title_label.setText(title_str)
        self.caculate_and_show_data()

        pass

    def caculate_and_show_data(self):
        df = self.whole_df
        df.reset_index(inplace=True)
        tradeDate_list = df['tradeDate'].values.tolist()
        x = range(len(df))
        xTick_show = []
        if len(tradeDate_list) > 100:
            x_dur = math.ceil(len(tradeDate_list) / 5)
        else:
            x_dur = math.ceil(len(tradeDate_list) / 5)
        # x_dur = math.ceil(len(df) / 20)
        for i in range(0, len(df), x_dur):
            xTick_show.append((i, tradeDate_list[i]))
        if len(df) % 5 != 0:
            xTick_show.append((len(df) - 1, tradeDate_list[-1]))
        candle_data = []
        segment_data = []
        vol_data = []
        for i, row in df.iterrows():
            candle_data.append((i, row['openPrice'], row['closePrice'], row['lowestPrice'], row['highestPrice']))
            segment_data.append((i, row['MACD']))
            vol_data.append((i, row['openPrice'], row['closePrice'], row['volume']))
        self.current_whole_data = df.loc[:, self.whole_pd_header].values.tolist()

        # 开始配置显示的内容
        self.pw.clear()
        self.pw2.clear()
        self.pw3.clear()
        self.pw4.clear()

        # x轴刻度
        xax = self.pw.getAxis('bottom')
        xax.setTicks([xTick_show])
        xax2 = self.pw2.getAxis('bottom')
        xax2.setTicks([xTick_show])
        xax3 = self.pw3.getAxis('bottom')
        xax3.setTicks([xTick_show])
        xax4 = self.pw4.getAxis('bottom')
        xax4.setTicks([xTick_show])

        # 画k线图和均线
        candle_fixed_target = CandlestickItem(candle_data)
        self.main_fixed_target_list.append(candle_fixed_target)
        self.pw.addItem(candle_fixed_target)
        self.pw.addLegend(size=(40, 40))
        ma5_fixed_target = pg.PlotCurveItem(x=np.array(x), y=np.array(df['ma5'].values.tolist()),
                                            pen=pg.mkPen({'color': self.color_ma_5, 'width': 2}),
                                            connect='finite')
        ma10_fixed_target = pg.PlotCurveItem(x=np.array(x), y=np.array(df['ma10'].values.tolist()),
                                             pen=pg.mkPen({'color': self.color_ma_10, 'width': 2}),
                                             connect='finite')
        ma20_fixed_target = pg.PlotCurveItem(x=np.array(x), y=np.array(df['ma20'].values.tolist()),
                                             pen=pg.mkPen({'color': self.color_ma_20, 'width': 2}),
                                             connect='finite')
        ma30_fixed_target = pg.PlotCurveItem(x=np.array(x), y=np.array(df['ma30'].values.tolist()),
                                             pen=pg.mkPen({'color': self.color_ma_30, 'width': 2}),
                                             connect='finite')
        ma60_fixed_target = pg.PlotCurveItem(x=np.array(x), y=np.array(df['ma60'].values.tolist()),
                                             pen=pg.mkPen({'color': self.color_ma_60, 'width': 2}),
                                             connect='finite')
        self.main_fixed_target_list.append(ma5_fixed_target)
        self.main_fixed_target_list.append(ma10_fixed_target)
        self.main_fixed_target_list.append(ma20_fixed_target)
        self.main_fixed_target_list.append(ma30_fixed_target)
        self.main_fixed_target_list.append(ma60_fixed_target)
        self.pw.addItem(ma5_fixed_target)
        self.pw.addItem(ma10_fixed_target)
        self.pw.addItem(ma20_fixed_target)
        self.pw.addItem(ma30_fixed_target)
        self.pw.addItem(ma60_fixed_target)
        # 十字线
        self.vLine = pg.InfiniteLine(angle=90, movable=False)  # 垂直线
        self.hLine = pg.InfiniteLine(angle=0, movable=False)  # 水平线
        self.label = pg.TextItem()
        self.ylabel = pg.TextItem()
        self.pw.addItem(self.vLine, ignoreBounds=True)
        self.pw.addItem(self.hLine, ignoreBounds=True)
        self.pw.addItem(self.label, ignoreBounds=True)
        self.pw.addItem(self.ylabel, ignoreBounds=True)
        self.vb = self.pw.getViewBox()
        self.proxy = pg.SignalProxy(self.pw.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)

        # 成交量
        vol_fixed_target = VolItem(vol_data)
        self.pw2.addItem(vol_fixed_target)
        self.vLine2 = pg.InfiniteLine(angle=90, movable=False)
        # self.hLine2 = pg.InfiniteLine(angle=0, movable=False)
        self.ylabel2 = pg.TextItem()
        self.pw2.addItem(self.vLine2, ignoreBounds=True)
        # self.pw2.addItem(self.hLine2, ignoreBounds=True)
        self.pw2.addItem(self.ylabel2, ignoreBounds=True)
        self.pw2.setXLink(self.pw)  # 可以同时缩放
        self.proxy2 = pg.SignalProxy(self.pw2.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)
        self.pw.enableAutoRange()
        self.pw2.enableAutoRange()
        self.pw2.setYRange(df['volume'].min(), df['volume'].max())

        # 指标 MACD
        # self.vLine3 = pg.InfiniteLine(angle=90, movable=False)
        # self.hLine3 = pg.InfiniteLine(angle=0, movable=False)
        # self.pw3.addItem(self.vLine3, ignoreBounds=True)
        # self.pw3.addItem(self.hLine3, ignoreBounds=True)
        segment_fixed_target = SegmenttickItem(segment_data)
        diff_fixed_target = pg.PlotCurveItem(x=np.array(x), y=np.array(df['DIFF'].values.tolist()),
                                             pen=pg.mkPen({'color': self.color_ma_5, 'width': 1}),
                                             connect='finite')
        dea_fixed_target = pg.PlotCurveItem(x=np.array(x), y=np.array(df['DEA'].values.tolist()),
                                            pen=pg.mkPen({'color': self.color_ma_10, 'width': 1}),
                                            connect='finite')
        self.main_fixed_target_list.append(diff_fixed_target)
        self.main_fixed_target_list.append(dea_fixed_target)
        self.main_fixed_target_list.append(segment_fixed_target)
        self.pw3.addItem(segment_fixed_target)
        self.pw3.addItem(diff_fixed_target)
        self.pw3.addItem(dea_fixed_target)
        self.pw.setXLink(self.pw)
        self.pw3.setXLink(self.pw)
        self.proxy3 = pg.SignalProxy(self.pw3.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)
        self.pw.enableAutoRange()
        self.pw2.enableAutoRange()
        self.pw3.enableAutoRange()

        # 指标 KDJ
        # self.vLine4 = pg.InfiniteLine(angle=90, movable=False)
        # self.hLine4 = pg.InfiniteLine(angle=0, movable=False)
        # self.pw4.addItem(self.vLine4, ignoreBounds=True)
        # self.pw4.addItem(self.hLine4, ignoreBounds=True)
        kdjk_fixed_target = pg.PlotCurveItem(x=np.array(x), y=np.array(df['kdj_k'].values.tolist()),
                                             pen=pg.mkPen({'color': self.color_ma_10, 'width': 1}),
                                             connect='finite')
        kdjd_fixed_target = pg.PlotCurveItem(x=np.array(x), y=np.array(df['kdj_d'].values.tolist()),
                                             pen=pg.mkPen({'color': self.color_ma_60, 'width': 1}),
                                             connect='finite')
        kdjj_fixed_target = pg.PlotCurveItem(x=np.array(x), y=np.array(df['kdj_j'].values.tolist()),
                                             pen=pg.mkPen({'color': self.color_ma_20, 'width': 1}),
                                             connect='finite')
        self.main_fixed_target_list.append(kdjk_fixed_target)
        self.main_fixed_target_list.append(kdjd_fixed_target)
        self.main_fixed_target_list.append(kdjj_fixed_target)
        self.pw4.addItem(kdjk_fixed_target)
        self.pw4.addItem(kdjd_fixed_target)
        self.pw4.addItem(kdjj_fixed_target)
        self.pw4.setXLink(self.pw)
        self.proxy4 = pg.SignalProxy(self.pw4.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)
        self.pw4.enableAutoRange()

        # pw3、pw4放入tabwidget
        layout1 = QFormLayout()
        layout2 = QFormLayout()
        layout1.addWidget(self.pw3)
        layout2.addWidget(self.pw4)
        self.tab1.setLayout(layout1)
        self.tab2.setLayout(layout2)

        return True
        pass

    def mouseMoved(self, evt):
        pos = evt[0]
        # 鼠标在k线图区域
        if self.pw.sceneBoundingRect().contains(pos):
            mousePoint = self.vb.mapSceneToView(pos)
            index = int(mousePoint.x())
            if 0 <= index < len(self.current_whole_data):
                target_data = self.current_whole_data[index]
                target_data[5] = round(target_data[5], 2)  # volume
                html_str = ''
                for i, item in enumerate(self.required_header):
                    html_str += f"<br/>{item}:{target_data[i]}"
                self.label.setHtml(html_str)
                self.label.setPos(mousePoint.x(), mousePoint.y())
                self.ylabel.setText(str(round(mousePoint.y(), 2)))
                self.ylabel.setPos(0, mousePoint.y())
            # 设置垂直线条和水平线条的位置组成十字光标
            self.vLine.setPos(mousePoint.x())
            self.hLine.setPos(mousePoint.y())
            self.vLine2.setPos(mousePoint.x())
            # self.vLine3.setPos(mousePoint.x())
            # self.vLine4.setPos(mousePoint.x())
            # self.hLine2.setPos(mousePoint.y())
        pass

    # def mouseMoved_pw2(self, evt):
    #     pos = evt[0]
    #     # 鼠标在vol区域
    #     if self.pw2.sceneBoundingRect().contains(pos):
    #         mousePoint = self.vb.mapSceneToView(pos)
    #         index = int(mousePoint.x())
    #         if 0 <= index < len(self.current_whole_data):
    #             target_data = self.current_whole_data[index]
    #             target_data[5] = round(target_data[5], 2)  # volume
    #             self.ylabel2.setText(str(target_data[5]))
    #             self.ylabel2.setPos(0, mousePoint.y())
    #         # 设置垂直线条和水平线条的位置组成十字光标
    #         self.vLine.setPos(mousePoint.x())
    #         self.hLine.setPos(mousePoint.y())
    #         self.vLine2.setPos(mousePoint.x())
    #         # self.hLine2.setPos(mousePoint.y())
    #     pass

    def mouseClicked(self, evt):
        pass

    def updateViews(self):
        pass

    pass


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    # window.setWindowState(Qt.WindowMaximized)
    window.show()  # 显示窗体,使控件可见(默认是隐藏)
    sys.exit(app.exec_())  # 程序关闭时退出进程
