import json
dict1 = {'a':1, 'b':2, 'c':3}
dict2 = {'a':1, 'B':2, 'C':3}
dict3 = {'a':1, 'b':2, 'z':3}
dict_list = []
dict_list.append(dict1)
dict_list.append(dict2)
dict_list.append(dict3)
# 其实，我完全可以这样写dict_list = [dict1，dict2，dict3]；之所如上述那么些，是让大家知道，我们是动态控制的
with open('demo3.json', mode='w', encoding='utf-8') as f:
    json.dump(dict_list, f)
    # 将字典列表存入json文件中

with open('demo3.json', mode='r', encoding='utf-8') as f:
    dicts = json.load(f)
    # 将多个字典从json文件中读出来
    for i in dicts:
        print(type(i))
        print(i['a'])
        print(i)
        break
