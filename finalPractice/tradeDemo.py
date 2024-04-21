import datetime
import tkinter  # 图形界面库
import threading
from tkinter import ttk
from tkinter import *
from tkinter import messagebox
from tkinter.messagebox import showerror, showinfo
from tkinter.simpledialog import askinteger
from tkinter.ttk import Separator

import pandas as pd
import tushare as ts  # 量化分析数据库
import os  # 用于文件操作
import json  # 用于保存导出我们记录的操作
import re

from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot
from PyQt5.QtWidgets import QMessageBox

TOTAL_ASSETS = 1000000  # 个人资产
PATH_BAK = 'myfile.json'

data_all = []
tmplist = []
codelist = ['RB888', 'RB99', 'SA99', 'SA888', 'jm888', 'jm99']  # 存储期货代码
codename = ['螺纹钢指数', '螺纹钢主连', '纯碱主连', '纯碱指数', '焦煤指数', '焦煤主连']
dict_codename = {'RB888': '螺纹钢指数', 'RB99': '螺纹钢主连', 'SA99': '纯碱主连', 'SA888': '纯碱指数',
                 'jm888': '焦煤指数', 'jm99': '焦煤主连'}
dict_tradeunit = {'RB888': 10, 'RB99': 10, 'SA99': 20, 'SA888': 20, 'jm888': 60, 'jm99': 60}
dict_marginratio = {'RB888': 0.07, 'RB99': 0.07, 'SA99': 0.12, 'SA888': 0.12, 'jm888': 0.2, 'jm99': 0.2}

remain = TOTAL_ASSETS  # 剩余资产
columns1 = ("成交时间", "合约代码", "合约名称", "类型", "成交量", "成交价", "平仓盈亏")  # 成交记录
columns2 = ("合约代码", "合约名称", "类型", "总仓", "开仓均价", "逐笔盈亏")  # 持仓记录


# self.old_dict:记录所有成交记录
# self.old_dict2:记录计算而得的持仓数据
class tradeDemo(QObject):
    signal1 = pyqtSignal(dict)  # 交易点
    signal2 = pyqtSignal(str, dict, dict)  # 双击持仓记录，显示持仓记录
    # signal3 = pyqtSignal(str, dict, dict)  # 双击成交记录，显示持仓记录
    signal_symbol = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def set_data(self, symbol, df):
        self.symbol = symbol  # 当前选择的symbol
        self.df = df  # columns=['symbol', 'datetime', 'close']每一个合约的最新价

        self.gui = tkinter.Tk()
        self.gui.title('模拟交易界面')
        self.gui.geometry('1500x820')

        frame1 = tkinter.LabelFrame(self.gui, text="市场情况", width=750, height=350)
        frame1.place(x=0, y=0)
        frame2 = tkinter.LabelFrame(self.gui, text="账户分析", width=750, height=350)
        frame2.place(x=750, y=0)
        frame3 = tkinter.LabelFrame(self.gui, text="交易记录", width=1500, height=400)
        frame3.place(x=0, y=350)

        ## 市场情况框架中的控件
        # 1.合约
        l1_symbol = tkinter.Label(frame1, text='合约代码:')
        l1_symbol.place(x=10, y=5)
        self.combo_box = ttk.Combobox(frame1, values=codelist, width=8)
        self.combo_box.pack()
        self.combo_box.current(codelist.index(self.symbol))  # 将当前symbol设置为默认选项
        self.combo_box.bind("<<ComboboxSelected>>", self.change_symbol)
        self.combo_box.place(x=110, y=5)
        # self.s11 = tkinter.StringVar()
        # self.s11.set(str(self.symbol))
        # l1 = tkinter.Label(frame1, textvariable=self.s11, width=10, height=1, bg='white', anchor='w',
        #                    font=("Courier", 11, "italic"))
        # l1.place(x=70, y=5)
        # 2.交易品种
        l2_kind = tkinter.Label(frame1, text='交易品种:')
        l2_kind.place(x=255, y=5)
        self.s12 = tkinter.StringVar()
        self.s12.set(dict_codename[self.symbol])
        l2 = tkinter.Label(frame1, textvariable=self.s12, width=10, height=1, bg='white', anchor='w',
                           font=("Courier", 11, "italic"))
        l2.place(x=335, y=5)
        # 3.交易单位
        l3_unit = tkinter.Label(frame1, text='交易单位:')
        l3_unit.place(x=510, y=5)
        self.s13 = tkinter.StringVar()
        self.s13.set(str(dict_tradeunit[self.symbol]) + " 吨/手")
        l3 = tkinter.Label(frame1, textvariable=self.s13, width=8, height=1, bg='white', anchor='w',
                           font=("Courier", 11, "italic"))
        l3.place(x=620, y=5)
        # 4.交易保证金比例
        l4_ratio = tkinter.Label(frame1, text='保证金比例:')
        l4_ratio.place(x=10, y=50)
        self.s14 = tkinter.StringVar()
        self.s14.set(str(int(dict_marginratio[self.symbol] * 100)) + " %")
        l4 = tkinter.Label(frame1, textvariable=self.s14, width=8, height=1, bg='white', anchor='w',
                           font=("Courier", 11, "italic"))
        l4.place(x=110, y=50)
        # 5.现价
        l5_currentPrice = tkinter.Label(frame1, text='现价:')
        l5_currentPrice.place(x=255, y=50)
        self.s15 = tkinter.StringVar()
        # str_series = self.df.loc[self.df['symbol'] == self.symbol, 'close'].to_string()
        # str_without_index = re.sub(r'\n.*\n', '\n', str_series)
        # print(df)
        # print(str_series)
        # print(str_without_index)
        # self.s13.set(str_without_index)
        s_str = self.df.loc[self.df['symbol'] == self.symbol, 'close'].astype(str)
        s_values = s_str.values
        self.s15.set(s_values[0])
        l5 = tkinter.Label(frame1, textvariable=self.s15, width=10, height=1, bg='white', anchor='w',
                           font=("Courier", 11, "italic"))
        l5.place(x=335, y=50)
        # 6.1手保证金约：
        l6_1shouprice = tkinter.Label(frame1, text='1手保证金约:')
        l6_1shouprice.place(x=510, y=50)
        self.s16 = tkinter.StringVar()
        s_str = self.df.loc[self.df['symbol'] == self.symbol, 'close'].astype(str)
        s_values = s_str.values
        self.s16.set(
            str(round(dict_tradeunit[self.symbol] * float(s_values[0]) * dict_marginratio[self.symbol])) + ' 元')
        l6 = tkinter.Label(frame1, textvariable=self.s16, width=8, height=1, bg='white', anchor='w',
                           font=("Courier", 11, "italic"))
        l6.place(x=620, y=50)
        # 7.买多
        b_duo = tkinter.Button(frame1, text='买多', width=10, height=1, bg='white', fg='red',
                               command=self.execOpduo)
        b_duo.place(x=40, y=100)
        # 8.卖空
        b_kong = tkinter.Button(frame1, text='卖空', width=10, height=1, bg='white', fg='green',
                                command=self.execOpkong)
        b_kong.place(x=290, y=100)
        # 9.平仓
        b_ping = tkinter.Button(frame1, text='平仓', width=10, height=1, bg='white', fg='blue',
                                command=self.execOpping)
        b_ping.place(x=540, y=100)

        ## 账户分析框架中的控件
        # 1.总资产
        l2_t = tkinter.Label(frame2, text='总资产:')
        l2_t.place(x=10, y=5)
        self.s2 = tkinter.StringVar()
        self.s2.set(str(TOTAL_ASSETS))
        l2 = tkinter.Label(frame2, textvariable=self.s2, width=10, height=1, bg='white', anchor='w',
                           font=("Courier", 11, "italic"))
        l2.place(x=80, y=5)
        # 2.总市值
        l5_t = tkinter.Label(frame2, text='总市值:')
        l5_t.place(x=260, y=5)
        self.s5 = tkinter.StringVar()
        l5 = tkinter.Label(frame2, textvariable=self.s5, width=10, height=1, bg='white', anchor='w',
                           font=("Courier", 11, "italic"))
        l5.place(x=340, y=5)
        # 3.剩余可用
        l4_t = tkinter.Label(frame2, text='剩余可用:')
        l4_t.place(x=510, y=5)
        self.s4 = tkinter.StringVar()
        l4 = tkinter.Label(frame2, textvariable=self.s4, width=10, height=1, bg='white', anchor='w',
                           font=("Courier", 11, "italic"))
        l4.place(x=600, y=5)
        # 4.总盈亏
        l3_t = tkinter.Label(frame2, text='总盈亏:')
        l3_t.place(x=10, y=53)
        self.s3 = tkinter.StringVar()
        l3 = tkinter.Label(frame2, textvariable=self.s3, width=10, height=1, bg='white', anchor='w',
                           font=("Courier", 11, "italic"))
        l3.place(x=80, y=50)
        # 5.持仓盈亏
        l6_t = tkinter.Label(frame2, text='持仓盈亏:')
        l6_t.place(x=260, y=53)
        self.s6 = tkinter.StringVar()
        l6 = tkinter.Label(frame2, textvariable=self.s6, width=10, height=1, bg='white', anchor='w',
                           font=("Courier", 11, "italic"))
        l6.place(x=350, y=50)
        # 6.资金使用率
        l7_t = tkinter.Label(frame2, text='资金使用率:')
        l7_t.place(x=510, y=53)
        self.s7 = tkinter.StringVar()
        l7 = tkinter.Label(frame2, textvariable=self.s7, width=8, height=1, bg='white', anchor='w',
                           font=("Courier", 11, "italic"))
        l7.place(x=620, y=50)
        # 7.账户分析
        b_analyze = tkinter.Button(frame2, text='账户分析', width=10, height=1, command=self.execOpanalyze)
        b_analyze.place(x=10, y=100)

        ## 交易记录框架中
        self.notebook = ttk.Notebook(frame3, width=1500, height=400)
        frame3_1 = tkinter.Frame(frame3, width=1500, height=400)  # 放成交记录
        frame3_2 = tkinter.Frame(frame3, width=1500, height=400)  # 放持仓记录
        frame3_1.place(x=0, y=0)
        frame3_2.place(x=0, y=0)
        frame3_1_query = tkinter.Frame(frame3_1, width=1500, height=50)  # 放成交记录的查询条件
        frame3_1_tree = tkinter.Frame(frame3_1, width=1500, height=300)  # 放成交记录的表格
        frame3_1_query.place(x=0, y=0)
        frame3_1_tree.place(x=0, y=50)
        frame3_2_query = tkinter.Frame(frame3_2, width=1500, height=50)  # 放持仓记录的查询条件
        frame3_2_tree = tkinter.Frame(frame3_2, width=1500, height=300)  # 放持仓记录的表格
        frame3_2_query.place(x=0, y=0)
        frame3_2_tree.place(x=0, y=50)

        # 滚动条
        scrollbar_1_y = Scrollbar(frame3_1_tree, orient=VERTICAL)
        scrollbar_2_y = Scrollbar(frame3_2_tree, orient=VERTICAL)

        # frame3_1_query:成交历史的筛选条件
        # 1.时间
        l1_time1 = tkinter.Label(frame3_1_query, text='成交时间:')
        l1_time1.place(x=5, y=5)
        self.entry_time1 = tkinter.Entry(frame3_1_query, font=("宋体", 10), width=20)
        self.entry_time1.insert(0, "2023-03-10")
        self.entry_time1.place(x=95, y=7)
        # 2.合约代码
        l2_symbol_query1 = tkinter.Label(frame3_1_query, text='合约代码:')
        l2_symbol_query1.place(x=330, y=5)
        self.combo_box_querysymbol1 = ttk.Combobox(frame3_1_query, values=codelist, width=8)
        self.combo_box_querysymbol1.pack()
        self.combo_box_querysymbol1.place(x=420, y=5)
        # 3.类型
        l3_kind_query1 = tkinter.Label(frame3_1_query, text='类型:')
        l3_kind_query1.place(x=575, y=5)
        self.combo_box_querykind1 = ttk.Combobox(frame3_1_query, values=['买开', '卖开', '卖平', '买平'], width=8)
        self.combo_box_querykind1.pack()
        self.combo_box_querykind1.place(x=630, y=5)
        # 4.确认查询&显示全部
        b_query1 = tkinter.Button(frame3_1_query, text='查询', width=10, height=1, command=self.yesquery1)
        b_query1.place(x=1000, y=5)
        b_displayall1 = tkinter.Button(frame3_1_query, text='显示全部', width=10, height=1, command=self.yesall1)
        b_displayall1.place(x=1150, y=5)

        # frame3_1_tree:成交历史的表格
        # columns1 = ("成交时间", "合约代码", "合约名称", "类型", "成交量", "成交价", "平仓盈亏")
        self.tree = ttk.Treeview(frame3_1_tree, height=15, show="headings", columns=columns1,
                                 yscrollcommand=scrollbar_1_y.set)
        self.tree.column("成交时间", width=250, anchor='center')  # 表示列,不显示
        self.tree.column("合约代码", width=200, anchor='center')
        self.tree.column("合约名称", width=200, anchor='center')
        self.tree.column("类型", width=200, anchor='center')
        self.tree.column("成交量", width=200, anchor='center')
        self.tree.column("成交价", width=200, anchor='center')
        self.tree.column("平仓盈亏", width=200, anchor='center')

        self.tree.heading("成交时间", text="成交时间")  # 显示表头
        self.tree.heading("合约代码", text="合约代码")
        self.tree.heading("合约名称", text="合约名称")
        self.tree.heading("类型", text="类型")
        self.tree.heading("成交量", text="成交量")
        self.tree.heading("成交价", text="成交价")
        self.tree.heading("平仓盈亏", text="平仓盈亏")
        self.tree.bind('<Double-1>', self.treeviewClick1)
        # self.tree.place(x=0, y=0)
        scrollbar_1_y.config(command=self.tree.yview)
        scrollbar_1_y.pack(side=RIGHT, fill=Y)
        self.tree.pack(fill=BOTH, expand=True)

        # frame3_2_query:持仓记录的筛选条件
        # 1.合约代码
        l1_symbol_query2 = tkinter.Label(frame3_2_query, text='合约代码:')
        l1_symbol_query2.place(x=5, y=5)
        self.combo_box_querysymbol2 = ttk.Combobox(frame3_2_query, values=codelist, width=8)
        self.combo_box_querysymbol2.pack()
        self.combo_box_querysymbol2.place(x=95, y=5)
        # 3.类型
        l2_kind_query2 = tkinter.Label(frame3_2_query, text='类型:')
        l2_kind_query2.place(x=250, y=5)
        self.combo_box_querykind2 = ttk.Combobox(frame3_2_query, values=['多', '空'], width=8)
        self.combo_box_querykind2.pack()
        self.combo_box_querykind2.place(x=305, y=5)
        # 4.确认查询&显示全部
        b_query2 = tkinter.Button(frame3_2_query, text='查询', width=10, height=1, command=self.yesquery2)
        b_query2.place(x=1000, y=5)
        b_displayall1 = tkinter.Button(frame3_2_query, text='显示全部', width=10, height=1, command=self.yesall2)
        b_displayall1.place(x=1150, y=5)

        # frame3_2_tree:持仓记录的表格
        # columns2 = ("合约代码", "合约名称", "类型", "总仓", "开仓均价", "逐笔盈亏")  # 持仓记录
        self.tree2 = ttk.Treeview(frame3_2_tree, height=18, show="headings", columns=columns2,
                                  yscrollcommand=scrollbar_2_y.set)
        self.tree2.column("合约代码", width=200, anchor='center')  # 表示列,不显示
        self.tree2.column("合约名称", width=200, anchor='center')
        self.tree2.column("类型", width=200, anchor='center')
        self.tree2.column("总仓", width=200, anchor='center')
        self.tree2.column("开仓均价", width=200, anchor='center')
        self.tree2.column("逐笔盈亏", width=200, anchor='center')

        self.tree2.heading("合约代码", text="合约代码")  # 显示表头
        self.tree2.heading("合约名称", text="合约名称")
        self.tree2.heading("类型", text="类型")
        self.tree2.heading("总仓", text="总仓")
        self.tree2.heading("开仓均价", text="开仓均价")
        self.tree2.heading("逐笔盈亏", text="逐笔盈亏")
        self.tree2.bind('<Double-1>', self.treeviewClick2)
        # self.tree2.place(x=0, y=0)
        scrollbar_2_y.config(command=self.tree2.yview)
        scrollbar_2_y.pack(side=RIGHT, fill=Y)
        self.tree2.pack(fill=BOTH, expand=True)

        self.notebook.add(frame3_1, text="   成交   ")
        self.notebook.add(frame3_2, text="   持仓   ")
        self.notebook.pack(fill=BOTH, expand=True)

        # 我的持仓初始化
        global mylist
        self.initMyList()
        global data_all
        self.getCurrentData()
        self.gui.mainloop()

    # 我的持仓初始化，获取remain、self.old_dict
    def initMyList(self):
        global remain
        self.old_dict = []
        with open(PATH_BAK, 'r', encoding='utf-8') as f:
            filetmp = f.read()
            if filetmp:
                self.old_dict = json.loads(filetmp)
                for i in self.old_dict:
                    remain = i['remain']
                    break
            else:
                remain = TOTAL_ASSETS

    # 买多
    def execOpduo(self):
        s_str = self.df.loc[self.df['symbol'] == self.symbol].astype(str)
        s_values = s_str.values
        currentprice = float(s_values[0][2])
        pershouprice = dict_tradeunit[self.symbol] * currentprice * dict_marginratio[self.symbol]
        max = remain // int(pershouprice)  # 交易手数的上限

        # 新的弹窗
        new_window = tkinter.Toplevel(self.gui)
        new_window.geometry("350x350")
        new_window.title("买多确认")
        # 1.标题
        label_duo = tkinter.Label(new_window, text='委托买多确认', font=("微软雅黑", 14))
        label_duo.place(x=90, y=10)
        # 2.具体内容
        label_symbol = tkinter.Label(new_window, text='合约: ', font=("宋体", 10), fg="dimgray")
        label_symbol.place(x=10, y=70)
        content_symbol = tkinter.StringVar()
        content_symbol.set(self.symbol)
        l1 = tkinter.Label(new_window, textvariable=content_symbol, anchor='w', font=("宋体", 10))
        l1.place(x=80, y=70)

        label_kind = tkinter.Label(new_window, text='类型: ', font=("宋体", 10), foreground="dimgray")
        label_kind.place(x=10, y=100)
        content_kind = tkinter.StringVar()
        content_kind.set("开多仓")
        l2 = tkinter.Label(new_window, textvariable=content_kind, anchor='w', font=("宋体", 10), fg="red")
        l2.place(x=80, y=100)

        label_price = tkinter.Label(new_window, text='价格: ', font=("宋体", 10), foreground="dimgray")
        label_price.place(x=10, y=130)
        content_price = tkinter.StringVar()
        content_price.set(currentprice)
        l3 = tkinter.Label(new_window, textvariable=content_price, anchor='w', font=("宋体", 10))
        l3.place(x=80, y=130)

        label_max = tkinter.Label(new_window, text='最多可开仓: ', font=("宋体", 10), foreground="dimgray")
        label_max.place(x=10, y=160)
        content_max = tkinter.StringVar()
        content_max.set(str(max) + " 手")
        l4 = tkinter.Label(new_window, textvariable=content_max, anchor='w', font=("宋体", 10))
        l4.place(x=130, y=160)

        label_shoushu = tkinter.Label(new_window, text='手数: ', font=("宋体", 10), foreground="dimgray")
        label_shoushu.place(x=10, y=190)
        self.entry_shoushu = tkinter.Entry(new_window, font=("宋体", 10), width=8)
        self.entry_shoushu.insert(0, 1)
        self.res = self.entry_shoushu.get()
        self.entry_shoushu.place(x=80, y=190)

        label_question = tkinter.Label(new_window, text='确认提交以上委托？', font=("宋体", 8), foreground="dimgray")
        label_question.place(x=10, y=240)

        # 3.确认取消按钮
        b_yes = tkinter.Button(new_window, text='确认买多', width=10, height=1, bg='blue', fg='white',
                               command=lambda: self.yesduo(new_window))
        b_yes.place(x=10, y=290)
        b_no = tkinter.Button(new_window, text='取消', width=10, height=1, bg='lightgrey', fg='black',
                              command=lambda: self.noduo(new_window))
        b_no.place(x=220, y=290)

        new_window.mainloop()

    def yesduo(self, window):
        global remain
        self.res = self.entry_shoushu.get()
        s_str = self.df.loc[self.df['symbol'] == self.symbol].astype(str)
        s_values = s_str.values
        currentprice = float(s_values[0][2])
        pershouprice = dict_tradeunit[self.symbol] * currentprice * dict_marginratio[self.symbol]
        max = remain // int(pershouprice)  # 交易手数的上限
        if int(self.res) > max:
            print(showerror(title="警告", message="超过可交易手数上限。"))
        else:
            remain = remain - int(self.res) * int(pershouprice)
            # columns1 = ("成交时间", "合约代码", "合约名称", "类型", "成交量", "成交价")
            dict = {'remain': remain, '成交时间': s_values[0][1], '合约代码': self.symbol,
                    '合约名称': dict_codename[self.symbol], '类型': "买开", '成交量': int(self.res),
                    '成交价': currentprice, '平仓盈亏': '-', '已平仓手数': 0}
            self.old_dict.append(dict)
            with open(PATH_BAK, 'w', encoding='utf-8') as f:  # 执行买入成功更新本地文件
                f.write(json.dumps(self.old_dict, ensure_ascii=False))
            self.getCurrentData()
            print(showinfo(title="提示",
                           message=dict['合约名称'] + self.symbol + ' ' + dict['类型'] + ' ' + str(
                               dict['成交量']) + "手。"))
            # 每次开多或者开空都向主页传参，显示交易点
            self.signal1.emit(dict)  # 发射信号
            window.destroy()

    def noduo(self, window):
        window.destroy()

    # 卖空
    def execOpkong(self):
        s_str = self.df.loc[self.df['symbol'] == self.symbol].astype(str)
        s_values = s_str.values
        currentprice = float(s_values[0][2])
        pershouprice = dict_tradeunit[self.symbol] * currentprice * dict_marginratio[self.symbol]
        max = remain // int(pershouprice)  # 交易手数的上限

        # 新的弹窗
        new_window = tkinter.Toplevel(self.gui)
        new_window.geometry("350x350")
        new_window.title("卖空确认")
        # 1.标题
        label_duo = tkinter.Label(new_window, text='委托卖空确认', font=("微软雅黑", 14))
        label_duo.place(x=90, y=10)
        # 2.具体内容
        label_symbol = tkinter.Label(new_window, text='合约: ', font=("宋体", 10), fg="dimgray")
        label_symbol.place(x=10, y=70)
        content_symbol = tkinter.StringVar()
        content_symbol.set(self.symbol)
        l1 = tkinter.Label(new_window, textvariable=content_symbol, anchor='w', font=("宋体", 10))
        l1.place(x=80, y=70)

        label_kind = tkinter.Label(new_window, text='类型: ', font=("宋体", 10), foreground="dimgray")
        label_kind.place(x=10, y=100)
        content_kind = tkinter.StringVar()
        content_kind.set("开空仓")
        l2 = tkinter.Label(new_window, textvariable=content_kind, anchor='w', font=("宋体", 10), fg="green")
        l2.place(x=80, y=100)

        label_price = tkinter.Label(new_window, text='价格: ', font=("宋体", 10), foreground="dimgray")
        label_price.place(x=10, y=130)
        content_price = tkinter.StringVar()
        content_price.set(currentprice)
        l3 = tkinter.Label(new_window, textvariable=content_price, anchor='w', font=("宋体", 10))
        l3.place(x=80, y=130)

        label_max = tkinter.Label(new_window, text='最多可开仓: ', font=("宋体", 10), foreground="dimgray")
        label_max.place(x=10, y=160)
        content_max = tkinter.StringVar()
        content_max.set(str(max) + " 手")
        l4 = tkinter.Label(new_window, textvariable=content_max, anchor='w', font=("宋体", 10))
        l4.place(x=130, y=160)

        label_shoushu = tkinter.Label(new_window, text='手数: ', font=("宋体", 10), foreground="dimgray")
        label_shoushu.place(x=10, y=190)
        self.entry_shoushu = tkinter.Entry(new_window, font=("宋体", 10), width=8)
        self.entry_shoushu.insert(0, 1)
        self.res = self.entry_shoushu.get()
        self.entry_shoushu.place(x=80, y=190)

        label_question = tkinter.Label(new_window, text='确认提交以上委托？', font=("宋体", 8), foreground="dimgray")
        label_question.place(x=10, y=240)

        # 3.确认取消按钮
        b_yes = tkinter.Button(new_window, text='确认卖空', width=10, height=1, bg='blue', fg='white',
                               command=lambda: self.yeskong(new_window))
        b_yes.place(x=10, y=290)
        b_no = tkinter.Button(new_window, text='取消', width=10, height=1, bg='lightgrey', fg='black',
                              command=lambda: self.nokong(new_window))
        b_no.place(x=220, y=290)

        new_window.mainloop()

    def yeskong(self, window):
        global remain
        self.res = self.entry_shoushu.get()
        s_str = self.df.loc[self.df['symbol'] == self.symbol].astype(str)
        s_values = s_str.values
        currentprice = float(s_values[0][2])
        pershouprice = dict_tradeunit[self.symbol] * currentprice * dict_marginratio[self.symbol]
        max = remain // int(pershouprice)  # 交易手数的上限
        if int(self.res) > max:
            print(showerror(title="警告", message="超过可交易手数上限。"))
        else:
            remain = remain - int(self.res) * int(pershouprice)
            # columns1 = ("成交时间", "合约代码", "合约名称", "类型", "成交量", "成交价")
            dict = {'remain': remain, '成交时间': s_values[0][1], '合约代码': self.symbol,
                    '合约名称': dict_codename[self.symbol], '类型': "卖开", '成交量': int(self.res),
                    '成交价': currentprice, '平仓盈亏': '-', '已平仓手数': 0}
            self.old_dict.append(dict)
            with open(PATH_BAK, 'w', encoding='utf-8') as f:  # 执行买入成功更新本地文件
                f.write(json.dumps(self.old_dict, ensure_ascii=False))
            self.getCurrentData()
            print(showinfo(title="提示",
                           message=dict['合约名称'] + self.symbol + ' ' + dict['类型'] + ' ' + str(
                               dict['成交量']) + "手。"))
            # 每次开多或者开空都向主页传参，显示交易点
            self.signal1.emit(dict)  # 发射信号
            window.destroy()

    def nokong(self, window):
        window.destroy()

    # 平仓
    def execOpping(self):
        s_str = self.df.loc[self.df['symbol'] == self.symbol].astype(str)
        s_values = s_str.values
        currentprice = float(s_values[0][2])
        pershouprice = dict_tradeunit[self.symbol] * currentprice * dict_marginratio[self.symbol]
        max = remain // int(pershouprice)  # 交易手数的上限

        # 新的弹窗
        new_window = tkinter.Toplevel(self.gui)
        new_window.geometry("500x400")
        new_window.title("平仓确认")
        # 1.标题
        label_duo = tkinter.Label(new_window, text=dict_codename[self.symbol] + self.symbol + " 平仓",
                                  font=("微软雅黑", 14))
        label_duo.place(x=100, y=10)
        # 2.具体内容
        # 计算最多可以平的仓数、盈亏
        num_duo = 0
        profitandloss_duo = 0
        num_kong = 0
        profitandloss_kong = 0
        for i in self.old_dict2:
            if i['合约代码'] == self.symbol:
                if i['类型'] == '多':
                    num_duo = i['总仓']
                    profitandloss_duo = i['逐笔盈亏']
                else:
                    num_kong = i['总仓']
                    profitandloss_kong = i['逐笔盈亏']
        # 创建两个画布分别放多空的平仓情况
        frame_duo = tkinter.Frame(new_window, width=500, height=180)
        frame_kong = tkinter.Frame(new_window, width=500, height=180)

        # frame_duo
        label_title = tkinter.Label(frame_duo, text='多单', font=("宋体", 10), fg="red")
        label_title.place(x=10, y=5)

        label_profitandloss = tkinter.Label(frame_duo, text='浮动盈亏: ', font=("宋体", 10), foreground="dimgray")
        label_profitandloss.place(x=10, y=35)
        content_profitandloss_duo = tkinter.StringVar()
        content_profitandloss_duo.set(str(round(profitandloss_duo, 2)))
        l1 = tkinter.Label(frame_duo, textvariable=content_profitandloss_duo, anchor='w', font=("宋体", 10))
        l1.place(x=100, y=35)

        label_currentprice = tkinter.Label(frame_duo, text='委托价格: ', font=("宋体", 10), foreground="dimgray")
        label_currentprice.place(x=10, y=65)
        content_currentprice = tkinter.StringVar()
        content_currentprice.set(round(currentprice, 2))
        l2 = tkinter.Label(frame_duo, textvariable=content_currentprice, anchor='w', font=("宋体", 10))
        l2.place(x=100, y=65)

        label_max = tkinter.Label(frame_duo, text='最多可卖平: ', font=("宋体", 10), foreground="dimgray")
        label_max.place(x=10, y=95)
        content_max = tkinter.StringVar()
        content_max.set(str(num_duo) + " 手")
        l3 = tkinter.Label(frame_duo, textvariable=content_max, anchor='w', font=("宋体", 10))
        l3.place(x=120, y=95)

        label_shoushu = tkinter.Label(frame_duo, text='手数: ', font=("宋体", 10), foreground="dimgray")
        label_shoushu.place(x=10, y=125)
        self.entry_pingduo = tkinter.Entry(frame_duo, font=("宋体", 10), width=8)
        self.entry_pingduo.insert(0, 1)
        self.res_pingduo = self.entry_pingduo.get()
        self.entry_pingduo.place(x=65, y=125)

        b_duo_yes = tkinter.Button(frame_duo, text='确认平多', width=8, height=1, bg='blue', fg='white',
                                   command=lambda: self.yespingduo(new_window, num_duo))
        b_duo_yes.place(x=200, y=65)
        b_duo_no = tkinter.Button(frame_duo, text='取消', width=8, height=1, bg='lightgrey', fg='black',
                                  command=lambda: self.nopingduo(new_window))
        b_duo_no.place(x=350, y=65)

        # frame_kong
        label_title_k = tkinter.Label(frame_kong, text='空单', font=("宋体", 10), fg="green")
        label_title_k.place(x=10, y=5)

        label_profitandloss_k = tkinter.Label(frame_kong, text='浮动盈亏: ', font=("宋体", 10), foreground="dimgray")
        label_profitandloss_k.place(x=10, y=35)
        content_profitandloss_kong = tkinter.StringVar()
        content_profitandloss_kong.set(str(round(profitandloss_kong, 2)))
        l1_k = tkinter.Label(frame_kong, textvariable=content_profitandloss_kong, anchor='w', font=("宋体", 10))
        l1_k.place(x=100, y=35)

        label_currentprice_k = tkinter.Label(frame_kong, text='委托价格: ', font=("宋体", 10), foreground="dimgray")
        label_currentprice_k.place(x=10, y=65)
        content_currentprice_k = tkinter.StringVar()
        content_currentprice_k.set(round(currentprice, 2))
        l2_k = tkinter.Label(frame_kong, textvariable=content_currentprice_k, anchor='w', font=("宋体", 10))
        l2_k.place(x=100, y=65)

        label_max_k = tkinter.Label(frame_kong, text='最多可买平: ', font=("宋体", 10), foreground="dimgray")
        label_max_k.place(x=10, y=95)
        content_max_k = tkinter.StringVar()
        content_max_k.set(str(num_kong) + " 手")
        l3_k = tkinter.Label(frame_kong, textvariable=content_max_k, anchor='w', font=("宋体", 10))
        l3_k.place(x=120, y=95)

        label_shoushu_k = tkinter.Label(frame_kong, text='手数: ', font=("宋体", 10), foreground="dimgray")
        label_shoushu_k.place(x=10, y=125)
        self.entry_pingkong = tkinter.Entry(frame_kong, font=("宋体", 10), width=8)
        self.entry_pingkong.insert(0, 1)
        self.res_pingkong = self.entry_pingkong.get()
        self.entry_pingkong.place(x=65, y=125)

        b_kong_yes = tkinter.Button(frame_kong, text='确认平空', width=8, height=1, bg='blue', fg='white',
                                    command=lambda: self.yespingkong(new_window, num_kong))
        b_kong_yes.place(x=200, y=65)
        b_kong_no = tkinter.Button(frame_kong, text='取消', width=8, height=1, bg='lightgrey', fg='black',
                                   command=lambda: self.nopingkong(new_window))
        b_kong_no.place(x=350, y=65)

        if num_duo != 0:
            if num_kong != 0:
                new_window.geometry("500x400")
                frame_duo.place(x=5, y=50)
                # sep1 = Separator(new_window, orient="horizontal")
                # sep1.pack(pady=210, fill='x')
                frame_kong.place(x=5, y=230)
            else:
                new_window.geometry("500x220")
                frame_duo.place(x=5, y=50)
        else:
            if num_kong != 0:
                new_window.geometry("500x220")
                frame_kong.place(x=5, y=50)
            else:
                print(showerror(title="警告", message="该合约无持仓可平。"))

        new_window.mainloop()

    # 要卖平
    def yespingduo(self, window, num_duo):
        global remain
        self.res_pingduo = self.entry_pingduo.get()
        s_str = self.df.loc[self.df['symbol'] == self.symbol].astype(str)
        s_values = s_str.values
        currentprice = float(s_values[0][2])
        pershouprice = dict_tradeunit[self.symbol] * currentprice * dict_marginratio[self.symbol]

        if int(self.res_pingduo) > num_duo:
            print(showerror(title="警告", message="超过可交易手数上限。"))
        else:
            remain = remain + int(self.res_pingduo) * int(pershouprice)
            tempt_dict = []  # 用于收集所有该symbol下的、还没有平仓完的买开成交记录
            profitandloss_duo = 0
            num_pingduo = int(self.res_pingduo)  # 需要平的手数
            for i in self.old_dict:
                if i['合约代码'] == self.symbol and i['类型'] == '买开' and i['已平仓手数'] != i['成交量']:
                    tempt_dict.append(i)
            for i in tempt_dict:
                if num_pingduo == 0:
                    break
                if i['成交量'] - i['已平仓手数'] <= num_pingduo:
                    num_pingduo -= (i['成交量'] - i['已平仓手数'])
                    # 更新self.old_dict、json数据
                    with open(PATH_BAK, 'r', encoding='utf-8') as f:
                        filetmp = f.read()
                        if filetmp:
                            for j in self.old_dict:
                                if j['合约代码'] == i['合约代码'] and j['类型'] == i['类型'] and j['成交时间'] == i[
                                    '成交时间'] and j['已平仓手数'] == i['已平仓手数']:
                                    profitandloss_duo += (i['成交量'] - i['已平仓手数']) * (
                                            currentprice - j['成交价']) * dict_tradeunit[j['合约代码']]
                                    j['已平仓手数'] = j['成交量']
                    with open(PATH_BAK, 'w', encoding='utf-8') as f:  # 执行买入成功更新本地文件
                        f.write(json.dumps(self.old_dict, ensure_ascii=False))
                else:
                    # 更新self.old_dict、json数据
                    with open(PATH_BAK, 'r', encoding='utf-8') as f:
                        filetmp = f.read()
                        if filetmp:
                            for j in self.old_dict:
                                if j['合约代码'] == i['合约代码'] and j['类型'] == i['类型'] and j['成交时间'] == i[
                                    '成交时间'] and j['已平仓手数'] == i['已平仓手数']:
                                    j['已平仓手数'] += num_pingduo
                                    profitandloss_duo += num_pingduo * (currentprice - j['成交价']) * dict_tradeunit[
                                        j['合约代码']]
                    with open(PATH_BAK, 'w', encoding='utf-8') as f:  # 执行买入成功更新本地文件
                        f.write(json.dumps(self.old_dict, ensure_ascii=False))
                    num_pingduo = 0
            dict = {'remain': remain, '成交时间': s_values[0][1], '合约代码': self.symbol,
                    '合约名称': dict_codename[self.symbol], '类型': "卖平", '成交量': int(self.res_pingduo),
                    '成交价': currentprice, '平仓盈亏': round(profitandloss_duo, 2)}
            self.old_dict.append(dict)
            with open(PATH_BAK, 'w', encoding='utf-8') as f:  # 执行买入成功更新本地文件
                f.write(json.dumps(self.old_dict, ensure_ascii=False))
            self.getCurrentData()
            print(showinfo(title="提示",
                           message=dict['合约名称'] + self.symbol + ' ' + dict['类型'] + ' ' + str(
                               dict['成交量']) + "手。"))
            window.destroy()

    # 取消平多（卖平）
    def nopingduo(self, window):
        window.destroy()

    # 要平空（买平）
    def yespingkong(self, window, num_kong):
        global remain
        self.res_pingkong = self.entry_pingkong.get()
        s_str = self.df.loc[self.df['symbol'] == self.symbol].astype(str)
        s_values = s_str.values
        currentprice = float(s_values[0][2])
        pershouprice = dict_tradeunit[self.symbol] * currentprice * dict_marginratio[self.symbol]

        if int(self.res_pingkong) > num_kong:
            print(showerror(title="警告", message="超过可交易手数上限。"))
        else:
            remain = remain + int(self.res_pingkong) * int(pershouprice)
            tempt_dict = []  # 用于收集所有该symbol下的、还没完全平仓的卖开成交记录
            profitandloss_kong = 0
            num_pingkong = int(self.res_pingkong)  # 需要平仓的手数
            for i in self.old_dict:
                if i['合约代码'] == self.symbol and i['类型'] == '卖开' and i['已平仓手数'] != i['成交量']:
                    tempt_dict.append(i)
            for i in tempt_dict:
                if num_pingkong == 0:
                    break
                if i['成交量'] - i['已平仓手数'] <= num_pingkong:
                    num_pingkong -= (i['成交量'] - i['已平仓手数'])
                    # 更新self.old_dict、json数据
                    with open(PATH_BAK, 'r', encoding='utf-8') as f:
                        filetmp = f.read()
                        if filetmp:
                            for j in self.old_dict:
                                if j['合约代码'] == i['合约代码'] and j['类型'] == i['类型'] and j['成交时间'] == i[
                                    '成交时间'] and j['已平仓手数'] == i['已平仓手数']:
                                    profitandloss_kong += (i['成交量'] - i['已平仓手数']) * (
                                            j['成交价'] - currentprice) * dict_tradeunit[j['合约代码']]
                                    j['已平仓手数'] = j['成交量']
                    with open(PATH_BAK, 'w', encoding='utf-8') as f:  # 执行买入成功更新本地文件
                        f.write(json.dumps(self.old_dict, ensure_ascii=False))
                else:
                    # 更新self.old_dict、json数据
                    with open(PATH_BAK, 'r', encoding='utf-8') as f:
                        filetmp = f.read()
                        if filetmp:
                            for j in self.old_dict:
                                if j['合约代码'] == i['合约代码'] and j['类型'] == i['类型'] and j['成交时间'] == i[
                                    '成交时间'] and j['已平仓手数'] == i['已平仓手数']:
                                    j['已平仓手数'] += num_pingkong
                                    profitandloss_kong += num_pingkong * (j['成交价'] - currentprice) * dict_tradeunit[
                                        j['合约代码']]
                    with open(PATH_BAK, 'w', encoding='utf-8') as f:  # 执行买入成功更新本地文件
                        f.write(json.dumps(self.old_dict, ensure_ascii=False))
                    num_pingkong = 0
            dict = {'remain': remain, '成交时间': s_values[0][1], '合约代码': self.symbol,
                    '合约名称': dict_codename[self.symbol], '类型': "买平", '成交量': int(self.res_pingkong),
                    '成交价': currentprice, '平仓盈亏': round(profitandloss_kong, 2)}
            self.old_dict.append(dict)
            with open(PATH_BAK, 'w', encoding='utf-8') as f:  # 执行买入成功更新本地文件
                f.write(json.dumps(self.old_dict, ensure_ascii=False))
            self.getCurrentData()
            print(showinfo(title="提示", message=dict['合约名称'] + self.symbol + ' ' + dict['类型'] + ' ' + str(
                dict['成交量']) + "手。"))
            window.destroy()

    # 取消平空（买平）
    def nopingkong(self, window):
        window.destroy()

    # 账户分析
    def execOpanalyze(self):
        print("账户分析")

    # frame3_1中，按照所输入的条件进行筛选
    def yesquery1(self):
        time = self.entry_time1.get().strip()
        symbol = self.combo_box_querysymbol1.get().strip()
        kind = self.combo_box_querykind1.get().strip()
        tempt_dict = []
        for item in self.old_dict:
            if time in item['成交时间'] and symbol in item['合约代码'] and kind in item['类型']:
                tempt_dict.append(item)
        # 展示数据
        index = 0
        # 清空表格数据，更新tree数据
        x = self.tree.get_children()
        for item in x:
            self.tree.delete(item)
        for i in tempt_dict:
            # columns1 = ("成交时间", "合约代码", "合约名称", "类型", "成交量", "成交价", "平仓盈亏")  # 成交记录
            # columns2 = ("合约代码", "合约名称", "类型", "总仓", "开仓均价", "逐笔盈亏")  # 持仓记录
            self.tree.insert('', index, values=(
                i['成交时间'], i['合约代码'], i['合约名称'], i['类型'], i['成交量'], i['成交价'], i['平仓盈亏']))
            index += 1

    # frame3_1中，显示所有成交历史
    def yesall1(self):
        self.combo_box_querysymbol1.set('')
        self.combo_box_querykind1.set('')
        # frame3数据
        index = 0
        # 清空表格数据，更新tree数据
        x = self.tree.get_children()
        for item in x:
            self.tree.delete(item)
        for i in self.old_dict:
            # columns1 = ("成交时间", "合约代码", "合约名称", "类型", "成交量", "成交价", "平仓盈亏")  # 成交记录
            # columns2 = ("合约代码", "合约名称", "类型", "总仓", "开仓均价", "逐笔盈亏")  # 持仓记录
            self.tree.insert('', index,
                             values=(i['成交时间'], i['合约代码'], i['合约名称'], i['类型'], i['成交量'], i['成交价'],
                                     i['平仓盈亏']))
            index += 1

    # frame3_2中，按照所输入的条件进行筛选
    def yesquery2(self):
        symbol = self.combo_box_querysymbol2.get().strip()
        kind = self.combo_box_querykind2.get().strip()
        tempt_dict = []
        for item in self.old_dict2:
            if symbol in item['合约代码'] and kind in item['类型']:
                tempt_dict.append(item)
        # 展示数据
        index = 0
        # 清空表格数据，更新tree数据
        x = self.tree2.get_children()
        for item in x:
            self.tree2.delete(item)
        for i in tempt_dict:
            # columns1 = ("成交时间", "合约代码", "合约名称", "类型", "成交量", "成交价", "平仓盈亏")  # 成交记录
            # columns2 = ("合约代码", "合约名称", "类型", "总仓", "开仓均价", "逐笔盈亏")  # 持仓记录
            self.tree2.insert('', index,
                              values=(i['合约代码'], i['合约名称'], i['类型'], i['总仓'], i['开仓均价'], i['逐笔盈亏']))
            index += 1

    # frame3_2中，显示所有持仓记录
    def yesall2(self):
        self.combo_box_querysymbol2.set('')
        self.combo_box_querykind2.set('')
        # frame3数据
        index = 0
        x = self.tree2.get_children()
        for item in x:
            self.tree2.delete(item)
        for i in self.old_dict2:
            # columns1 = ("成交时间", "合约代码", "合约名称", "类型", "成交量", "成交价", "平仓盈亏")  # 成交记录
            # columns2 = ("合约代码", "合约名称", "类型", "总仓", "开仓均价", "逐笔盈亏")  # 持仓记录
            self.tree2.insert('', index,
                              values=(i['合约代码'], i['合约名称'], i['类型'], i['总仓'], i['开仓均价'], i['逐笔盈亏']))
            index += 1

    # 更新表格数据
    def getCurrentData(self):
        # frame3数据
        index = 0
        position = 0  # 总持仓资金,总市值=总持仓
        # 清空表格数据，更新self.tree数据
        x = self.tree.get_children()
        for item in x:
            self.tree.delete(item)
        for i in self.old_dict:
            # columns1 = ("成交时间", "合约代码", "合约名称", "类型", "成交量", "成交价", "平仓盈亏")  # 成交记录
            # columns2 = ("合约代码", "合约名称", "类型", "总仓", "开仓均价", "逐笔盈亏")  # 持仓记录
            self.tree.insert('', index,
                             values=(i['成交时间'], i['合约代码'], i['合约名称'], i['类型'], i['成交量'], i['成交价'],
                                     i['平仓盈亏']))
            # if i['类型'] == '买开' or i['类型'] == '买平':
            #     self.tree.tag_configure('buy', foreground='red')
            #     self.tree.item('', tags=('buy',), values=(i['成交时间'], i['合约代码'], i['合约名称'], i['类型'], i['成交量'], i['成交价'], i['平仓盈亏']))
            # if i['类型'] == '卖开' or i['类型'] == '卖平':
            #     self.tree.tag_configure('sell', foreground='green')
            #     self.tree.item('4', tags=('sell',), values=(i['成交时间'], i['合约代码'], i['合约名称'], i['类型'], i['成交量'], i['成交价'], i['平仓盈亏']))
            s_str = self.df.loc[self.df['symbol'] == self.symbol].astype(str)
            s_values = s_str.values
            currentprice = float(s_values[0][2])
            if i['类型'] == "买开" or i['类型'] == "卖开":
                position += dict_tradeunit[i['合约代码']] * currentprice * dict_marginratio[i['合约代码']] * i['成交量']
            index += 1
        # 清空表格数据，更新tree2数据
        index = 0
        x = self.tree2.get_children()
        for item in x:
            self.tree2.delete(item)
        # columns1 = ("成交时间", "合约代码", "合约名称", "类型", "成交量", "成交价", "平仓盈亏")  # 成交记录
        # columns2 = ("合约代码", "合约名称", "类型", "总仓", "开仓均价", "逐笔盈亏")  # 持仓记录
        self.old_dict2 = []  # 用于记录计算而得的持仓数据
        # 对每一个合约，计算持仓数据（多+空）
        profitandloss = 0
        for i in codelist:
            dict_duo = {}  # 记录代码为i 买开的
            dict_kong = {}  # 记录代码为i 卖开的
            num_duo = 0
            num_kong = 0
            average_price_duo = 0
            average_price_kong = 0
            profitandloss_duo = 0
            profitandloss_kong = 0
            s_stri = self.df.loc[self.df['symbol'] == i].astype(str)
            s_valuesi = s_stri.values
            currentpricei = float(s_valuesi[0][2])
            for j in self.old_dict:
                if j['合约代码'] == i:
                    if j['类型'] == '买开':
                        num_duo += (j['成交量'] - j['已平仓手数'])
                        average_price_duo += (j['成交量'] - j['已平仓手数']) * j['成交价']
                        profitandloss_duo += (j['成交量'] - j['已平仓手数']) * (currentpricei - j['成交价']) * dict_tradeunit[j['合约代码']]
                    if j['类型'] == '卖开':
                        num_kong += (j['成交量'] - j['已平仓手数'])
                        average_price_kong += (j['成交量'] - j['已平仓手数']) * j['成交价']
                        profitandloss_kong += (j['成交量'] - j['已平仓手数']) * (j['成交价'] - currentpricei) * dict_tradeunit[j['合约代码']]
            if num_duo != 0:
                dict_duo = {'合约代码': i, '合约名称': dict_codename[i], '类型': '多', '总仓': num_duo,
                            '开仓均价': round(average_price_duo / num_duo, 2), '逐笔盈亏': round(profitandloss_duo, 2)}
                self.old_dict2.append(dict_duo)
                profitandloss += profitandloss_duo
            if num_kong != 0:
                dict_kong = {'合约代码': i, '合约名称': dict_codename[i], '类型': '空', '总仓': num_kong,
                             '开仓均价': round(average_price_kong / num_kong, 2),
                             '逐笔盈亏': round(profitandloss_kong, 2)}
                self.old_dict2.append(dict_kong)
                profitandloss += profitandloss_kong
        for i in self.old_dict2:
            # columns1 = ("成交时间", "合约代码", "合约名称", "类型", "成交量", "成交价", "平仓盈亏")  # 成交记录
            # columns2 = ("合约代码", "合约名称", "类型", "总仓", "开仓均价", "逐笔盈亏")  # 持仓记录
            self.tree2.insert('', index,
                              values=(i['合约代码'], i['合约名称'], i['类型'], i['总仓'], i['开仓均价'], i['逐笔盈亏']))
            index += 1
        # 更新frame2统计数据
        ratio = 0
        ratio = (position + remain - TOTAL_ASSETS) / TOTAL_ASSETS
        self.s2.set(str(round(position + remain, 2)))  # 总资产=总持仓+剩余资产
        self.s3.set(format(ratio, '.2%'))  # 总盈亏=(总资产-启动资金)/启动资金
        self.s4.set(str(remain))
        self.s5.set(str(round(position, 2)))  # 总市值=总持仓
        if len(self.old_dict) == 0:
            self.s6.set('-')
        else:
            self.s6.set(str(round(profitandloss, 2)))
        self.s7.set(format((1000000 - remain) / 1000000, '.2%'))

    def change_symbol(self, aaa):
        self.symbol = self.combo_box.get()
        s_str = self.df.loc[self.df['symbol'] == self.symbol, 'close'].astype(str)
        s_values = s_str.values
        self.s12.set(dict_codename[self.symbol])
        self.s13.set(str(dict_tradeunit[self.symbol]) + " 吨/手")
        self.s14.set(str(int(dict_marginratio[self.symbol] * 100)) + " %")
        self.s15.set(s_values[0])
        self.s16.set(
            str(round(dict_tradeunit[self.symbol] * float(s_values[0]) * dict_marginratio[self.symbol])) + ' 元')
        # 每次改变合约都向主页传参，主页也要改变合约
        self.signal_symbol.emit(self.symbol)  # 发射信号

    def treeviewClick1(self, event):
        dict = {}
        dict2 = {}
        symbol_name = None
        for item in self.tree.selection():
            #  values=(i['成交时间'], i['合约代码'], i['合约名称'], i['类型'], i['成交量'], i['成交价'], i['平仓盈亏']))
            item_text = self.tree.item(item, "values")
            symbol_name = item_text[1]
        for i in self.old_dict2:
            if i['合约代码'] == symbol_name and i['类型'] == '多':
                dict = i
            if i['合约代码'] == symbol_name and i['类型'] == '空':
                dict2 = i
        # 每次双击某条持仓记录都向主页传参，显示持仓记录
        self.signal2.emit(symbol_name, dict, dict2)  # 发射信号

    def treeviewClick2(self, event):
        dict = {}
        dict2 = {}
        for item in self.tree2.selection():
            # values = (i['合约代码'], i['合约名称'], i['类型'], i['总仓'], i['开仓均价'], i['逐笔盈亏']))
            item_text = self.tree2.item(item, "values")
            dict = {'合约代码': item_text[0], '合约名称': item_text[1], '类型': item_text[2], '总仓': item_text[3],
                         '开仓均价':item_text[4], '逐笔盈亏': item_text[5]}
        for i in self.old_dict2:
            if i['合约代码'] == dict['合约代码'] and i['类型'] != dict['类型']:
                dict2 = i
                break
        # 每次双击某条持仓记录都向主页传参，显示持仓记录
        self.signal2.emit(dict['合约代码'], dict, dict2)  # 发射信号



