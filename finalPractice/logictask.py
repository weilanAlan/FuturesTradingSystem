from PyQt5.Qt import *
from PyQt5 import QtGui, QtWidgets
import pyqtgraph as pg
import numpy as np
import pandas as pd
import talib
from typing import Dict, Any
import sys
from pyqtgraph import AxisItem
import sqlite3
from pandas.core.frame import DataFrame
from toolClass.CandlestickItem import CandlestickItem
from toolClass.VolItem import VolItem
from finalPractice.quantitativeTradingDemo import quantitativeTradingDemo
from finalPractice.tradeDemo import tradeDemo
from finalPractice.datadisplay import Ui_MainWindow

pg.setConfigOption('background', 'k')
pg.setConfigOption('foreground', 'w')

# 设置全局变量
symbol = 'RB888'
average_state = 0
bulin_state = 0


# 主窗口
# self.data:所有数据
# self.current_data:待处理的所有数据 symbol下or时间边界下
# self.newest_data:传给tradeDemo的数据，每个symbol在该时间段的最新价格
class MyWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyWindow, self).__init__(parent)
        self.setupUi(self)
        self.hline_tradepoint_dict = None # 从交易页面传来的数据们
        self.chicang_symbol = None
        self.chicang_record = None
        self.chicang_record2 = None

        # 读取数据库
        self.read_db()

        # 设置合约名称、时间边界、下单按钮
        self.label_contract.setStyleSheet("QLabel{color:rgb(0,0,0);font-size:15;font-weight:bold;font-family:宋体;}")
        self.title_label = QtWidgets.QLabel('合约名称')
        self.title_label.setFont(QFont("微软雅黑", 14, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        left_tip = QtWidgets.QLabel('左边界：')
        left_tip.setStyleSheet("QLabel{color:rgb(0,0,0);font-size:15;font-weight:bold;font-family:宋体;}")
        self.left_point = QtWidgets.QDateTimeEdit()
        self.left_point.setCalendarPopup(True)
        self.left_point.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        right_tip = QtWidgets.QLabel('右边界：')
        right_tip.setStyleSheet("QLabel{color:rgb(0,0,0);font-size:15;font-weight:bold;font-family:宋体;}")
        self.right_point = QtWidgets.QDateTimeEdit()
        self.right_point.setCalendarPopup(True)
        self.right_point.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.check_box_average = QCheckBox("均线")
        self.check_box_bulin = QCheckBox("布林线")
        self.check_box_average.setChecked(False)
        self.check_box_bulin.setChecked(False)
        self.check_box_average.stateChanged.connect(self.show_or_not_average)
        self.check_box_bulin.stateChanged.connect(self.show_or_not_bulin)
        duration_sel_btn = QtWidgets.QPushButton('确定')
        duration_sel_btn.clicked.connect(self.duration_sel_btn_clicked)
        duration_trade_btn = QtWidgets.QPushButton('下单')
        duration_trade_btn.clicked.connect(self.duration_trade_btn_clicked)
        duration_qt_btn = QtWidgets.QPushButton('量化交易')
        duration_qt_btn.clicked.connect(self.duration_qt_btn_clicked)
        self.whole_duration_label = QtWidgets.QLabel('所有范围：左边界~右边界')
        self.now_duration_label = QtWidgets.QLabel('当前范围：左边界~右边界')

        # 设置title，获取值
        self.title_label.setText(symbol)
        self.getCurrentData()  # 设置self.current_data:symbol下的所有数据

        # 画默认的图(先只画前100个)，放在verticalLayout_kline_graph
        graph = PyQtGraphLineWidget()
        self.whole_duration_label.setText(
            f"原始边界：{self.current_data.iloc[0]['datetime']}~{self.current_data.iloc[-1]['datetime']}")
        self.current_data = self.current_data.iloc[0:min(100, len(self.current_data))]  # 默认最多100个
        self.newest_data = self.data.loc[self.data['datetime']==self.current_data.iloc[-1]['datetime']]
        self.now_duration_label.setText(
            f"当前边界：{self.current_data.iloc[0]['datetime']}~{self.current_data.iloc[min(100, len(self.current_data)) - 1]['datetime']}")
        graph.set_data(self.dealwithData(), self.hline_tradepoint_dict, self.chicang_record, self.chicang_record2)
        self.verticalLayout_kline_graph.addWidget(graph)

        # 布局，放在verticalLayout_dateframe
        spacerItem1 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        spacerItem2 = QtWidgets.QSpacerItem(50, 20, QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        layout_date = QtWidgets.QHBoxLayout()
        layout_date.addWidget(left_tip)
        layout_date.addWidget(self.left_point)
        layout_date.addItem(spacerItem2)
        layout_date.addWidget(right_tip)
        layout_date.addWidget(self.right_point)
        layout_date.addItem(spacerItem1)
        layout_date.addWidget(self.check_box_average)
        layout_date.addWidget(self.check_box_bulin)
        layout_date.addItem(spacerItem1)
        layout_date.addWidget(duration_sel_btn)
        layout_date.addItem(spacerItem2)
        layout_date.addWidget(duration_trade_btn)
        layout_date.addItem(spacerItem2)
        layout_date.addWidget(duration_qt_btn)
        layout_date.addItem(spacerItem1)
        layout_duration = QtWidgets.QHBoxLayout()
        layout_duration.addWidget(self.whole_duration_label)
        layout_duration.addItem(spacerItem2)
        layout_duration.addWidget(self.now_duration_label)
        layout_duration.addItem(spacerItem1)
        self.verticalLayout_dateframe.addWidget(self.title_label)
        self.verticalLayout_dateframe.addLayout(layout_date)
        self.verticalLayout_dateframe.addLayout(layout_duration)

        # 切换合约
        self.comboBox_contract.currentIndexChanged.connect(self.select_contract)

        # 切换各种k线图
        self.action_dayK.triggered.connect(self.select_dayK)
        self.action_weekK.triggered.connect(self.select_weekK)
        self.action_monthK.triggered.connect(self.select_monthK)
        self.action_quarterK.triggered.connect(self.select_quarterK)
        self.action_yearK.triggered.connect(self.select_yearK)
        self.action_1min.triggered.connect(self.select_1min)
        self.action_3min.triggered.connect(self.select_3min)
        self.action_5min.triggered.connect(self.select_5min)
        self.action_10min.triggered.connect(self.select_10min)
        self.action_15min.triggered.connect(self.select_15min)
        self.action_30min.triggered.connect(self.select_30min)
        self.action_1h.triggered.connect(self.select_1h)
        self.action_2h.triggered.connect(self.select_2h)

        # 状态栏
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("1分钟k")  # 默认显示1分钟k

    # 从.db文件读取数据
    def read_db(self):
        # 连接
        conn = sqlite3.connect("C:/Users/12345/Desktop/FuturesTradingSystem/database/database.db")
        c = conn.cursor()
        c.execute("select * from dbbardata")
        rows = c.fetchall()  # rows返回所有记录，rows是一个二维列表
        self.data = DataFrame(rows)  # 所有数据
        self.data.rename(
            columns={0: 'id', 1: 'symbol', 2: 'exchange', 3: 'datetime', 4: 'interval', 5: 'volume', 6: 'turnover',
                     7: 'open_interset', 8: 'open', 9: 'high', 10: 'low', 11: 'close'}, inplace=True)
        # 关闭
        c.close()
        conn.close()

    # 设置该symbol下的所有数据
    def getCurrentData(self):
        self.current_data = self.data[self.data['symbol'] == symbol]

    # 数据处理及计算
    def dealwithData(self):
        df = pd.DataFrame(self.current_data, columns=['datetime', 'close', 'open', 'high', 'low', 'volume'])
        df.columns = ['tradeDate', 'closePrice', 'openPrice', 'highestPrice', 'lowestPrice', 'volume']  # 改列名
        # 计算均线
        close_list = df['closePrice']
        df['ma5'] = 0
        df['ma10'] = 0
        df['ma20'] = 0
        df['ma30'] = 0
        df['ma60'] = 0
        if len(df['closePrice']) >= 60:
            df['ma5'] = talib.MA(close_list, 5)
            df['ma10'] = talib.MA(close_list, 10)
            df['ma20'] = talib.MA(close_list, 20)
            df['ma30'] = talib.MA(close_list, 30)
            df['ma60'] = talib.MA(close_list, 60)
        elif len(df['closePrice']) >= 30:
            df['ma5'] = talib.MA(close_list, 5)
            df['ma10'] = talib.MA(close_list, 10)
            df['ma20'] = talib.MA(close_list, 20)
            df['ma30'] = talib.MA(close_list, 30)
        elif len(df['closePrice']) >= 20:
            df['ma5'] = talib.MA(close_list, 5)
            df['ma10'] = talib.MA(close_list, 10)
            df['ma20'] = talib.MA(close_list, 20)
        elif len(df['closePrice']) >= 10:
            df['ma5'] = talib.MA(close_list, 5)
            df['ma10'] = talib.MA(close_list, 10)
        elif len(df['closePrice']) >= 5:
            df['ma5'] = talib.MA(close_list, 5)
        else:
            print()
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
        df = df.round({'closePrice':2, 'openPrice':2, 'highestPrice':2, 'lowestPrice':2, 'volume':2})
        whole_pd_header = ['tradeDate', 'closePrice', 'openPrice', 'highestPrice', 'lowestPrice', 'volume']
        line_data = {
            'whole_pd_header': whole_pd_header,
            'whole_pd_header_Chinese': ['日期', '收盘价', '开盘价', '最高价', '最低价', '成交量'],
            'whole_df': df
        }
        return line_data

    # 下拉框选择新的合约后触发
    def select_contract(self):
        self.statusbar.showMessage("1分钟k")
        global symbol
        symbol = self.comboBox_contract.currentText()
        # clear之前画的图
        for i in range(self.verticalLayout_kline_graph.count()):
            self.verticalLayout_kline_graph.itemAt(i).widget().deleteLater()
        # 重新设置值
        self.title_label.setText(symbol)
        self.getCurrentData()  # 设置self.current_data:symbol下的所有数据
        self.whole_duration_label.setText(
            f"原始边界：{self.current_data.iloc[0]['datetime']}~{self.current_data.iloc[-1]['datetime']}")
        left_point = self.left_point.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        right_point = self.right_point.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        df = self.current_data.copy()
        df['o_date'] = pd.to_datetime(df['datetime'])
        if len(df.loc[(df['o_date'] >= left_point) & (df['o_date'] <= right_point)]) == 0:  # 没有设定过时间,取默认个数
            self.current_data = self.current_data.iloc[0:min(100, len(self.current_data))]
        else:  # 设定过时间
            self.current_data = None
            self.current_data = df.loc[(df['o_date'] >= left_point) & (df['o_date'] <= right_point)]
        self.newest_data = None
        self.newest_data = self.data.loc[self.data['datetime'] == self.current_data.iloc[-1]['datetime']]
        self.now_duration_label.setText(
            f"当前边界：{self.current_data.iloc[0]['datetime']}~{self.current_data.iloc[-1]['datetime']}")
        # 画图
        graph = PyQtGraphLineWidget()
        graph.set_data(self.dealwithData(), self.hline_tradepoint_dict, self.chicang_record, self.chicang_record2)
        self.verticalLayout_kline_graph.addWidget(graph)

    #  点击时间边界确认按钮
    def duration_sel_btn_clicked(self):
        left_point = self.left_point.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        right_point = self.right_point.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        self.getCurrentData()
        df = self.current_data.copy()
        df['o_date'] = pd.to_datetime(df['datetime'])
        self.current_data = None
        self.current_data = df.loc[(df['o_date'] >= left_point) & (df['o_date'] <= right_point)]
        if len(self.current_data) == 0:
            reply = QMessageBox.about(self, "警告", "该时间段内无交易信息，请另选时间。")
        elif len(self.current_data) < 2:
            reply = QMessageBox.about(self, "警告", "数据少于2个，无法作图。")
        else:
            self.statusbar.showMessage("1分钟k")
            self.now_duration_label.setText(
                f"当前边界：{self.current_data.iloc[0]['datetime']}~{self.current_data.iloc[-1]['datetime']}")
            self.newest_data = None
            self.newest_data = self.data.loc[self.data['datetime'] == self.current_data.iloc[-1]['datetime']]
            graph = PyQtGraphLineWidget()
            graph.set_data(self.dealwithData(), self.hline_tradepoint_dict, self.chicang_record, self.chicang_record2)
            # clear之前画的图
            for i in range(self.verticalLayout_kline_graph.count()):
                self.verticalLayout_kline_graph.itemAt(i).widget().deleteLater()
            self.verticalLayout_kline_graph.addWidget(graph)

    # 点击下单按钮
    def duration_trade_btn_clicked(self):
        df = pd.DataFrame(self.newest_data, columns=['symbol', 'datetime', 'close'])
        df = df.round({'close': 2})
        self.tradedemo = tradeDemo()
        # 绑定信号与槽
        self.tradedemo.signal1.connect(self.receive_tradepoint)
        self.tradedemo.signal2.connect(self.receive_record)
        self.tradedemo.signal_symbol.connect(self.receive_new_symbol)
        self.tradedemo.set_data(symbol, df)

    # 点击量化交易按钮
    def duration_qt_btn_clicked(self):
        left_point = self.left_point.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        right_point = self.right_point.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        df = self.data.copy()
        df['o_date'] = pd.to_datetime(df['datetime'])
        data = None
        data = df.loc[(df['o_date'] >= left_point) & (df['o_date'] <= right_point)]
        if len(data) == 0:
            reply = QMessageBox.about(self, "警告", "该时间段内无交易信息，请另选时间。")
        else:
            self.qttradedemo = quantitativeTradingDemo()
            self.qttradedemo.set_data(data, self.left_point.dateTime().toString('yyyy-MM-dd HH:mm:ss'),
                                      self.right_point.dateTime().toString('yyyy-MM-dd HH:mm:ss'))

    def select_dayK(self):
        self.getCurrentData()  # 设置self.current_data:symbol下的所有数据
        left_point = self.left_point.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        right_point = self.right_point.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        df = self.current_data.copy()
        df['o_date'] = pd.to_datetime(df['datetime'])
        if len(df.loc[(df['o_date'] >= left_point) & (df['o_date'] <= right_point)]) == 0:  # 没有设定过时间,取默认个数
            self.current_data = self.current_data.iloc[0:min(100, len(self.current_data))]
        else:  # 设定过时间
            self.current_data = None
            self.current_data = df.loc[(df['o_date'] >= left_point) & (df['o_date'] <= right_point)]
        self.current_data['datetime'] = pd.to_datetime(self.current_data['datetime'])
        self.current_data.set_index('datetime', inplace=True)
        self.current_data = self.current_data.resample('D').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).dropna()
        self.current_data.reset_index(inplace=True)
        if len(self.current_data) < 2 :
            reply = QMessageBox.about(self, "警告", "天数少于2，无法作图。")
            self.select_1min()
        else:
            self.statusbar.showMessage("日k")
            # clear之前画的图
            for i in range(self.verticalLayout_kline_graph.count()):
                self.verticalLayout_kline_graph.itemAt(i).widget().deleteLater()
            graph = PyQtGraphLineWidget()
            graph.set_data(self.dealwithData(), self.hline_tradepoint_dict, self.chicang_record, self.chicang_record2)
            self.verticalLayout_kline_graph.addWidget(graph)

    def select_weekK(self):
        self.getCurrentData()  # 设置self.current_data:symbol下的所有数据
        left_point = self.left_point.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        right_point = self.right_point.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        df = self.current_data.copy()
        df['o_date'] = pd.to_datetime(df['datetime'])
        if len(df.loc[(df['o_date'] >= left_point) & (df['o_date'] <= right_point)]) == 0:  # 没有设定过时间,取默认个数
            self.current_data = self.current_data.iloc[0:min(100, len(self.current_data))]
        else:  # 设定过时间
            self.current_data = None
            self.current_data = df.loc[(df['o_date'] >= left_point) & (df['o_date'] <= right_point)]
        self.current_data['datetime'] = pd.to_datetime(self.current_data['datetime'])
        self.current_data.set_index('datetime', inplace=True)
        self.current_data = self.current_data.resample('D').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).dropna()
        self.current_data = self.current_data.resample('W').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).dropna()
        self.current_data.reset_index(inplace=True)
        if len(self.current_data) < 2 :
            reply = QMessageBox.about(self, "警告", "周数少于2，无法作图。")
            self.select_1min()
        else:
            self.statusbar.showMessage("周k")
            # clear之前画的图
            for i in range(self.verticalLayout_kline_graph.count()):
                self.verticalLayout_kline_graph.itemAt(i).widget().deleteLater()
            graph = PyQtGraphLineWidget()
            graph.set_data(self.dealwithData(), self.hline_tradepoint_dict, self.chicang_record, self.chicang_record2)
            self.verticalLayout_kline_graph.addWidget(graph)

    def select_monthK(self):
        self.getCurrentData()  # 设置self.current_data:symbol下的所有数据
        left_point = self.left_point.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        right_point = self.right_point.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        df = self.current_data.copy()
        df['o_date'] = pd.to_datetime(df['datetime'])
        if len(df.loc[(df['o_date'] >= left_point) & (df['o_date'] <= right_point)]) == 0:  # 没有设定过时间,取默认个数
            self.current_data = self.current_data.iloc[0:min(100, len(self.current_data))]
        else:  # 设定过时间
            self.current_data = None
            self.current_data = df.loc[(df['o_date'] >= left_point) & (df['o_date'] <= right_point)]
        self.current_data['datetime'] = pd.to_datetime(self.current_data['datetime'])
        self.current_data.set_index('datetime', inplace=True)
        self.current_data = self.current_data.resample('D').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).dropna()
        self.current_data = self.current_data.resample('M').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).dropna()
        self.current_data.reset_index(inplace=True)
        if len(self.current_data) < 2:
            reply = QMessageBox.about(self, "警告", "月份数少于2，无法作图。")
            self.select_1min()
        else:
            self.statusbar.showMessage("月k")
            # clear之前画的图
            for i in range(self.verticalLayout_kline_graph.count()):
                self.verticalLayout_kline_graph.itemAt(i).widget().deleteLater()
            graph = PyQtGraphLineWidget()
            graph.set_data(self.dealwithData(), self.hline_tradepoint_dict, self.chicang_record, self.chicang_record2)
            self.verticalLayout_kline_graph.addWidget(graph)

    def select_quarterK(self):
        self.getCurrentData()  # 设置self.current_data:symbol下的所有数据
        left_point = self.left_point.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        right_point = self.right_point.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        df = self.current_data.copy()
        df['o_date'] = pd.to_datetime(df['datetime'])
        if len(df.loc[(df['o_date'] >= left_point) & (df['o_date'] <= right_point)]) == 0:  # 没有设定过时间,取默认个数
            self.current_data = self.current_data.iloc[0:min(100, len(self.current_data))]
        else:  # 设定过时间
            self.current_data = None
            self.current_data = df.loc[(df['o_date'] >= left_point) & (df['o_date'] <= right_point)]
        self.current_data['datetime'] = pd.to_datetime(self.current_data['datetime'])
        self.current_data.set_index('datetime', inplace=True)
        self.current_data = self.current_data.resample('D').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).dropna()
        self.current_data = self.current_data.resample('Q').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).dropna()
        self.current_data.reset_index(inplace=True)
        if len(self.current_data) < 2 :
            reply = QMessageBox.about(self, "警告", "季度数少于2，无法作图。")
            self.select_1min()
        else:
            self.statusbar.showMessage("季k")
            # clear之前画的图
            for i in range(self.verticalLayout_kline_graph.count()):
                self.verticalLayout_kline_graph.itemAt(i).widget().deleteLater()
            graph = PyQtGraphLineWidget()
            graph.set_data(self.dealwithData(), self.hline_tradepoint_dict, self.chicang_record, self.chicang_record2)
            self.verticalLayout_kline_graph.addWidget(graph)

    def select_yearK(self):
        self.getCurrentData()  # 设置self.current_data:symbol下的所有数据
        left_point = self.left_point.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        right_point = self.right_point.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        df = self.current_data.copy()
        df['o_date'] = pd.to_datetime(df['datetime'])
        if len(df.loc[(df['o_date'] >= left_point) & (df['o_date'] <= right_point)]) == 0:  # 没有设定过时间,取默认个数
            self.current_data = self.current_data.iloc[0:min(100, len(self.current_data))]
        else:  # 设定过时间
            self.current_data = None
            self.current_data = df.loc[(df['o_date'] >= left_point) & (df['o_date'] <= right_point)]
        self.current_data['datetime'] = pd.to_datetime(self.current_data['datetime'])
        self.current_data.set_index('datetime', inplace=True)
        self.current_data = self.current_data.resample('D').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).dropna()
        self.current_data = self.current_data.resample('Y').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).dropna()
        self.current_data.reset_index(inplace=True)
        if len(self.current_data) < 2:
            reply = QMessageBox.about(self, "警告", "年数少于2，无法作图。")
            self.select_1min()
        else:
            self.statusbar.showMessage("年k")
            # clear之前画的图
            for i in range(self.verticalLayout_kline_graph.count()):
                self.verticalLayout_kline_graph.itemAt(i).widget().deleteLater()
            graph = PyQtGraphLineWidget()
            graph.set_data(self.dealwithData(), self.hline_tradepoint_dict, self.chicang_record, self.chicang_record2)
            self.verticalLayout_kline_graph.addWidget(graph)

    def select_1min(self):
        self.statusbar.showMessage("1分钟k")
        self.getCurrentData()  # 设置self.current_data:symbol下的所有数据
        left_point = self.left_point.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        right_point = self.right_point.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        df = self.current_data.copy()
        df['o_date'] = pd.to_datetime(df['datetime'])
        if len(df.loc[(df['o_date'] >= left_point) & (df['o_date'] <= right_point)]) == 0:  # 没有设定过时间,取默认个数
            self.current_data = self.current_data.iloc[0:min(100, len(self.current_data))]
        else:  # 设定过时间
            self.current_data = None
            self.current_data = df.loc[(df['o_date'] >= left_point) & (df['o_date'] <= right_point)]
        # clear之前画的图
        for i in range(self.verticalLayout_kline_graph.count()):
            self.verticalLayout_kline_graph.itemAt(i).widget().deleteLater()
        graph = PyQtGraphLineWidget()
        graph.set_data(self.dealwithData(), self.hline_tradepoint_dict, self.chicang_record, self.chicang_record2)
        self.verticalLayout_kline_graph.addWidget(graph)

    def select_3min(self):
        self.getCurrentData()  # 设置self.current_data:symbol下的所有数据
        left_point = self.left_point.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        right_point = self.right_point.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        df = self.current_data.copy()
        df['o_date'] = pd.to_datetime(df['datetime'])
        if len(df.loc[(df['o_date'] >= left_point) & (df['o_date'] <= right_point)]) == 0:  # 没有设定过时间,取默认个数
            self.current_data = self.current_data.iloc[0:min(100, len(self.current_data))]
        else:  # 设定过时间
            self.current_data = None
            self.current_data = df.loc[(df['o_date'] >= left_point) & (df['o_date'] <= right_point)]
        self.current_data['datetime'] = pd.to_datetime(self.current_data['datetime'])
        self.current_data.set_index('datetime', inplace=True)
        self.current_data = self.current_data.resample('3min').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).dropna()
        self.current_data.reset_index(inplace=True)
        if len(self.current_data) < 2:
            reply = QMessageBox.about(self, "警告", "不足6分钟，无法作图。")
            self.select_1min()
        else:
            self.statusbar.showMessage("3分钟k")
            # clear之前画的图
            for i in range(self.verticalLayout_kline_graph.count()):
                self.verticalLayout_kline_graph.itemAt(i).widget().deleteLater()
            graph = PyQtGraphLineWidget()
            graph.set_data(self.dealwithData(), self.hline_tradepoint_dict, self.chicang_record, self.chicang_record2)
            self.verticalLayout_kline_graph.addWidget(graph)

    def select_5min(self):
        self.getCurrentData()  # 设置self.current_data:symbol下的所有数据
        left_point = self.left_point.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        right_point = self.right_point.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        df = self.current_data.copy()
        df['o_date'] = pd.to_datetime(df['datetime'])
        if len(df.loc[(df['o_date'] >= left_point) & (df['o_date'] <= right_point)]) == 0:  # 没有设定过时间,取默认个数
            self.current_data = self.current_data.iloc[0:min(100, len(self.current_data))]
        else:  # 设定过时间
            self.current_data = None
            self.current_data = df.loc[(df['o_date'] >= left_point) & (df['o_date'] <= right_point)]
        self.current_data['datetime'] = pd.to_datetime(self.current_data['datetime'])
        self.current_data.set_index('datetime', inplace=True)
        self.current_data = self.current_data.resample('5min').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).dropna()
        self.current_data.reset_index(inplace=True)
        if len(self.current_data) < 2:
            reply = QMessageBox.about(self, "警告", "不足10分钟，无法作图。")
            self.select_1min()
        else:
            self.statusbar.showMessage("5分钟k")
            # clear之前画的图
            for i in range(self.verticalLayout_kline_graph.count()):
                self.verticalLayout_kline_graph.itemAt(i).widget().deleteLater()
            graph = PyQtGraphLineWidget()
            graph.set_data(self.dealwithData(), self.hline_tradepoint_dict, self.chicang_record, self.chicang_record2)
            self.verticalLayout_kline_graph.addWidget(graph)

    def select_10min(self):
        self.getCurrentData()  # 设置self.current_data:symbol下的所有数据
        left_point = self.left_point.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        right_point = self.right_point.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        df = self.current_data.copy()
        df['o_date'] = pd.to_datetime(df['datetime'])
        if len(df.loc[(df['o_date'] >= left_point) & (df['o_date'] <= right_point)]) == 0:  # 没有设定过时间,取默认个数
            self.current_data = self.current_data.iloc[0:min(100, len(self.current_data))]
        else:  # 设定过时间
            self.current_data = None
            self.current_data = df.loc[(df['o_date'] >= left_point) & (df['o_date'] <= right_point)]
        self.current_data['datetime'] = pd.to_datetime(self.current_data['datetime'])
        self.current_data.set_index('datetime', inplace=True)
        self.current_data = self.current_data.resample('10min').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).dropna()
        self.current_data.reset_index(inplace=True)
        if len(self.current_data) < 2:
            reply = QMessageBox.about(self, "警告", "不足20分钟，无法作图。")
            self.select_1min()
        else:
            self.statusbar.showMessage("10分钟k")
            # clear之前画的图
            for i in range(self.verticalLayout_kline_graph.count()):
                self.verticalLayout_kline_graph.itemAt(i).widget().deleteLater()
            graph = PyQtGraphLineWidget()
            graph.set_data(self.dealwithData(), self.hline_tradepoint_dict, self.chicang_record, self.chicang_record2)
            self.verticalLayout_kline_graph.addWidget(graph)

    def select_15min(self):
        self.getCurrentData()  # 设置self.current_data:symbol下的所有数据
        left_point = self.left_point.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        right_point = self.right_point.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        df = self.current_data.copy()
        df['o_date'] = pd.to_datetime(df['datetime'])
        if len(df.loc[(df['o_date'] >= left_point) & (df['o_date'] <= right_point)]) == 0:  # 没有设定过时间,取默认个数
            self.current_data = self.current_data.iloc[0:min(100, len(self.current_data))]
        else:  # 设定过时间
            self.current_data = None
            self.current_data = df.loc[(df['o_date'] >= left_point) & (df['o_date'] <= right_point)]
        self.current_data['datetime'] = pd.to_datetime(self.current_data['datetime'])
        self.current_data.set_index('datetime', inplace=True)
        self.current_data = self.current_data.resample('15min').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).dropna()
        self.current_data.reset_index(inplace=True)
        if len(self.current_data) < 2:
            reply = QMessageBox.about(self, "警告", "不足半小时，无法作图。")
            self.select_1min()
        else:
            self.statusbar.showMessage("15分钟k")
            # clear之前画的图
            for i in range(self.verticalLayout_kline_graph.count()):
                self.verticalLayout_kline_graph.itemAt(i).widget().deleteLater()
            graph = PyQtGraphLineWidget()
            graph.set_data(self.dealwithData(), self.hline_tradepoint_dict, self.chicang_record, self.chicang_record2)
            self.verticalLayout_kline_graph.addWidget(graph)

    def select_30min(self):
        self.getCurrentData()  # 设置self.current_data:symbol下的所有数据
        left_point = self.left_point.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        right_point = self.right_point.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        df = self.current_data.copy()
        df['o_date'] = pd.to_datetime(df['datetime'])
        if len(df.loc[(df['o_date'] >= left_point) & (df['o_date'] <= right_point)]) == 0:  # 没有设定过时间,取默认个数
            self.current_data = self.current_data.iloc[0:min(100, len(self.current_data))]
        else:  # 设定过时间
            self.current_data = None
            self.current_data = df.loc[(df['o_date'] >= left_point) & (df['o_date'] <= right_point)]
        self.current_data['datetime'] = pd.to_datetime(self.current_data['datetime'])
        self.current_data.set_index('datetime', inplace=True)
        self.current_data = self.current_data.resample('30min').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).dropna()
        self.current_data.reset_index(inplace=True)
        if len(self.current_data) < 2:
            reply = QMessageBox.about(self, "警告", "不足1小时，无法作图。")
            self.select_1min()
        else:
            self.statusbar.showMessage("30分钟k")
            # clear之前画的图
            for i in range(self.verticalLayout_kline_graph.count()):
                self.verticalLayout_kline_graph.itemAt(i).widget().deleteLater()
            graph = PyQtGraphLineWidget()
            graph.set_data(self.dealwithData(), self.hline_tradepoint_dict, self.chicang_record, self.chicang_record2)
            self.verticalLayout_kline_graph.addWidget(graph)

    def select_1h(self):
        self.getCurrentData()  # 设置self.current_data:symbol下的所有数据
        left_point = self.left_point.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        right_point = self.right_point.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        df = self.current_data.copy()
        df['o_date'] = pd.to_datetime(df['datetime'])
        if len(df.loc[(df['o_date'] >= left_point) & (df['o_date'] <= right_point)]) == 0:  # 没有设定过时间,取默认个数
            self.current_data = self.current_data.iloc[0:min(100, len(self.current_data))]
        else:  # 设定过时间
            self.current_data = None
            self.current_data = df.loc[(df['o_date'] >= left_point) & (df['o_date'] <= right_point)]
        self.current_data['datetime'] = pd.to_datetime(self.current_data['datetime'])
        self.current_data.set_index('datetime', inplace=True)
        self.current_data = self.current_data.resample('60min').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).dropna()
        self.current_data.reset_index(inplace=True)
        if len(self.current_data) < 2:
            reply = QMessageBox.about(self, "警告", "不足2小时，无法作图。")
            self.select_1min()
        else:
            self.statusbar.showMessage("1小时k")
            # clear之前画的图
            for i in range(self.verticalLayout_kline_graph.count()):
                self.verticalLayout_kline_graph.itemAt(i).widget().deleteLater()
            graph = PyQtGraphLineWidget()
            graph.set_data(self.dealwithData(), self.hline_tradepoint_dict, self.chicang_record, self.chicang_record2)
            self.verticalLayout_kline_graph.addWidget(graph)

    def select_2h(self):
        self.getCurrentData()  # 设置self.current_data:symbol下的所有数据
        left_point = self.left_point.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        right_point = self.right_point.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        df = self.current_data.copy()
        df['o_date'] = pd.to_datetime(df['datetime'])
        if len(df.loc[(df['o_date'] >= left_point) & (df['o_date'] <= right_point)]) == 0:  # 没有设定过时间,取默认个数
            self.current_data = self.current_data.iloc[0:min(100, len(self.current_data))]
        else:  # 设定过时间
            self.current_data = None
            self.current_data = df.loc[(df['o_date'] >= left_point) & (df['o_date'] <= right_point)]
        self.current_data['datetime'] = pd.to_datetime(self.current_data['datetime'])
        self.current_data.set_index('datetime', inplace=True)
        self.current_data = self.current_data.resample('120min').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).dropna()
        self.current_data.reset_index(inplace=True)
        if len(self.current_data) < 2:
            reply = QMessageBox.about(self, "警告", "不足4小时，无法作图。")
            self.select_1min()
        else:
            self.statusbar.showMessage("2小时k")
            # clear之前画的图
            for i in range(self.verticalLayout_kline_graph.count()):
                self.verticalLayout_kline_graph.itemAt(i).widget().deleteLater()
            graph = PyQtGraphLineWidget()
            graph.set_data(self.dealwithData(), self.hline_tradepoint_dict, self.chicang_record, self.chicang_record2)
            self.verticalLayout_kline_graph.addWidget(graph)

    def show_or_not_average(self):
        global average_state
        average_state = 1- average_state
        # clear之前画的图
        for i in range(self.verticalLayout_kline_graph.count()):
            self.verticalLayout_kline_graph.itemAt(i).widget().deleteLater()
        graph = PyQtGraphLineWidget()
        graph.set_data(self.dealwithData(), self.hline_tradepoint_dict, self.chicang_record, self.chicang_record2)
        self.verticalLayout_kline_graph.addWidget(graph)

    def show_or_not_bulin(self):
        global bulin_state
        bulin_state = 1- bulin_state
        # clear之前画的图
        for i in range(self.verticalLayout_kline_graph.count()):
            self.verticalLayout_kline_graph.itemAt(i).widget().deleteLater()
        graph = PyQtGraphLineWidget()
        graph.set_data(self.dealwithData(), self.hline_tradepoint_dict, self.chicang_record, self.chicang_record2)
        self.verticalLayout_kline_graph.addWidget(graph)

    def receive_tradepoint(self, dict):
        self.hline_tradepoint_dict = dict
        # clear之前画的图
        item_list = list(range(self.verticalLayout_kline_graph.count()))
        item_list.reverse()  # 倒序删除，避免影响布局顺序
        for i in item_list:
            item = self.verticalLayout_kline_graph.itemAt(i)
            self.verticalLayout_kline_graph.removeItem(item)
            if item.widget():
                item.widget().deleteLater()
        self.statusbar.showMessage("1分钟k")
        self.getCurrentData()  # 设置self.current_data:symbol下的所有数据
        left_point = self.left_point.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        right_point = self.right_point.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        df = self.current_data.copy()
        df['o_date'] = pd.to_datetime(df['datetime'])
        if len(df.loc[(df['o_date'] >= left_point) & (df['o_date'] <= right_point)]) == 0:  # 没有设定过时间,取默认个数
            self.current_data = self.current_data.iloc[0:min(100, len(self.current_data))]
        else:  # 设定过时间
            self.current_data = None
            self.current_data = df.loc[(df['o_date'] >= left_point) & (df['o_date'] <= right_point)]
        graph = PyQtGraphLineWidget()
        self.newest_data = self.data.loc[self.data['datetime'] == self.current_data.iloc[-1]['datetime']]
        graph.set_data(self.dealwithData(), self.hline_tradepoint_dict, self.chicang_record, self.chicang_record2)
        self.verticalLayout_kline_graph.addWidget(graph)
        self.hline_tradepoint_dict = None

    def receive_record(self, str, dict, dict2):
        self.chicang_symbol = str
        self.chicang_record = dict
        self.chicang_record2 = dict2
        # 重新设置值
        if symbol != str:
            # clear之前画的图
            item_list = list(range(self.verticalLayout_kline_graph.count()))
            item_list.reverse()  # 倒序删除，避免影响布局顺序
            for i in item_list:
                item = self.verticalLayout_kline_graph.itemAt(i)
                self.verticalLayout_kline_graph.removeItem(item)
                if item.widget():
                    item.widget().deleteLater()
            codelist = ['RB888', 'RB99', 'SA99', 'SA888', 'jm888', 'jm99']  # 存储期货代码
            self.comboBox_contract.setCurrentIndex(codelist.index(str))
        else:
            self.statusbar.showMessage("1分钟k")
            # clear之前画的图
            item_list = list(range(self.verticalLayout_kline_graph.count()))
            item_list.reverse()  # 倒序删除，避免影响布局顺序
            for i in item_list:
                item = self.verticalLayout_kline_graph.itemAt(i)
                self.verticalLayout_kline_graph.removeItem(item)
                if item.widget():
                    item.widget().deleteLater()
            self.getCurrentData()  # 设置self.current_data:symbol下的所有数据
            left_point = self.left_point.dateTime().toString('yyyy-MM-dd HH:mm:ss')
            right_point = self.right_point.dateTime().toString('yyyy-MM-dd HH:mm:ss')
            df = self.current_data.copy()
            df['o_date'] = pd.to_datetime(df['datetime'])
            if len(df.loc[(df['o_date'] >= left_point) & (df['o_date'] <= right_point)]) == 0:  # 没有设定过时间,取默认个数
                self.current_data = self.current_data.iloc[0:min(100, len(self.current_data))]
            else:  # 设定过时间
                self.current_data = None
                self.current_data = df.loc[(df['o_date'] >= left_point) & (df['o_date'] <= right_point)]
            graph = PyQtGraphLineWidget()
            self.newest_data = self.data.loc[self.data['datetime'] == self.current_data.iloc[-1]['datetime']]
            graph.set_data(self.dealwithData(), self.hline_tradepoint_dict, self.chicang_record, self.chicang_record2)
            self.verticalLayout_kline_graph.addWidget(graph)
        self.chicang_symbol = None
        self.chicang_record = None
        self.chicang_record2 = None

    def receive_new_symbol(self, str):
        # 重新设置值
        if symbol != str:
            # clear之前画的图
            item_list = list(range(self.verticalLayout_kline_graph.count()))
            item_list.reverse()  # 倒序删除，避免影响布局顺序
            for i in item_list:
                item = self.verticalLayout_kline_graph.itemAt(i)
                self.verticalLayout_kline_graph.removeItem(item)
                if item.widget():
                    item.widget().deleteLater()
            codelist = ['RB888', 'RB99', 'SA99', 'SA888', 'jm888', 'jm99']  # 存储期货代码
            self.comboBox_contract.setCurrentIndex(codelist.index(str))


#  所有图表（K线图、均线、vol、macd、kdj）显示的控件
#  self.whole_df:该symbol下、接收到的所有数据
#  self.whole_pd_header:该symbol下的所有列名
#  self.whole_pd_header_Chinese:该symbol下的所有中文列名
#  self.current_whole_data:该symbol下的所有列的数据，后续要操作
#  self.pw:k线图的地方
#  self.timer：定时器
#  self.points:当前最近更新页面上绘制的30个（或更少）数据
#  self.current_whole_df:边界选择之后的数据
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
        self.color_kai = (255, 0, 0)
        self.color_kong = (0, 255, 0)
        self.main_fixed_target_list = []  # 主体固定曲线，不能被删除
        self.whole_df = None  # 所有数据
        self.current_whole_df = None  # 边界选择之后的数据
        self.whole_pd_header = None  # 所有列名
        self.whole_pd_header_Chinese = None  # 所有中文列名
        self.current_whole_data = None  # 所有列的数据，后续要操作
        self.points = None  # 当前最近更新页面上绘制的30个（或更少）数据
        pass

    def init_ui(self):
        # 1.一些标题
        self.vol_label = QtWidgets.QLabel('成交量')
        self.vol_label.setAlignment(Qt.AlignLeft)
        self.vol_label.setStyleSheet("QLabel{color:rgb(0,0,0);font-size:15;font-weight:bold;font-family:宋体;}")
        self.kdj_label = QtWidgets.QLabel('KDJ')
        self.kdj_label.setAlignment(Qt.AlignLeft)
        self.kdj_label.setStyleSheet("QLabel{color:rgb(0,0,0);font-size:15;font-weight:bold;font-family:宋体;}")

        # 2.k线图
        x = AxisItem(orientation='bottom')  # x轴
        x.setHeight(h=20)
        self.pw = pg.PlotWidget(axisItems={'bottom': x})
        self.pw.setMouseEnabled(x=True, y=True)
        self.pw.setAutoVisible(x=False, y=False)

        # 3.vol
        x2 = AxisItem(orientation='bottom')  # x轴
        x2.setHeight(h=20)
        self.pw2 = pg.PlotWidget(axisItems={'bottom': x2})
        self.pw2.setMouseEnabled(x=True, y=False)
        self.pw2.setAutoVisible(x=False, y=True)

        # 4.kdj
        x4 = AxisItem(orientation='bottom')  # kdj x轴
        x4.setHeight(h=20)
        self.pw4 = pg.PlotWidget(axisItems={'bottom': x4})
        self.pw4.setMouseEnabled(x=True, y=False)
        self.pw4.setAutoVisible(x=False, y=True)

        # 5.加入布局
        self.layout2 = QtWidgets.QVBoxLayout()
        self.layout2.addWidget(self.pw)
        self.layout2.addWidget(self.vol_label)
        self.layout2.addWidget(self.pw2)
        self.layout2.addWidget(self.kdj_label)
        self.layout2.addWidget(self.pw4)
        # 设置比例 setStretch(int index, int stretch)
        # 参数1为索引,参数2为比例,单独设置一个位置的比例无效
        self.layout2.setStretch(0, 4)
        self.layout2.setStretch(2, 1)
        self.layout2.setStretch(4, 1)
        # 设置间距
        self.layout2.setSpacing(2)
        self.setLayout(self.layout2)

    def set_data(self, data: Dict[str, Any], hline_tradepoint_dict: dict, chicang_record: dict, chicang_record2: dict):
        self.whole_df = data['whole_df']  # 接收到的所有数据
        self.whole_df['tradeDate'] = self.whole_df['tradeDate'].astype(str)
        self.whole_pd_header = data['whole_pd_header']  # 所有列名
        self.whole_pd_header_Chinese = data['whole_pd_header_Chinese']  # 所有列名的中文
        self.hline_tradepoint_dict = hline_tradepoint_dict  # 当前交易点的dict
        self.chicang_record = chicang_record  # 当前选中的持仓记录
        self.chicang_record2 = chicang_record2  # 相同symbol，另一种类型的持仓记录
        self.caculate_and_show_data()
        pass

    # 画图
    def caculate_and_show_data(self):
        df = self.whole_df.copy()
        df.reset_index(inplace=True)
        tradeDate_list = df['tradeDate'].values.tolist()
        x = range(len(df))
        xTick_show = []
        candle_data = []
        segment_data = []
        vol_data = []
        for i, row in df.iterrows():
            candle_data.append((i, row['openPrice'], row['closePrice'], row['lowestPrice'], row['highestPrice']))
            segment_data.append((i, row['MACD']))
            vol_data.append((i, row['openPrice'], row['closePrice'], row['volume']))
        self.current_whole_data = df.loc[:, self.whole_pd_header].values.tolist()

        # x轴刻度
        xax = self.pw.getAxis('bottom')
        xax.setTicks([xTick_show])
        xax2 = self.pw2.getAxis('bottom')
        xax2.setTicks([xTick_show])
        xax4 = self.pw4.getAxis('bottom')
        xax4.setTicks([xTick_show])

        # 开始配置显示的内容
        self.pw.clear()
        self.pw2.clear()
        self.pw4.clear()

        # 1.画k线图
        candle_fixed_target = CandlestickItem(candle_data)
        self.main_fixed_target_list.append(candle_fixed_target)
        self.pw.addItem(candle_fixed_target)

        # 要显示均线
        if average_state == 1:
            if df['ma5'][0] != 0:
                ma5_fixed_target = pg.PlotCurveItem(x=np.array(x), y=np.array(df['ma5'].values.tolist()),
                                                    pen=pg.mkPen({'color': self.color_ma_5, 'width': 2}),
                                                    connect='finite')
                self.main_fixed_target_list.append(ma5_fixed_target)
                self.pw.addItem(ma5_fixed_target)
            if df['ma10'][0] != 0:
                ma10_fixed_target = pg.PlotCurveItem(x=np.array(x), y=np.array(df['ma10'].values.tolist()),
                                                     pen=pg.mkPen({'color': self.color_ma_10, 'width': 2}),
                                                     connect='finite')
                self.main_fixed_target_list.append(ma10_fixed_target)
                self.pw.addItem(ma10_fixed_target)
            if df['ma20'][0] != 0:
                ma20_fixed_target = pg.PlotCurveItem(x=np.array(x), y=np.array(df['ma20'].values.tolist()),
                                                     pen=pg.mkPen({'color': self.color_ma_20, 'width': 2}),
                                                     connect='finite')
                self.main_fixed_target_list.append(ma20_fixed_target)
                self.pw.addItem(ma20_fixed_target)
            if df['ma30'][0] != 0:
                ma30_fixed_target = pg.PlotCurveItem(x=np.array(x), y=np.array(df['ma30'].values.tolist()),
                                                     pen=pg.mkPen({'color': self.color_ma_30, 'width': 2}),
                                                     connect='finite')
                self.main_fixed_target_list.append(ma30_fixed_target)
                self.pw.addItem(ma30_fixed_target)
            if df['ma60'][0] != 0:
                ma60_fixed_target = pg.PlotCurveItem(x=np.array(x), y=np.array(df['ma60'].values.tolist()),
                                                     pen=pg.mkPen({'color': self.color_ma_60, 'width': 2}),
                                                     connect='finite')
                self.main_fixed_target_list.append(ma60_fixed_target)
                self.pw.addItem(ma60_fixed_target)
        # 要显示布林线
        if bulin_state == 1:
            mad_fixed_target = pg.PlotCurveItem(x=np.array(x), y=np.array(df['md'].values.tolist()),
                                                pen=pg.mkPen({'color': 'blue', 'width': 2}),
                                                connect='finite')
            upper_fixed_target = pg.PlotCurveItem(x=np.array(x), y=np.array(df['upper'].values.tolist()),
                                                  pen=pg.mkPen({'color': 'red', 'width': 2}),
                                                  connect='finite')
            lower_fixed_target = pg.PlotCurveItem(x=np.array(x), y=np.array(df['lower'].values.tolist()),
                                                  pen=pg.mkPen({'color': 'green', 'width': 2}),
                                                  connect='finite')
            self.pw.addItem(mad_fixed_target)
            self.pw.addItem(upper_fixed_target)
            self.pw.addItem(lower_fixed_target)

        # 有交易点要显示
        if self.hline_tradepoint_dict != None:
            if self.hline_tradepoint_dict['类型'] == '买开' or self.hline_tradepoint_dict['类型'] == '买平':
                if self.hline_tradepoint_dict['类型'] == '买开':
                    html_str = str(self.hline_tradepoint_dict['成交价']) + '  买多' + str(self.hline_tradepoint_dict['成交量']) + "手"
                else:
                    html_str = str(self.hline_tradepoint_dict['成交价']) + '  平空' + str(self.hline_tradepoint_dict['成交量']) + "手"
                self.line_tradepoint = pg.InfiniteLine(pos=(0, self.hline_tradepoint_dict['成交价']), movable=False, angle=0, pen=self.color_kai,
                                      label=html_str,
                                      labelOpts={'position': 0.05, 'color': (255, 255, 255), 'movable': True,
                                                 'fill': (self.color_kai[0], self.color_kai[1], self.color_kai[2], 150)})
            else:
                if self.hline_tradepoint_dict['类型'] == '卖开':
                    html_str = str(self.hline_tradepoint_dict['成交价']) + '  卖空' + str(
                        self.hline_tradepoint_dict['成交量']) + "手"
                else:
                    html_str = str(self.hline_tradepoint_dict['成交价']) + '  平多' + str(
                        self.hline_tradepoint_dict['成交量']) + "手"
                self.line_tradepoint = pg.InfiniteLine(pos=(0, self.hline_tradepoint_dict['成交价']), movable=False,
                                                       angle=0, pen=self.color_kong,
                                                       label=html_str,
                                                       labelOpts={'position': 0.05, 'color': (255, 255, 255), 'movable': False,
                                                                  'fill': (self.color_kong[0], self.color_kong[1],
                                                                           self.color_kong[2], 150)})
            self.pw.addItem(self.line_tradepoint, ignoreBounds=True)

        # 持仓记录要显示
        if self.chicang_record:
            html_str = str(self.chicang_record['总仓']) + "手" + self.chicang_record['类型'] + '单  ' \
                       + str(self.chicang_record['开仓均价']) + '  ' + str(self.chicang_record['逐笔盈亏'])
            self.line_chicang_record = pg.InfiniteLine(pos=(0, float(self.chicang_record['开仓均价'])), movable=False,
                                                       angle=0, pen=(205, 192, 176), label=html_str,
                                                        labelOpts={'position': 0.1, 'color': (255, 255, 255),
                                                                   'movable': True, 'fill': (205, 192, 176, 150)})
            self.pw.addItem(self.line_chicang_record, ignoreBounds=True)
        if self.chicang_record2:
            html_str = str(self.chicang_record2['总仓']) + "手" + self.chicang_record2['类型'] + '单  ' \
                       + str(self.chicang_record2['开仓均价']) + '  ' + str(self.chicang_record2['逐笔盈亏'])
            self.line_chicang_record2 = pg.InfiniteLine(pos=(0, float(self.chicang_record2['开仓均价'])),
                                                        movable=False,
                                                        angle=0, pen=(205, 192, 176), label=html_str,
                                                        labelOpts={'position': 0.1, 'color': (255, 255, 255),
                                                                   'movable': True, 'fill': (205, 192, 176, 150)})
            self.pw.addItem(self.line_chicang_record2, ignoreBounds=True)

        # 十字线
        self.vLine = pg.InfiniteLine(angle=90, movable=False)  # 垂直线
        self.hLine = pg.InfiniteLine(angle=0, movable=False)  # 水平线
        self.label = pg.TextItem()
        self.pw.addItem(self.vLine, ignoreBounds=True)
        self.pw.addItem(self.hLine, ignoreBounds=True)
        self.pw.addItem(self.label, ignoreBounds=True)

        # 2.成交量
        vol_fixed_target = VolItem(vol_data)
        self.pw2.addItem(vol_fixed_target)
        self.vLine2 = pg.InfiniteLine(angle=90, movable=False)
        self.pw2.addItem(self.vLine2, ignoreBounds=True)
        self.pw2.setYRange(df['volume'].min(), df['volume'].max())

        # 4.指标 KDJ
        self.vLine4 = pg.InfiniteLine(angle=90, movable=False)
        self.pw4.addItem(self.vLine4, ignoreBounds=True)
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

        self.pw.setXLink(self.pw)
        self.pw2.setXLink(self.pw)
        self.pw4.setXLink(self.pw)
        self.pw.enableAutoRange()
        self.pw2.enableAutoRange()
        self.pw4.enableAutoRange()
        self.vb = self.pw.getViewBox()
        self.proxy = pg.SignalProxy(self.pw.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)
        self.proxy2 = pg.SignalProxy(self.pw2.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)
        self.proxy4 = pg.SignalProxy(self.pw4.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)
        self.pw.addLegend(size=(40, 40))
        self.pw2.addLegend(size=(40, 40))
        self.pw4.addLegend(size=(40, 40))
        return True
        pass

    # 鼠标移动
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
                for i, item in enumerate(self.whole_pd_header_Chinese):
                    html_str += f"<br/>{item}:{target_data[i]}"
                self.label.setHtml(html_str)
                self.label.setPos(mousePoint.x(), mousePoint.y())
            # 设置垂直线条和水平线条的位置组成十字光标
            self.vLine.setPos(mousePoint.x())
            self.hLine.setPos(mousePoint.y())
            self.vLine2.setPos(mousePoint.x())
            self.vLine4.setPos(mousePoint.x())


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.show()  # 显示窗体,使控件可见(默认是隐藏)
    sys.exit(app.exec_())  # 程序关闭时退出进程
