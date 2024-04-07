import datetime
import tkinter  # 图形界面库
import threading
from tkinter import ttk
from tkinter import messagebox
from tkinter.simpledialog import askinteger

import pandas as pd
import tushare as ts  # 量化分析数据库
import os  # 用于文件操作
import json  # 用于保存导出我们记录的操作

TOTAL_ASSETS = 1000000  # 个人资产
PATH_BAK = 'myfile.json'

data_all = []
tmplist = []
codelist = ['RB888', 'RB99', 'SA99', 'SA888', 'jm888', 'jm99']  # 存储期货代码
codename = ['螺纹钢指数', '螺纹钢主连', '纯碱主连', '纯碱指数', '焦煤指数', '焦煤主连']
dict_code = {'RB888':'螺纹钢指数', 'RB99':'螺纹钢主连', 'SA99':'纯碱主连', 'SA888':'纯碱指数', 'jm888':'焦煤指数', 'jm99':'焦煤主连'}
remain = TOTAL_ASSETS  # 剩余资产
columns = ("时间", "代码", "名称", "开平", "持仓", "价位")


class tradeDemo:
    def __init__(self, symbol, current_whole_df):
        self.symbol = symbol
        self.current_whole_df = current_whole_df  # symbol下，时间边界选择之后的数据

        self.gui = tkinter.Tk()
        self.gui.title('模拟交易界面')
        self.gui.geometry('1500x800')

        frame1 = tkinter.LabelFrame(self.gui, text="市场情况", width=750, height=400)
        frame1.place(x=0, y=0)
        frame2 = tkinter.LabelFrame(self.gui, text="个人情况", width=750, height=400)
        frame2.place(x=750, y=0)
        frame3 = tkinter.LabelFrame(self.gui, text="交易历史", width=1500, height=400)
        frame3.place(x=0, y=400)


        ## 市场情况框架中的控件
        # 1.合约
        l1_symbol = tkinter.Label(frame1, text='合约:')
        l1_symbol.place(x=10, y=5)
        self.s11 = tkinter.StringVar()
        self.s11.set(str(self.symbol))
        l1 = tkinter.Label(frame1, textvariable=self.s11, width=10, height=1, bg='white', anchor='w',
                           font=("Courier", 11, "italic"))
        l1.place(x=70, y=5)
        # 2.手数
        l2_shoushu = tkinter.Label(frame1, text='1手：')
        l2_shoushu.place(x=260, y=5)
        self.s12 = tkinter.StringVar()
        self.s12.set("10吨")
        l2 = tkinter.Label(frame1, textvariable=self.s12, width=10, height=1, bg='white', anchor='w',
                           font=("Courier", 11, "italic"))
        l2.place(x=320, y=5)
        # 3.现价
        l3_currentPrice = tkinter.Label(frame1, text='现价：')
        l3_currentPrice.place(x=510, y=5)
        self.s13 = tkinter.StringVar()
        print(self.current_whole_df.iloc[-1]['closePrice'])
        self.s13.set(str(self.current_whole_df.iloc[-1]['closePrice']))
        l3 = tkinter.Label(frame1, textvariable=self.s13, width=10, height=1, bg='white', anchor='w',
                           font=("Courier", 11, "italic"))
        l3.place(x=570, y=5)
        # 4.买多
        b_duo = tkinter.Button(frame1, text='买多', width=10, height=1, bg='white', fg='red',
                               command=self.execOpduo)
        b_duo.place(x=40, y=50)
        # 5.卖空
        b_kong = tkinter.Button(frame1, text='卖空', width=10, height=1, bg='white', fg='green',
                                command=self.execOpkong)
        b_kong.place(x=290, y=50)
        # 6.平仓
        b_ping = tkinter.Button(frame1, text='平仓', width=10, height=1, bg='white', fg='blue',
                                command=self.execOpping)
        b_ping.place(x=540, y=50)

        ## 我的交易框架中的控件
        # 1.总资产
        l2_t = tkinter.Label(frame2, text='总资产:')
        l2_t.place(x=10, y=5)
        self.s2 = tkinter.StringVar()
        self.s2.set(str(TOTAL_ASSETS))
        l2 = tkinter.Label(frame2, textvariable=self.s2, width=10, height=1, bg='white', anchor='w',
                           font=("Courier", 11, "italic"))
        l2.place(x=80, y=5)
        # 2.总盈亏
        l3_t = tkinter.Label(frame2, text='总盈亏:')
        l3_t.place(x=260, y=5)
        self.s3 = tkinter.StringVar()
        l3 = tkinter.Label(frame2, textvariable=self.s3, width=10, height=1, bg='white', anchor='w',
                           font=("Courier", 11, "italic"))
        l3.place(x=340, y=5)
        # 3.剩余可用
        l4_t = tkinter.Label(frame2, text='剩余可用:')
        l4_t.place(x=510, y=5)
        self.s4 = tkinter.StringVar()
        l4 = tkinter.Label(frame2, textvariable=self.s4, width=10, height=1, bg='white', anchor='w',
                           font=("Courier", 11, "italic"))
        l4.place(x=600, y=5)
        # 4.总市值
        l5_t = tkinter.Label(frame2, text='总市值:')
        l5_t.place(x=10, y=53)
        self.s5 = tkinter.StringVar()
        l5 = tkinter.Label(frame2, textvariable=self.s5, width=10, height=1, bg='white', anchor='w',
                           font=("Courier", 11, "italic"))
        l5.place(x=80, y=50)
        # 5.持仓盈亏
        l6_t = tkinter.Label(frame2, text='持仓盈亏:')
        l6_t.place(x=260, y=53)
        self.s6 = tkinter.StringVar()
        l6 = tkinter.Label(frame2, textvariable=self.s6, width=10, height=1, bg='white', anchor='w',
                           font=("Courier", 11, "italic"))
        l6.place(x=340, y=50)
        # 6.综合评价
        l7_t = tkinter.Label(frame2, text='综合评价:')
        l7_t.place(x=510, y=53)
        self.s7 = tkinter.StringVar()
        l7 = tkinter.Label(frame2, textvariable=self.s7, width=10, height=1, bg='white', anchor='w',
                           font=("Courier", 11, "italic"))
        l7.place(x=600, y=50)

        ## 交易历史框架中
        # columns = ("时间", "代码", "名称", "开平", "持仓", "价位")
        self.tree = ttk.Treeview(frame3, height=18, show="headings", columns=columns)
        self.tree.column("时间", width=250, anchor='center')  # 表示列,不显示
        self.tree.column("代码", width=200, anchor='center')
        self.tree.column("名称", width=200, anchor='center')
        self.tree.column("开平", width=200, anchor='center')
        self.tree.column("持仓", width=200, anchor='center')
        self.tree.column("价位", width=200, anchor='center')

        self.tree.heading("时间", text="时间")  # 显示表头
        self.tree.heading("代码", text="代码")
        self.tree.heading("名称", text="名称")
        self.tree.heading("开平", text="开平")
        self.tree.heading("持仓", text="持仓")
        self.tree.heading("价位", text="价位")
        # self.tree.bind('<Double-1>', self.treeviewClick2)
        self.tree.place(x=0, y=0)

        # 我的持仓初始化
        global mylist
        self.initMyList()
        global data_all
        self.getCurrentData()
        self.gui.mainloop()

    # 我的持仓初始化
    def initMyList(self):
        global remain
        self.old_dict = []
        with open(PATH_BAK, 'r', encoding='utf-8') as f:
            filetmp = f.read()
            if filetmp:
                self.old_dict = json.loads(filetmp)
                print(self.old_dict)
                for i in self.old_dict:
                    remain = i['remain']
                    break
            else:
                remain = TOTAL_ASSETS

    # 买多
    def execOpduo(self):
        print("买多")
        global remain
        max = remain // int(self.current_whole_df.iloc[-1]['closePrice'] * 100)  # 设定交易手数的上限，如果余额不足则不予交易（最少交易一手=100股）
        res = askinteger(self.symbol, "买入/手：", initialvalue=1, minvalue=1, maxvalue=max)
        if res:
            remain = remain - res * int(float(self.current_whole_df.iloc[-1]['closePrice']) * 100)
            dict = {'remain':remain, '时间':self.current_whole_df.iloc[-1]['tradeDate'], '代码':self.symbol,
                    '名称':dict_code[self.symbol], '开平':"多开", '持仓':res, '价位':self.current_whole_df.iloc[-1]['closePrice']}
            # dict['remain'] = remain
            # dict['时间'] = self.current_whole_df.iloc[-1]['tradeDate']
            # dict['代码'] = self.symbol
            # dict['名称'] = dict_code[self.symbol]
            # dict['开平'] = "多开"
            # dict['持仓'] = res
            # dict['价位'] = self.current_whole_df.iloc[-1]['closePrice']
            self.old_dict.append(dict)
            with open(PATH_BAK, 'w', encoding='utf-8') as f:  # 执行买入成功更新本地文件
                f.write(json.dumps(self.old_dict, ensure_ascii=False))
            self.getCurrentData()
        else:
            print('取消买入！')


    def execOpkong(self):
        print("买空")


    def execOpping(self):
        print("平仓")

    def getCurrentData(self):  # 获得当前数据
        # frame3数据
        index = 0
        position = 0
        # 清空表格数据
        x = self.tree.get_children()
        for item in x:
            self.tree.delete(item)
        for i in self.old_dict:
            self.tree.insert('', index, values=(i['时间'], i['代码'], i['名称'], i['开平'], i['持仓'], i['价位']))
            position += int(float(i['价位'])*100) * i['持仓']
            index += 1
        # 更新frame2统计数据
        ratio = 0
        ratio = (position+remain-TOTAL_ASSETS)/TOTAL_ASSETS
        self.s2.set(str(position + remain))  # 总资产=总持仓+剩余资产
        self.s3.set(format(ratio, '.2%'))  # 总盈亏=(总资产-启动资金)/启动资金
        self.s4.set(str(remain))
        self.s5.set(str(position))  # 总市值=总持仓
        self.s6.set('-')
        if ratio <= -1:
            self.s7.set('反向股神')
        elif ratio > -1 and ratio <= -0.2:
            self.s7.set('韭皇')
        elif ratio > -0.2 and ratio <= 0:
            self.s7.set('小韭菜')
        elif ratio > 0 and ratio <=0.2:
            self.s7.set('股仔')
        elif ratio > 0.2 and ratio <= 1:
            self.s7.set('股尊')
        elif ratio > 1:
            self.s7.set('股神')

