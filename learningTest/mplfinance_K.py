import mplfinance as mpf
import matplotlib.pyplot as plt
import pandas as pd
import akshare as ak
from cycler import cycler  # 用于定制线条颜色
import matplotlib as mpl  # 用于设置曲线参数
import talib
import matplotlib.pyplot as plt
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.ticker as ticker

# 返回符合mplfinance要求的数据
def getDf(df):
    df_new = pd.DataFrame(df, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
    df_new.columns = ['date', 'Open', 'High', 'Low', 'Close', 'Volume']
    # 转换为日期格式
    df_new['date'] = pd.to_datetime(df_new['date'])
    # 将日期列作为行索引
    df_new.set_index("date", inplace=True)
    # print(df_new)
    # print(df_new.axes)
    return df_new


# 画K线图、均线图、成交量
def draw(symbol, df):
    kwargs = dict(
        type='candle',  # type:绘制图形的类型(candle, renko, ohlc, line)
        mav=(5, 10, 30),  # mav(moving average):均线类型,此处设置5,10,30日线
        volume=True,  # volume:布尔类型，设置是否显示成交量，默认False
        title='\n candle_line:%s' % (symbol),  # title:设置标题
        ylabel='OHLC Candles',  # y_label:设置纵轴主标题
        ylabel_lower='Shares\nTraded Volume',  # y_label_lower:设置成交量图一栏的标题
        figratio=(15, 10),  # figratio:设置图形纵横比
        figscale=5)  # figscale:设置图形尺寸(数值越大图像质量越高)
    mc = mpf.make_marketcolors(
        up='red',  # up:设置K线线柱颜色，up意为收盘价大于等于开盘价
        down='green',  # down:与up相反，这样设置与国内K线颜色标准相符
        edge='i',  # edge:K线线柱边缘颜色(i代表继承自up和down的颜色)，下同。详见官方文档)
        wick='i',  # wick:灯芯(上下影线)颜色
        volume='in',  # volume:成交量直方图的颜色
        inherit=True)  # inherit:是否继承，选填
    s = mpf.make_mpf_style(
        gridaxis='both',  # gridaxis:设置网格线位置
        gridstyle='-.',  # gridstyle:设置网格线线型
        y_on_right=False,  # y_on_right:设置y轴位置是否在右
        marketcolors=mc)
    # 设置均线颜色
    mpl.rcParams['axes.prop_cycle'] = cycler(
        color=['dodgerblue', 'deeppink',
               'navy', 'teal', 'maroon', 'darkorange',
               'indigo'])
    # 设置线宽
    mpl.rcParams['lines.linewidth'] = .5
    # 图形绘制
    # show_nontrading:是否显示非交易日，默认False
    mpf.plot(df.loc['2024-01-16 13:00':'2024-01-16 16:00', :],
             **kwargs,
             style=s,
             show_nontrading=False)
    plt.show()


# 画K线图、均线图、成交量（自定义均线，成交量）
def draw_def(start, end, df, mav_def, volume_def):
    if volume_def:
        kwargs = dict(
            type='candle',  # type:绘制图形的类型(candle, renko, ohlc, line)
            mav=mav_def,  # mav(moving average):均线类型
            volume=True,  # volume:布尔类型，设置是否显示成交量，默认False
            ylabel_lower='Shares\nTraded Volume',  # y_label_lower:设置成交量图一栏的标题
            figratio=(15, 10),  # figratio:设置图形纵横比
            figscale=5)  # figscale:设置图形尺寸(数值越大图像质量越高)
        mc = mpf.make_marketcolors(
            up='red',  # up:设置K线线柱颜色，up意为收盘价大于等于开盘价
            down='green',  # down:与up相反，这样设置与国内K线颜色标准相符
            edge='i',  # edge:K线线柱边缘颜色(i代表继承自up和down的颜色)，下同。详见官方文档)
            wick='i',  # wick:灯芯(上下影线)颜色
            volume='in',  # volume:成交量直方图的颜色
            inherit=True)  # inherit:是否继承，选填
    else:
        kwargs = dict(
            type='candle',  # type:绘制图形的类型(candle, renko, ohlc, line)
            mav=mav_def,  # mav(moving average):均线类型
            volume=False,  # volume:布尔类型，设置是否显示成交量，默认False
            figratio=(15, 10),  # figratio:设置图形纵横比
            figscale=5)  # figscale:设置图形尺寸(数值越大图像质量越高)
        mc = mpf.make_marketcolors(
            up='red',  # up:设置K线线柱颜色，up意为收盘价大于等于开盘价
            down='green',  # down:与up相反，这样设置与国内K线颜色标准相符
            edge='i',  # edge:K线线柱边缘颜色(i代表继承自up和down的颜色)，下同。详见官方文档)
            wick='i',  # wick:灯芯(上下影线)颜色
            inherit=True)  # inherit:是否继承，选填
    s = mpf.make_mpf_style(
        gridaxis='both',  # gridaxis:设置网格线位置
        gridstyle='-.',  # gridstyle:设置网格线线型
        y_on_right=False,  # y_on_right:设置y轴位置是否在右
        marketcolors=mc)
    # 设置均线颜色
    mpl.rcParams['axes.prop_cycle'] = cycler(
        color=['dodgerblue', 'deeppink',
               'navy', 'teal', 'maroon', 'darkorange',
               'indigo'])
    # 设置线宽
    mpl.rcParams['lines.linewidth'] = .5
    # 图形绘制
    # show_nontrading:是否显示非交易日，默认False
    mpf.plot(df.loc[start:end, :],
             **kwargs,
             style=s,
             show_nontrading=False)
    plt.show()


#  画KDJ
def draw_kdj(df, start, end):
    plt.figure(figsize=(12, 8))
    df_new = df
    df_new['datetime'] = pd.to_datetime(df_new['datetime'])
    df_new = df_new[(df_new['datetime'] >= start) & (df_new['datetime'] <= end)]
    df_new["rsi"] = talib.RSI(df_new["close"])
    #plt.set_ylabel("(%)")
    plt.plot(df_new['datetime'], [70] * len(df_new['datetime']), label="overbought")
    plt.plot(df_new['datetime'], [30] * len(df_new['datetime']), label="oversold")
    plt.plot(df_new['datetime'], df_new["rsi"], label="rsi")
    # plt.set_title('KDJ')
    plt.legend()
    plt.show()


# 所有金融期货(中金所主力合约)具体合约
cffex_text = ak.match_main_contract(symbol="cffex")
# class 'str' -> class 'list'
cffex_text = cffex_text.split(',')
#for i in cffex_text:
#    futures_zh_minute_sina_df = ak.futures_zh_minute_sina(symbol=i, period="1")
#    draw(i, getDf(futures_zh_minute_sina_df))
futures_zh_minute_sina_df = ak.futures_zh_minute_sina(symbol=cffex_text[2], period="1")
print(getDf(futures_zh_minute_sina_df))
draw_def('2024-01-19 14:00', '2024-01-19 15:00', getDf(futures_zh_minute_sina_df), (5,10,30), True)
draw_kdj(futures_zh_minute_sina_df, '2024-01-19 14:00', '2024-01-19 15:00')
# plot_chart(cffex_text[2], futures_zh_minute_sina_df,'2024-01-18 15:00', '2024-01-20 15:00')
