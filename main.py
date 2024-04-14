# This is a sample Python script.
import pandas as pd


# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.
    # 创建数据
    data = pd.DataFrame(data=[['bar', 'one', 'z', '1'],
                              ['bar', 'two', 'v', '2'],
                              ['foo', 'one', 'x', '3'],
                              ['foo', 'two', 'w', '4']])
    print(data)
    data.columns = ['a', 'b', 'c', 'd']
    # data.set_index('c', inplace=True)
    print(data)
    # data.reset_index(inplace=True)
    d = data.loc[data['a'] == 'bar' and data['b'] == 'one']['c']
    print(d)



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

