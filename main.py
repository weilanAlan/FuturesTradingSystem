import quantstats as qs
import pandas as pd
import numpy as np

date_index = pd.date_range(start='2020-01-01 00:00:00', periods=1000)
stock_returns = pd.Series((np.random.random(size=1000) - 0.5) / 10, index=date_index)

# 可视化并导出html文件
qs.reports.html(stock_returns, output="performance.html", download_filename="my_quant_stats.html")

# 指标计算
adj_result = qs.stats.adjusted_sortino(stock_returns)

# rolling 指标
stats_rolling_sharpe = qs.stats.rolling_sharpe(stock_returns, rolling_period=20)

# 其他指标
stats_monthly_returns = qs.stats.monthly_returns(stock_returns)

print("可计算的全部指标：", [f for f in dir(qs.stats) if f[0] != '_'])
print("可用于绘图的全部指标：", [f for f in dir(qs.stats) if f[0] != '_'])
