# 列表 --- 列表是可变的数据结构
list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
print("列表的长度：" + str(len(list)))
list.append(11)  # 添加元素
list.remove(list[1])  # 删除元素
list.remove(1)
print(list)

print("-----------------------------------")

# 元组 --- 元组是不可变的数据结构
Tuple = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
print("元组的长度：" + str(len(Tuple)))

print("-----------------------------------")

# 字典 --- 键值对(键是不可变的，值是可变的)，字典是可变的数据结构
# 因此，元组可以作为字典的键
Dict = {
    "张三": 18,
    (1, 2, 3): "数字"
}
print("字典的长度：" + str(len(Dict)))
print(Dict.keys()) # 字典的键
print(Dict.values()) # 字典的值
Dict.pop("张三") # 根据键删除值
print("张三" in Dict) # False
print(Dict)