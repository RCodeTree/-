# format 函数 格式化字符串
year = 2023
name1 = "Alice"
string1 = "{0}年".format(year) # 位置参数
string2 = "Hello, {name}!".format(name=name1) # 关键字参数
print(string1)
print(string2)

# f 格式化字符串
name2 = "Alice"
age = 25
string = f"My name is {name2} and I am {age} years old."
print(string)
