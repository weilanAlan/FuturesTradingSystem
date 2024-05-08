import tkinter as tk
from tkinter import ttk
from tkinter import *
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

strategy_list = ['双均线策略', 'Dual Thrust策略', '菲阿里四价策略']
# strategy_list = ['双均线策略', '菲阿里四价策略']
codelist = ['RB888', 'RB99', 'SA99', 'SA888', 'jm888', 'jm99']  # 存储期货代码
dict_tradeunit = {'RB888': 10, 'RB99': 10, 'SA99': 20, 'SA888': 20, 'jm888': 60, 'jm99': 60}
dict_marginratio = {'RB888': 0.07, 'RB99': 0.07, 'SA99': 0.12, 'SA888': 0.12, 'jm888': 0.2, 'jm99': 0.2}
initial_cash = 30000


class quantitativeTradingDemo:
    def __init__(self):
        super().__init__()

    def set_data(self, data, str1, str2):
        self.data = pd.DataFrame(data, columns=['symbol', 'datetime', 'close', 'open', 'high', 'low', 'volume'])
        self.data['openinterest'] = 0
        self.left_time = str1
        self.right_time = str2
        self.plot_df = None
        self.init_ui()

    # 初始化界面
    def init_ui(self):
        self.gui = tk.Tk()
        self.gui.title('量化交易界面')
        self.gui.geometry('1500x800')
        # 设置框架
        self.frame1 = tk.LabelFrame(self.gui, text="参数选择", width=1500, height=100)
        self.frame1.place(x=0, y=0)
        self.frame2 = tk.LabelFrame(self.gui, text="量化策略", width=750, height=700)
        self.frame2.place(x=0, y=100)
        self.frame3 = tk.LabelFrame(self.gui, text="交易记录", width=750, height=700)
        self.frame3.place(x=750, y=100)
        # frame1设计:回测时间、初始资金、量化策略
        l_time = tk.Label(self.frame1, text='回测时间:')
        l_time.place(x=5, y=15)
        s1 = tk.StringVar()
        s1.set(self.left_time)
        l_left_time = tk.Label(self.frame1, textvariable=s1, width=18, height=1)
        l_left_time.place(x=85, y=15)
        l_seperate = tk.Label(self.frame1, text='~')
        l_seperate.place(x=290, y=15)
        s2 = tk.StringVar()
        s2.set(self.right_time)
        l_right_time = tk.Label(self.frame1, textvariable=s2, width=18, height=1)
        l_right_time.place(x=310, y=15)
        l_initial_cash = tk.Label(self.frame1, text='初始资金:')
        l_initial_cash.place(x=670, y=15)
        s3 = tk.StringVar()
        s3.set(str(30000))
        l_cash = tk.Label(self.frame1, textvariable=s3, height=1)
        l_cash.place(x=755, y=15)
        l_strategy = tk.Label(self.frame1, text='合约选择:')
        l_strategy.place(x=970, y=15)
        self.combo_box = ttk.Combobox(self.frame1, values=codelist, width=10)
        self.combo_box.place(x=1060, y=15)
        self.symbol = 'RB888'
        self.combo_box.current(codelist.index('RB888'))
        self.combo_box.bind("<<ComboboxSelected>>", self.change_symbol)
        # frame2设计
        self.fig = plt.figure(figsize=(5, 4.5), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, self.frame2)  # 将fig与窗体关联
        self.var1 = tk.BooleanVar()
        self.checkbox = tk.Checkbutton(self.frame2, text="是否显示Dual Thrust策略", variable=self.var1, onvalue=True,
                                       offvalue=False, command=lambda: self.plot_graph(self.plot_df, self.fig, self.canvas))
        self.checkbox.place(x=0, y=0)
        self.canvas.get_tk_widget().pack()
        # frame3设计
        scrollbar_y = Scrollbar(self.frame3, orient=VERTICAL)  # 滚动条
        style = ttk.Style()
        style.configure("Treeview", rowheight=22)
        self.tree = ttk.Treeview(self.frame3, columns=('时间', '类型', '成交量', '成交价', '平仓盈亏'), height=28,
                                 show="tree headings", displaycolumns="#all", yscrollcommand=scrollbar_y.set)
        self.tree.column("时间", width=210, anchor='center')
        self.tree.column("类型", width=70, anchor='center')
        self.tree.column("成交量", width=70, anchor='center')
        self.tree.column("成交价", width=80, anchor='center')
        self.tree.column("平仓盈亏", width=80, anchor='center')
        self.tree.heading("时间", text="时间")
        self.tree.heading("类型", text="类型")
        self.tree.heading("成交量", text="成交量")
        self.tree.heading("成交价", text="成交价")
        self.tree.heading("平仓盈亏", text="平仓盈亏")
        # 根节点、子节点
        self.list_tree = []
        self.tree.tag_configure('tag_sum', background="lightgrey")
        self.root = self.tree.insert('', END, text="量化交易记录")
        for i in range(len(strategy_list)):
            self.list_tree.append(self.tree.insert(self.root, END, text=strategy_list[i]))
        scrollbar_y.config(command=self.tree.yview)
        scrollbar_y.pack(side=RIGHT, fill=Y)
        self.tree.pack(fill=BOTH, expand=True)
        self.calculate_graph(self.fig, self.canvas)
        self.gui.mainloop()

    def change_symbol(self, aaa):
        self.symbol = self.combo_box.get()
        print(self.symbol)
        # 清除表格
        x = self.tree.get_children()
        for item in x:
            self.tree.delete(item)
        self.list_tree = []
        self.tree.tag_configure('tag_sum', background="lightgrey")
        self.root = self.tree.insert('', END, text="量化交易记录")
        for i in range(len(strategy_list)):
            self.list_tree.append(self.tree.insert(self.root, END, text=strategy_list[i]))
        self.calculate_graph(self.fig, self.canvas)

    def calculate_graph(self, fig, canvas):
        global initial_cash
        df = pd.DataFrame(self.data, columns=['symbol', 'datetime', 'open', 'close', 'high', 'low'])
        df = df[df['symbol'] == self.symbol]
        # 1.双均线策略
        # 短周期为20，长周期为60
        # 当短期均线由下向上穿越长期均线时做多,当短期均线由上向下穿越长期均线时做空
        # 每次开仓前先平掉所持仓位，再开仓
        self.chicang_num_duo = [0, 0, 0]
        self.chicang_num_kong = [0, 0, 0]
        initial_cash = 30000
        chengjiao_dict = []
        df['position1'] = 0
        df['remain1'] = 30000
        short_window = 20
        long_window = 60
        df['short_MA'] = df['close'].rolling(window=short_window).mean()
        df['long_MA'] = df['close'].rolling(window=long_window).mean()
        # 交易逻辑
        for i in range(len(df)):
            if i < long_window:
                continue
            else:
                # 短均线上穿长均线，做多（即当前时间点短均线处于长均线上方，前一时间点短均线处于长均线下方）
                if df.iloc[i - 1]['short_MA'] < df.iloc[i - 1]['long_MA'] and df.iloc[i]['short_MA'] >= df.iloc[i][
                    'long_MA']:
                    if self.chicang_num_kong[0] == 0:  # 无空仓情况下，直接开多
                        initial_cash -= dict_tradeunit[self.symbol] * df.iloc[i]['close'] * dict_marginratio[
                            self.symbol]
                        tempt_dict = {'时间': df.iloc[i]['datetime'], '类型': '买开', '成交量': 1,
                                      '成交价': df.iloc[i]['close'], '平仓盈亏': '-', '已平仓手数': 0}
                        chengjiao_dict.append(tempt_dict)
                        self.chicang_num_duo[0] += 1
                    else:  # 有空仓情况下，先平空，再开多
                        # 平空
                        initial_cash += dict_tradeunit[self.symbol] * df.iloc[i]['close'] * dict_marginratio[
                            self.symbol] * self.chicang_num_kong[0]
                        profitandloss = 0
                        for ii in chengjiao_dict:
                            if ii['类型'] == '卖开' and ii['已平仓手数'] == 0:
                                profitandloss += (ii['成交量'] * (ii['成交价'] - df.iloc[i]['close']) * dict_tradeunit[
                                    self.symbol])
                                ii['已平仓手数'] = ii['成交量']
                        tempt_dict = {'时间': df.iloc[i]['datetime'], '类型': '买平',
                                      '成交量': self.chicang_num_kong[0],
                                      '成交价': df.iloc[i]['close'], '平仓盈亏': round(profitandloss, 2)}
                        chengjiao_dict.append(tempt_dict)
                        self.chicang_num_kong[0] = 0
                        # 买多
                        initial_cash -= dict_tradeunit[self.symbol] * df.iloc[i]['close'] * dict_marginratio[
                            self.symbol]
                        tempt_dict = {'时间': df.iloc[i]['datetime'], '类型': '买开', '成交量': 1,
                                      '成交价': df.iloc[i]['close'], '平仓盈亏': '-', '已平仓手数': 0}
                        chengjiao_dict.append(tempt_dict)
                        self.chicang_num_duo[0] += 1
                    df.loc[df['datetime'] == df.iloc[i]['datetime'], 'remain1'] = initial_cash
                #  短均线下穿长均线，做空(即当前时间点短均线处于长均线下方，前一时间点短均线处于长均线上方)
                elif df.iloc[i - 1]['short_MA'] > df.iloc[i - 1]['long_MA'] and df.iloc[i]['short_MA'] <= df.iloc[i][
                    'long_MA']:
                    if self.chicang_num_duo[0] == 0:  # 无多仓情况下，直接开空
                        initial_cash -= dict_tradeunit[self.symbol] * df.iloc[i]['close'] * dict_marginratio[
                            self.symbol]
                        tempt_dict = {'时间': df.iloc[i]['datetime'], '类型': '卖开', '成交量': 1,
                                      '成交价': df.iloc[i]['close'], '平仓盈亏': '-', '已平仓手数': 0}
                        chengjiao_dict.append(tempt_dict)
                        self.chicang_num_kong[0] += 1
                    else:  # 有多仓情况下，先平多，再开空
                        # 平多
                        initial_cash += dict_tradeunit[self.symbol] * df.iloc[i]['close'] * dict_marginratio[
                            self.symbol] * self.chicang_num_duo[0]
                        profitandloss = 0
                        for ii in chengjiao_dict:
                            if ii['类型'] == '买开' and ii['已平仓手数'] == 0:
                                profitandloss += (ii['成交量'] * (df.iloc[i]['close'] - ii['成交价']) * dict_tradeunit[
                                    self.symbol])
                                ii['已平仓手数'] = ii['成交量']
                        tempt_dict = {'时间': df.iloc[i]['datetime'], '类型': '卖平', '成交量': self.chicang_num_duo[0],
                                      '成交价': df.iloc[i]['close'], '平仓盈亏': round(profitandloss, 2)}
                        chengjiao_dict.append(tempt_dict)
                        self.chicang_num_duo[0] = 0
                        # 卖空
                        initial_cash -= dict_tradeunit[self.symbol] * df.iloc[i]['close'] * dict_marginratio[
                            self.symbol]
                        tempt_dict = {'时间': df.iloc[i]['datetime'], '类型': '卖开', '成交量': 1,
                                      '成交价': df.iloc[i]['close'], '平仓盈亏': '-', '已平仓手数': 0}
                        chengjiao_dict.append(tempt_dict)
                        self.chicang_num_kong[0] += 1
                    df.loc[df['datetime'] == df.iloc[i]['datetime'], 'remain1'] = initial_cash
                else:
                    df.loc[df['datetime'] == df.iloc[i]['datetime'], 'remain1'] = df.iloc[i - 1]['remain1']
                df.loc[df['datetime'] == df.iloc[i]['datetime'], 'position1'] = df.iloc[i]['close'] * dict_tradeunit[
                    self.symbol] * dict_marginratio[self.symbol] * (self.chicang_num_duo[0] + self.chicang_num_kong[0])
        shoushu = 0
        yingkui = 0
        for i in chengjiao_dict:
            self.tree.insert(self.list_tree[0], END, values=(
                i['时间'], i['类型'], i['成交量'], i['成交价'], i['平仓盈亏']))
            shoushu += i['成交量']
            if i['平仓盈亏'] != '-':
                yingkui += float(i['平仓盈亏'])
        self.tree.insert(self.list_tree[0], END, values=('总计', '', shoushu, '', round(yingkui, 2)), tags='tag_sum')
        self.tree.insert(self.list_tree[0], END, values=('', '', '', '', '', ''))
        df['total_value1'] = df['position1'] + df['remain1']

        # 3.菲阿里四价策略
        # 一种日内策略交易，适合短线投资者。
        # 菲阿里四价指的是：昨日高点、昨日低点、昨天收盘、今天开盘四个价格。
        # 如果有多头持仓，当价格跌破了开盘价止损。
        # 如果有空头持仓，当价格上涨超过开盘价止损。
        # 如果没有持仓，且现价大于了昨天最高价做多，小于昨天最低价做空。
        initial_cash = 30000
        chengjiao_dict = []
        df['position3'] = 0
        df['remain3'] = 30000
        flag = 0
        # 设置参数
        open = df['open'].iloc[-1]  # 开盘价直接在data最后一个数据里取到,前一交易日的最高和最低价为history_data里面的倒数第二条中取到
        high = df['high'].iloc[-2]
        low = df['low'].iloc[-2]
        # 交易逻辑部分
        for i in range(len(df)):
            if self.chicang_num_duo[2] != 0:  # 持多仓
                if df.iloc[i]['close'] < open:  # 小于开盘价止损(平多)
                    # 平多
                    initial_cash += dict_tradeunit[self.symbol] * df.iloc[i]['close'] * dict_marginratio[self.symbol] * \
                                    self.chicang_num_duo[2]
                    profitandloss = 0
                    for ii in chengjiao_dict:
                        if ii['类型'] == '买开' and ii['已平仓手数'] == 0:
                            profitandloss += (ii['成交量'] * (df.iloc[i]['close'] - ii['成交价']) * dict_tradeunit[
                                self.symbol])
                            ii['已平仓手数'] = ii['成交量']
                    tempt_dict = {'时间': df.iloc[i]['datetime'], '类型': '卖平', '成交量': self.chicang_num_duo[2],
                                  '成交价': df.iloc[i]['close'], '平仓盈亏': round(profitandloss, 2)}
                    chengjiao_dict.append(tempt_dict)
                    self.chicang_num_duo[2] = 0
                    df.loc[df['datetime'] == df.iloc[i]['datetime'], 'remain3'] = initial_cash
                else:
                    df.loc[df['datetime'] == df.iloc[i]['datetime'], 'remain3'] = df.iloc[i - 1]['remain3']
            elif self.chicang_num_kong[2] != 0:  # 持空仓
                if df.iloc[i]['close'] > open:  # 大于开盘价止损(平空)
                    # 平空
                    initial_cash += dict_tradeunit[self.symbol] * df.iloc[i]['close'] * dict_marginratio[self.symbol] * \
                                    self.chicang_num_kong[2]
                    profitandloss = 0
                    for ii in chengjiao_dict:
                        if ii['类型'] == '卖开' and ii['已平仓手数'] == 0:
                            profitandloss += (ii['成交量'] * (ii['成交价'] - df.iloc[i]['close']) * dict_tradeunit[
                                self.symbol])
                            ii['已平仓手数'] = ii['成交量']
                    tempt_dict = {'时间': df.iloc[i]['datetime'], '类型': '买平', '成交量': self.chicang_num_kong[2],
                                  '成交价': df.iloc[i]['close'], '平仓盈亏': round(profitandloss, 2)}
                    chengjiao_dict.append(tempt_dict)
                    self.chicang_num_kong[2] = 0
                    df.loc[df['datetime'] == df.iloc[i]['datetime'], 'remain3'] = initial_cash
                else:
                    df.loc[df['datetime'] == df.iloc[i]['datetime'], 'remain3'] = df.iloc[i - 1]['remain3']
            else:  # 没有持仓
                if df.iloc[i]['close'] > high:
                    # 买多
                    initial_cash -= dict_tradeunit[self.symbol] * df.iloc[i]['close'] * dict_marginratio[self.symbol]
                    tempt_dict = {'时间': df.iloc[i]['datetime'], '类型': '买开', '成交量': 1,
                                  '成交价': df.iloc[i]['close'], '平仓盈亏': '-', '已平仓手数': 0}
                    chengjiao_dict.append(tempt_dict)
                    self.chicang_num_duo[2] += 1
                    df.loc[df['datetime'] == df.iloc[i]['datetime'], 'remain3'] = initial_cash
                elif df.iloc[i]['close'] < low:
                    # 买空
                    initial_cash -= dict_tradeunit[self.symbol] * df.iloc[i]['close'] * dict_marginratio[self.symbol]
                    tempt_dict = {'时间': df.iloc[i]['datetime'], '类型': '卖开', '成交量': 1,
                                  '成交价': df.iloc[i]['close'], '平仓盈亏': '-', '已平仓手数': 0}
                    chengjiao_dict.append(tempt_dict)
                    self.chicang_num_kong[2] += 1
                    df.loc[df['datetime'] == df.iloc[i]['datetime'], 'remain3'] = initial_cash
                else:
                    df.loc[df['datetime'] == df.iloc[i]['datetime'], 'remain3'] = df.iloc[i - 1]['remain3']
            df.loc[df['datetime'] == df.iloc[i]['datetime'], 'position3'] = df.iloc[i]['close'] * dict_tradeunit[
                self.symbol] * dict_marginratio[self.symbol] * (self.chicang_num_duo[2] + self.chicang_num_kong[
                2])
        # 最后一分钟平仓
        if self.chicang_num_duo[2] != 0:
            # 平多
            initial_cash += dict_tradeunit[self.symbol] * df.iloc[-1]['close'] * dict_marginratio[self.symbol] * \
                            self.chicang_num_duo[2]
            profitandloss = 0
            for ii in chengjiao_dict:
                if ii['类型'] == '买开' and ii['已平仓手数'] == 0:
                    profitandloss += (ii['成交量'] * (df.iloc[-1]['close'] - ii['成交价']) * dict_tradeunit[
                        self.symbol])
                    ii['已平仓手数'] = ii['成交量']
            tempt_dict = {'时间': df.iloc[-1]['datetime'], '类型': '卖平', '成交量': self.chicang_num_duo[2],
                          '成交价': df.iloc[-1]['close'], '平仓盈亏': round(profitandloss, 2)}
            chengjiao_dict.append(tempt_dict)
            self.chicang_num_duo[2] = 0
            df.loc[df['datetime'] == df.iloc[-1]['datetime'], 'position3'] = df.iloc[-1]['close'] * dict_tradeunit[
                self.symbol] * dict_marginratio[self.symbol] * (self.chicang_num_duo[2] + self.chicang_num_kong[
                2])
            df.loc[df['datetime'] == df.iloc[-1]['datetime'], 'remain3'] = initial_cash
        if self.chicang_num_kong[2] != 0:
            # 平空
            initial_cash += dict_tradeunit[self.symbol] * df.iloc[-1]['close'] * dict_marginratio[self.symbol] * \
                            self.chicang_num_kong[2]
            profitandloss = 0
            for ii in chengjiao_dict:
                if ii['类型'] == '卖开' and ii['已平仓手数'] == 0:
                    profitandloss += (ii['成交量'] * (ii['成交价'] - df.iloc[-1]['close']) * dict_tradeunit[
                        self.symbol])
                    ii['已平仓手数'] = ii['成交量']
            tempt_dict = {'时间': df.iloc[-1]['datetime'], '类型': '买平', '成交量': self.chicang_num_kong[2],
                          '成交价': df.iloc[-1]['close'], '平仓盈亏': round(profitandloss, 2)}
            chengjiao_dict.append(tempt_dict)
            self.chicang_num_kong[2] = 0
            df.loc[df['datetime'] == df.iloc[-1]['datetime'], 'position3'] = df.iloc[-1]['close'] * dict_tradeunit[
                self.symbol] * dict_marginratio[self.symbol] * (self.chicang_num_duo[2] + self.chicang_num_kong[
                2])
            df.loc[df['datetime'] == df.iloc[-1]['datetime'], 'remain3'] = initial_cash
        shoushu = 0
        yingkui = 0
        for i in chengjiao_dict:
            self.tree.insert(self.list_tree[2], END, values=(
                i['时间'], i['类型'], i['成交量'], i['成交价'], i['平仓盈亏']))
            shoushu += i['成交量']
            if i['平仓盈亏'] != '-':
                yingkui += float(i['平仓盈亏'])
        self.tree.insert(self.list_tree[2], END, values=('总计', '', shoushu, '', round(yingkui, 2)), tags='tag_sum')
        self.tree.insert(self.list_tree[2], END, values=('', '', '', '', '', ''))
        df['total_value3'] = df['position3'] + df['remain3']

        # 2.Dual Thrust策略
        # 定义一个区间，区间的上界和下界分别为支撑线和阻力线。
        # 当价格超过上界时，如果持有空仓，先平再开多；如果没有仓位，直接开多。
        # 当价格跌破下界时，如果持有多仓，先平再开空；如果没有仓位，直接开空。
        initial_cash = 30000
        chengjiao_dict = []
        df['position2'] = 0
        df['remain2'] = 30000
        # 设置参数，一般根据自己经验以及回测结果进行优化
        k1 = 0.2
        k2 = 0.2
        HH = df['high'].max()  # 计算Dual Thrust 的上下轨
        HC = df['close'].max()
        LC = df['close'].max()
        LL = df['low'].min()
        p_range = max(HH - LC, HC - LL)
        current_open = df['open'].iloc[-1]  # 获取当天的开盘价
        df.drop(df.tail(1).index, inplace=True)  # 去掉当天的实时数据
        buy_line = current_open + p_range * k1  # 上轨
        sell_line = current_open - p_range * k2  # 下轨
        # 交易逻辑
        for i in range(len(df)):
            # 如果超过range的上界
            if df.iloc[i]['close'] > buy_line:
                if self.chicang_num_duo[1] != 0:  # 已经持有多仓，直接返回
                    continue
                elif self.chicang_num_kong[1] != 0:  # 已经持有空仓，平空再做多
                    # 平空
                    initial_cash += dict_tradeunit[self.symbol] * df.iloc[i]['close'] * dict_marginratio[self.symbol] * \
                                    self.chicang_num_kong[1]
                    profitandloss = 0
                    for ii in chengjiao_dict:
                        if ii['类型'] == '卖开' and ii['已平仓手数'] == 0:
                            profitandloss += (ii['成交量'] * (ii['成交价'] - df.iloc[i]['close']) * dict_tradeunit[
                                self.symbol])
                            ii['已平仓手数'] = ii['成交量']
                    tempt_dict = {'时间': df.iloc[i]['datetime'], '类型': '买平', '成交量': self.chicang_num_kong[1],
                                  '成交价': df.iloc[i]['close'], '平仓盈亏': round(profitandloss, 2)}
                    chengjiao_dict.append(tempt_dict)
                    self.chicang_num_kong[1] = 0
                    # 买多
                    initial_cash -= dict_tradeunit[self.symbol] * df.iloc[i]['close'] * dict_marginratio[self.symbol]
                    tempt_dict = {'时间': df.iloc[i]['datetime'], '类型': '买开', '成交量': 1,
                                  '成交价': df.iloc[i]['close'], '平仓盈亏': '-', '已平仓手数': 0}
                    chengjiao_dict.append(tempt_dict)
                    self.chicang_num_duo[1] += 1
                else:  # 没有持仓时，市价开多
                    initial_cash -= dict_tradeunit[self.symbol] * df.iloc[i]['close'] * dict_marginratio[self.symbol]
                    tempt_dict = {'时间': df.iloc[i]['datetime'], '类型': '买开', '成交量': 1,
                                  '成交价': df.iloc[i]['close'], '平仓盈亏': '-', '已平仓手数': 0}
                    chengjiao_dict.append(tempt_dict)
                    self.chicang_num_duo[1] += 1
                df.loc[df['datetime'] == df.iloc[i]['datetime'], 'remain2'] = initial_cash
            # 如果低于range的下界
            elif df.iloc[i]['close'] < sell_line:
                if self.chicang_num_kong[1] != 0:  # 已经持有空仓，直接返回
                    continue
                elif self.chicang_num_duo[1] != 0:  # 已经持有多仓，平多再做空
                    # 平多
                    initial_cash += dict_tradeunit[self.symbol] * df.iloc[i]['close'] * dict_marginratio[self.symbol] * \
                                    self.chicang_num_duo[1]
                    profitandloss = 0
                    for ii in chengjiao_dict:
                        if ii['类型'] == '买开' and ii['已平仓手数'] == 0:
                            profitandloss += (ii['成交量'] * (df.iloc[i]['close'] - ii['成交价']) * dict_tradeunit[
                                self.symbol])
                            ii['已平仓手数'] = ii['成交量']
                    tempt_dict = {'时间': df.iloc[i]['datetime'], '类型': '卖平', '成交量': self.chicang_num_duo[1],
                                  '成交价': df.iloc[i]['close'], '平仓盈亏': round(profitandloss, 2)}
                    chengjiao_dict.append(tempt_dict)
                    self.chicang_num_duo[1] = 0
                    # 买空
                    initial_cash -= dict_tradeunit[self.symbol] * df.iloc[i]['close'] * dict_marginratio[self.symbol]
                    tempt_dict = {'时间': df.iloc[i]['datetime'], '类型': '卖开', '成交量': 1,
                                  '成交价': df.iloc[i]['close'], '平仓盈亏': '-', '已平仓手数': 0}
                    chengjiao_dict.append(tempt_dict)
                    self.chicang_num_kong[1] += 1
                else:  # 没有持仓时，市价开空
                    initial_cash -= dict_tradeunit[self.symbol] * df.iloc[i]['close'] * dict_marginratio[self.symbol]
                    tempt_dict = {'时间': df.iloc[i]['datetime'], '类型': '卖开', '成交量': 1,
                                  '成交价': df.iloc[i]['close'], '平仓盈亏': '-', '已平仓手数': 0}
                    chengjiao_dict.append(tempt_dict)
                    self.chicang_num_kong[1] += 1
                df.loc[df['datetime'] == df.iloc[i]['datetime'], 'remain2'] = initial_cash
            else:
                df.loc[df['datetime'] == df.iloc[i]['datetime'], 'remain2'] = df.iloc[i - 1]['remain2']
            df.loc[df['datetime'] == df.iloc[i]['datetime'], 'position2'] = df.iloc[i]['close'] * dict_tradeunit[
                self.symbol] * dict_marginratio[self.symbol] * (self.chicang_num_duo[1] + self.chicang_num_kong[
                1])
        shoushu = 0
        yingkui = 0
        for i in chengjiao_dict:
            self.tree.insert(self.list_tree[1], END, values=(
                i['时间'], i['类型'], i['成交量'], i['成交价'], i['平仓盈亏']))
            shoushu += i['成交量']
            if i['平仓盈亏'] != '-':
                yingkui += float(i['平仓盈亏'])
        self.tree.insert(self.list_tree[1], END, values=('总计', '', shoushu, '', round(yingkui, 2)), tags='tag_sum')
        self.tree.insert(self.list_tree[1], END, values=('', '', '', '', '', ''))
        df['total_value2'] = df['position2'] + df['remain2']
        # 画图
        self.plot_df = df.copy()
        self.plot_graph(self.plot_df, fig, canvas)

    def plot_graph(self, df, fig, canvas):
        # 清除画布
        fig.clf()
        canvas.draw()
        # 作图
        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # 显示中文标签,处理中文乱码问题
        plt.title('总资产')
        plt.plot(df['total_value1'], label='双均线', color='tomato')
        if self.var1.get() == True:
            plt.plot(df['total_value2'], label='Dual thrust', color='darkseagreen')
        plt.plot(df['total_value3'], label='菲阿里四价', color='slateblue')
        plt.xticks([])
        plt.xlabel('时间')
        plt.legend(loc='upper left')
        canvas.draw()
