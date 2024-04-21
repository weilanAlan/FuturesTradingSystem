import time
import json

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
import sqlite3
from pandas.core.frame import DataFrame

from finalPractice.CandlestickItem import CandlestickItem
from finalPractice.SegmenttickItem import SegmenttickItem
from finalPractice.VolItem import VolItem
from finalPractice.tradeDemo import tradeDemo
from finalPractice.datadisplay import Ui_MainWindow

pg.setConfigOption('background', 'k')
pg.setConfigOption('foreground', 'w')

# 设置全局变量：合约名称
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
        self.read_db()  # 读取数据库
        self.hline_tradepoint_dict = None
        self.chicang_symbol = None
        self.chicang_record = None
        self.chicang_record2 = None

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
        # duration_sel_btn.setStyleSheet("QPushButton{color:rgb(0,0,0);font-size:15;font-weight:bold;font-family:宋体;}")
        duration_sel_btn.clicked.connect(self.duration_sel_btn_clicked)
        duration_trade_btn = QtWidgets.QPushButton('下单')
        # duration_trade_btn.setStyleSheet("QPushButton{color:rgb(0,0,0);font-size:15;font-weight:bold;font-family:宋体;}")
        duration_trade_btn.clicked.connect(self.duration_trade_btn_clicked)
        self.whole_duration_label = QtWidgets.QLabel('所有范围：左边界~右边界')
        self.now_duration_label = QtWidgets.QLabel('当前范围：左边界~右边界')

        # 设置值
        self.title_label.setText(symbol)
        self.getCurrentData()  # 设置self.current_data:symbol下的所有数据

        # 画默认的图(先只画前100个)verticalLayout_kline_graph 以及日期
        graph = PyQtGraphLineWidget()
        self.whole_duration_label.setText(
            f"原始边界：{self.current_data.iloc[0]['datetime']}~{self.current_data.iloc[-1]['datetime']}")
        self.current_data = self.current_data.iloc[0:min(100, len(self.current_data))]  # 默认最多100个
        self.newest_data = self.data.loc[self.data['datetime']==self.current_data.iloc[-1]['datetime']]
        self.now_duration_label.setText(
            f"当前边界：{self.current_data.iloc[0]['datetime']}~{self.current_data.iloc[min(100, len(self.current_data)) - 1]['datetime']}")
        graph.set_data(self.dealwithData(), self.hline_tradepoint_dict, self.chicang_record, self.chicang_record2)
        self.verticalLayout_kline_graph.addWidget(graph)

        # 布局verticalLayout_dateframe
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
        # layout_date.addItem(spacerItem2)
        layout_date.addWidget(self.check_box_bulin)
        layout_date.addItem(spacerItem1)
        layout_date.addWidget(duration_sel_btn)
        layout_date.addItem(spacerItem2)
        layout_date.addWidget(duration_trade_btn)
        layout_date.addItem(spacerItem1)
        layout_duration = QtWidgets.QHBoxLayout()
        layout_duration.addWidget(self.whole_duration_label)
        layout_duration.addItem(spacerItem2)
        layout_duration.addWidget(self.now_duration_label)
        layout_duration.addItem(spacerItem1)
        self.verticalLayout_dateframe.addWidget(self.title_label)
        self.verticalLayout_dateframe.addLayout(layout_date)
        self.verticalLayout_dateframe.addLayout(layout_duration)
        # 设置间距
        # self.layout.setSpacing(2)
        # self.setLayout(self.layout)
        # mainwidget = QWidget()
        # mainwidget.setLayout(self.layout)
        # self.setCentralWidget(mainwidget)

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
        # 正常执行SQL查询
        # c.execute("select * from dbbardata where symbol='%s'" % (symbol))
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
        # df = ak.futures_zh_minute_sina(symbol=contract, period="1")
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
        #  封装数据
        # whole_pd_header = ['tradeDate', 'closePrice', 'openPrice', 'highestPrice', 'lowestPrice', 'ma5', 'ma10', 'ma20',
        #                    'ma30', 'ma60', 'volume', 'DIFF', 'DEA', 'MACD', 'kdj_k', 'kdj_d', 'kdj_j']
        whole_pd_header = ['tradeDate', 'closePrice', 'openPrice', 'highestPrice', 'lowestPrice', 'volume']
        line_data = {
            'title_str': symbol,
            'whole_pd_header': whole_pd_header,
            'whole_pd_header_Chinese': ['日期', '收盘价', '开盘价', '最高价', '最低价', '成交量'],
            'whole_df': df
            # # 需要展示的参数
            # 'required_header': ['日期', '收盘价', '开盘价', '最高价', '最低价', '成交量'],
            # 'required_pd_header': ['tradeDate', 'closePrice', 'openPrice', 'highestPrice', 'lowestPrice', 'volume']
        }
        return line_data

    # 下拉框选择新的合约后触发（切换合约后时间按设定的，否则默认）
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
        # left_point = self.left_point.date().toString('yyyy-MM-dd')
        # right_point = self.right_point.date().toString('yyyy-MM-dd')
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
        # left_point = self.left_point.date().toString('yyyy-MM-dd')
        # right_point = self.right_point.date().toString('yyyy-MM-dd')
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
        self.tradedemo.signal1.connect(self.receive_tradepoint)
        self.tradedemo.signal2.connect(self.receive_chicang_record)
        self.tradedemo.signal_symbol.connect(self.receive_new_symbol)
        self.tradedemo.set_data(symbol, df)

    def select_dayK(self):
        self.statusbar.showMessage("日k")
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
        # self.current_data['datetime'] = self.current_data['datetime'].apply(lambda x: x.strftime('%Y-%m-%d'))
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
        else:
            # clear之前画的图
            for i in range(self.verticalLayout_kline_graph.count()):
                self.verticalLayout_kline_graph.itemAt(i).widget().deleteLater()
            graph = PyQtGraphLineWidget()
            graph.set_data(self.dealwithData(), self.hline_tradepoint_dict, self.chicang_record, self.chicang_record2)
            self.verticalLayout_kline_graph.addWidget(graph)

    def select_weekK(self):
        self.statusbar.showMessage("周k")
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
        # self.current_data['datetime'] = self.current_data['datetime'].apply(lambda x: x.strftime('%Y-%m-%d'))
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
        else:
            # clear之前画的图
            for i in range(self.verticalLayout_kline_graph.count()):
                self.verticalLayout_kline_graph.itemAt(i).widget().deleteLater()
            graph = PyQtGraphLineWidget()
            graph.set_data(self.dealwithData(), self.hline_tradepoint_dict, self.chicang_record, self.chicang_record2)
            self.verticalLayout_kline_graph.addWidget(graph)

    def select_monthK(self):
        self.statusbar.showMessage("月k")
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
        # self.current_data['datetime'] = self.current_data['datetime'].apply(lambda x: x.strftime('%Y-%m-%d'))
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
        else:
            # clear之前画的图
            for i in range(self.verticalLayout_kline_graph.count()):
                self.verticalLayout_kline_graph.itemAt(i).widget().deleteLater()
            graph = PyQtGraphLineWidget()
            graph.set_data(self.dealwithData(), self.hline_tradepoint_dict, self.chicang_record, self.chicang_record2)
            self.verticalLayout_kline_graph.addWidget(graph)

    def select_quarterK(self):
        self.statusbar.showMessage("季k")
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
        # self.current_data['datetime'] = self.current_data['datetime'].apply(lambda x: x.strftime('%Y-%m-%d'))
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
        else:
            # clear之前画的图
            for i in range(self.verticalLayout_kline_graph.count()):
                self.verticalLayout_kline_graph.itemAt(i).widget().deleteLater()
            graph = PyQtGraphLineWidget()
            graph.set_data(self.dealwithData(), self.hline_tradepoint_dict, self.chicang_record, self.chicang_record2)
            self.verticalLayout_kline_graph.addWidget(graph)

    def select_yearK(self):
        self.statusbar.showMessage("年k")
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
        # self.current_data['datetime'] = self.current_data['datetime'].apply(lambda x: x.strftime('%Y-%m-%d'))
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
        else:
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
        self.statusbar.showMessage("3分钟k")
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
        # self.current_data['datetime'] = self.current_data['datetime'].apply(lambda x: x.strftime('%Y-%m-%d'))
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
        else:
            # clear之前画的图
            for i in range(self.verticalLayout_kline_graph.count()):
                self.verticalLayout_kline_graph.itemAt(i).widget().deleteLater()
            graph = PyQtGraphLineWidget()
            graph.set_data(self.dealwithData(), self.hline_tradepoint_dict, self.chicang_record, self.chicang_record2)
            self.verticalLayout_kline_graph.addWidget(graph)

    def select_5min(self):
        self.statusbar.showMessage("5分钟k")
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
        # self.current_data['datetime'] = self.current_data['datetime'].apply(lambda x: x.strftime('%Y-%m-%d'))
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
        else:
            # clear之前画的图
            for i in range(self.verticalLayout_kline_graph.count()):
                self.verticalLayout_kline_graph.itemAt(i).widget().deleteLater()
            graph = PyQtGraphLineWidget()
            graph.set_data(self.dealwithData(), self.hline_tradepoint_dict, self.chicang_record, self.chicang_record2)
            self.verticalLayout_kline_graph.addWidget(graph)

    def select_10min(self):
        self.statusbar.showMessage("10分钟k")
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
        # self.current_data['datetime'] = self.current_data['datetime'].apply(lambda x: x.strftime('%Y-%m-%d'))
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
        else:
            # clear之前画的图
            for i in range(self.verticalLayout_kline_graph.count()):
                self.verticalLayout_kline_graph.itemAt(i).widget().deleteLater()
            graph = PyQtGraphLineWidget()
            graph.set_data(self.dealwithData(), self.hline_tradepoint_dict, self.chicang_record, self.chicang_record2)
            self.verticalLayout_kline_graph.addWidget(graph)

    def select_15min(self):
        self.statusbar.showMessage("15分钟k")
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
        # self.current_data['datetime'] = self.current_data['datetime'].apply(lambda x: x.strftime('%Y-%m-%d'))
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
        else:
            # clear之前画的图
            for i in range(self.verticalLayout_kline_graph.count()):
                self.verticalLayout_kline_graph.itemAt(i).widget().deleteLater()
            graph = PyQtGraphLineWidget()
            graph.set_data(self.dealwithData(), self.hline_tradepoint_dict, self.chicang_record, self.chicang_record2)
            self.verticalLayout_kline_graph.addWidget(graph)

    def select_30min(self):
        self.statusbar.showMessage("30分钟k")
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
        # self.current_data['datetime'] = self.current_data['datetime'].apply(lambda x: x.strftime('%Y-%m-%d'))
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
        else:
            # clear之前画的图
            for i in range(self.verticalLayout_kline_graph.count()):
                self.verticalLayout_kline_graph.itemAt(i).widget().deleteLater()
            graph = PyQtGraphLineWidget()
            graph.set_data(self.dealwithData(), self.hline_tradepoint_dict, self.chicang_record, self.chicang_record2)
            self.verticalLayout_kline_graph.addWidget(graph)

    def select_1h(self):
        self.statusbar.showMessage("1小时k")
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
        # self.current_data['datetime'] = self.current_data['datetime'].apply(lambda x: x.strftime('%Y-%m-%d'))
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
        else:
            # clear之前画的图
            for i in range(self.verticalLayout_kline_graph.count()):
                self.verticalLayout_kline_graph.itemAt(i).widget().deleteLater()
            graph = PyQtGraphLineWidget()
            graph.set_data(self.dealwithData(), self.hline_tradepoint_dict, self.chicang_record, self.chicang_record2)
            self.verticalLayout_kline_graph.addWidget(graph)

    def select_2h(self):
        self.statusbar.showMessage("2小时k")
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
        # self.current_data['datetime'] = self.current_data['datetime'].apply(lambda x: x.strftime('%Y-%m-%d'))
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
        else:
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

    def receive_chicang_record(self, str, dict, dict2):
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


#  所有图表（K线图、均线、vol、macd、kdj）显示的控件
#  self.whole_df:该symbol下、接收到的所有数据
#  self.whole_pd_header:该symbol下的所有列名
#  self.whole_pd_header_Chinese:该symbol下的所有中文列名
#  self.current_whole_data:该symbol下的所有列的数据，后续要操作
#  self.pw:k线图的地方
#  self.timer：定时器
#  self.points:当前最近更新页面上绘制的30个（或更少）数据
#  self.current_whole_df:边界选择之后的数据
#  self.whole_duration_label:'原始边界：左边界~右边界'
#  self.now_duration_label:'当前边界：左边界~右边界'
class PyQtGraphLineWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.init_data()
        self.init_ui()
        # self.timerStart()  # 开始画图
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
        self.current_whole_df = None  # 边界选择之后的数据
        pass

    def init_ui(self):
        # 设置定时器
        # self.timer = QTimer(self)
        # self.timer.timeout.connect(self.newPointPlot)

        # 1.一些标题
        self.vol_label = QtWidgets.QLabel('持仓量')
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
        # self.pw.enableAutoRange(x=False,y=True)
        self.pw.setAutoVisible(x=False, y=False)

        # 3.vol
        x2 = AxisItem(orientation='bottom')  # x轴
        x2.setHeight(h=20)
        self.pw2 = pg.PlotWidget(axisItems={'bottom': x2})
        self.pw2.setMouseEnabled(x=True, y=False)
        # self.pw2.enableAutoRange(x=False,y=True)
        self.pw2.setAutoVisible(x=False, y=True)

        # 4.macd&kdj
        # spacerItem1 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        # self.layout_button = QHBoxLayout()
        # self.button_macd = QPushButton()
        # self.button_macd.setText("MACD")
        # self.button_kdj = QPushButton()
        # self.button_kdj.setText("KDJ")
        # self.button_macd.clicked.connect(self.button_macd_clicked)
        # self.button_kdj.clicked.connect(self.button_kdj_clicked)
        # self.layout_button.addWidget(self.button_macd)
        # self.layout_button.addWidget(self.button_kdj)
        # self.layout_button.addItem(spacerItem1)
        # self.stackedwidget = QStackedWidget()
        # self.stackedwidget.setCurrentIndex(0)

        # x3 = AxisItem(orientation='bottom')  # macd x轴
        # x3.setHeight(h=20)
        # self.pw3 = pg.PlotWidget(axisItems={'bottom': x3})
        # self.pw3.setMouseEnabled(x=True, y=False)
        # self.pw3.setAutoVisible(x=False, y=True)
        x4 = AxisItem(orientation='bottom')  # kdj x轴
        x4.setHeight(h=20)
        self.pw4 = pg.PlotWidget(axisItems={'bottom': x4})
        self.pw4.setMouseEnabled(x=True, y=False)
        self.pw4.setAutoVisible(x=False, y=True)
        # self.stackedwidget.addWidget(self.pw3)
        # self.stackedwidget.addWidget(self.pw4)

        # 5.最后，加入布局
        self.layout2 = QtWidgets.QVBoxLayout()
        self.layout2.addWidget(self.pw)
        self.layout2.addWidget(self.vol_label)
        self.layout2.addWidget(self.pw2)
        # self.layout2.addLayout(self.layout_button)
        # self.layout2.addWidget(self.stackedwidget)
        # self.layout2.addWidget(self.pw3)
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
        # self.current_whole_df = self.whole_df.iloc[0:min(30, len(self.whole_df))]
        self.whole_pd_header = data['whole_pd_header']  # 所有列名
        self.whole_pd_header_Chinese = data['whole_pd_header_Chinese']  # 所有列名的中文
        self.hline_tradepoint_dict = hline_tradepoint_dict  # 当前交易点的dict
        self.chicang_record = chicang_record  # 当前选中的持仓记录
        self.chicang_record2 = chicang_record2  # 相同symbol，另一种类型的持仓记录

        self.caculate_and_show_data()
        pass

    # 画当前画布的数据
    def caculate_and_show_data(self):
        # df = self.points.copy()
        df = self.whole_df.copy()
        df.reset_index(inplace=True)
        tradeDate_list = df['tradeDate'].values.tolist()
        x = range(len(df))
        xTick_show = []
        # if len(tradeDate_list) > 100:
        #     x_dur = math.ceil(len(tradeDate_list) / 5)
        # else:
        #     x_dur = math.ceil(len(tradeDate_list) / 5)
        # # x_dur = math.ceil(len(df) / 20)
        # for i in range(0, len(df), x_dur):
        #     xTick_show.append((i, tradeDate_list[i]))
        # if len(df) % 5 != 0:
        #     xTick_show.append((len(df) - 1, tradeDate_list[-1]))
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
        # xax3 = self.pw3.getAxis('bottom')
        # xax3.setTicks([xTick_show])
        xax4 = self.pw4.getAxis('bottom')
        xax4.setTicks([xTick_show])

        # 开始配置显示的内容
        self.pw.clear()
        self.pw2.clear()
        # self.pw3.clear()
        self.pw4.clear()

        # 1.画k线图
        candle_fixed_target = CandlestickItem(candle_data)
        self.main_fixed_target_list.append(candle_fixed_target)
        self.pw.addItem(candle_fixed_target)

        # 要显示均线
        if average_state == 1:
            # self.pw.addLegend(size=(40, 40))
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
            # self.line_tradepoint = pg.InfiniteLine(angle=0, movable=False)
            # self.label_tradepoint = pg.TextItem()
            # self.line_tradepoint.setPos(self.hline_tradepoint_dict['成交价'])
            if self.hline_tradepoint_dict['类型'] == '买开':
                html_str = str(self.hline_tradepoint_dict['成交量']) + "手开多  " + str(self.hline_tradepoint_dict['成交价'])
                self.line_tradepoint = pg.InfiniteLine(pos=(0, self.hline_tradepoint_dict['成交价']), movable=False, angle=0, pen=self.color_kai,
                                      label=html_str,
                                      labelOpts={'position': 0.05, 'color': (255, 255, 255), 'movable': True,
                                                 'fill': (self.color_kai[0], self.color_kai[1], self.color_kai[2], 150)})
            else:
                html_str = str(self.hline_tradepoint_dict['成交量']) + "手开空  " + str(self.hline_tradepoint_dict['成交价'])
                self.line_tradepoint = pg.InfiniteLine(pos=(0, self.hline_tradepoint_dict['成交价']), movable=False,
                                                       angle=0, pen=self.color_kong,
                                                       label=html_str,
                                                       labelOpts={'position': 0.05, 'color': (255, 255, 255), 'movable': False,
                                                                  'fill': (self.color_kong[0], self.color_kong[1],
                                                                           self.color_kong[2], 150)})
            # self.label_tradepoint.setHtml(html_str)
            # self.label_tradepoint.setPos(0, self.hline_tradepoint_dict['成交价'])
            self.pw.addItem(self.line_tradepoint, ignoreBounds=True)
            # self.pw.addItem(self.label_tradepoint, ignoreBounds=True)

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

        # 2.持仓量
        vol_fixed_target = VolItem(vol_data)
        self.pw2.addItem(vol_fixed_target)
        self.vLine2 = pg.InfiniteLine(angle=90, movable=False)
        # self.hLine2 = pg.InfiniteLine(angle=0, movable=False)
        self.pw2.addItem(self.vLine2, ignoreBounds=True)
        self.pw2.setYRange(df['volume'].min(), df['volume'].max())

        # # 3.指标 MACD
        # self.vLine3 = pg.InfiniteLine(angle=90, movable=False)
        # # self.hLine3 = pg.InfiniteLine(angle=0, movable=False)
        # self.pw3.addItem(self.vLine3, ignoreBounds=True)
        # # self.pw3.addItem(self.hLine3, ignoreBounds=True)
        # segment_fixed_target = SegmenttickItem(segment_data)
        # diff_fixed_target = pg.PlotCurveItem(x=np.array(x), y=np.array(df['DIFF'].values.tolist()),
        #                                      pen=pg.mkPen({'color': self.color_ma_5, 'width': 1}),
        #                                      connect='finite')
        # dea_fixed_target = pg.PlotCurveItem(x=np.array(x), y=np.array(df['DEA'].values.tolist()),
        #                                     pen=pg.mkPen({'color': self.color_ma_10, 'width': 1}),
        #                                     connect='finite')
        # self.main_fixed_target_list.append(diff_fixed_target)
        # self.main_fixed_target_list.append(dea_fixed_target)
        # self.main_fixed_target_list.append(segment_fixed_target)
        # self.pw3.addItem(segment_fixed_target)
        # self.pw3.addItem(diff_fixed_target)
        # self.pw3.addItem(dea_fixed_target)

        # 4.指标 KDJ
        self.vLine4 = pg.InfiniteLine(angle=90, movable=False)
        # self.hLine4 = pg.InfiniteLine(angle=0, movable=False)
        self.pw4.addItem(self.vLine4, ignoreBounds=True)
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

        self.pw.setXLink(self.pw)
        self.pw2.setXLink(self.pw)
        # self.pw3.setXLink(self.pw)
        self.pw4.setXLink(self.pw)
        self.pw.enableAutoRange()
        self.pw2.enableAutoRange()
        # self.pw3.enableAutoRange()
        self.pw4.enableAutoRange()
        self.vb = self.pw.getViewBox()
        self.proxy = pg.SignalProxy(self.pw.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)
        self.proxy2 = pg.SignalProxy(self.pw2.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)
        # self.proxy3 = pg.SignalProxy(self.pw3.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)
        self.proxy4 = pg.SignalProxy(self.pw4.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)
        self.pw.addLegend(size=(40, 40))
        self.pw2.addLegend(size=(40, 40))
        # self.pw3.addLegend(size=(40, 40))
        self.pw4.addLegend(size=(40, 40))


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
                for i, item in enumerate(self.whole_pd_header_Chinese):
                    html_str += f"<br/>{item}:{target_data[i]}"
                self.label.setHtml(html_str)
                self.label.setPos(mousePoint.x(), mousePoint.y())
            # 设置垂直线条和水平线条的位置组成十字光标
            self.vLine.setPos(mousePoint.x())
            self.hLine.setPos(mousePoint.y())
            self.vLine2.setPos(mousePoint.x())
            # self.vLine3.setPos(mousePoint.x())
            self.vLine4.setPos(mousePoint.x())
            # self.hLine2.setPos(mousePoint.y())
        pass

    # 右键菜单
    def contextMenuEvent(self, event):
        menu =QMenu(self)
        action = QAction("下单", self)
        action.triggered.connect(self.trade)
        menu.addAction(action)
        menu.exec_(QtGui.QCursor().pos())

    # def button_macd_clicked(self):
    #     self.stackedwidget.setCurrentIndex(0)
    #
    # def button_kdj_clicked(self):
    #     self.stackedwidget.setCurrentIndex(1)

    pass


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    # window.setWindowState(Qt.WindowMaximized)
    window.show()  # 显示窗体,使控件可见(默认是隐藏)
    sys.exit(app.exec_())  # 程序关闭时退出进程
