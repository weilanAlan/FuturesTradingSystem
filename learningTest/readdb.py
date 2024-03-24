import sqlite3
from pandas.core.frame import DataFrame

symbol = "RB888"

# 连接
conn = sqlite3.connect("C:/Users/12345/Desktop/FuturesTradingSystem/database/database.db")
c = conn.cursor()

# 正常执行SQL查询
# c.execute("select * from dbbardata where symbol={};".format(symbol))
c.execute("select * from dbbardata where symbol='%s'"%(symbol))
rows = c.fetchall()  # rows返回所有记录，rows是一个二维列表
data = DataFrame(rows)
data.rename(columns={0: 'id', 1: 'symbol', 2: 'exchange', 3: 'datetime', 4: 'interval', 5: 'volume', 6: 'turnover',
                     7: 'open_interset', 8: 'open', 9: 'high', 10: 'low', 11: 'close'}, inplace=True)
print(type(data))
print(data)

# 关闭
c.close()
conn.close()
