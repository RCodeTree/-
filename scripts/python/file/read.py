# 文件读取

# read() 函数读取文件所有内容 返回所有内容的字符串(包含换行符)
file = open("./test.txt", "r", encoding="utf-8")
print(file.read())
file.close()

print("--------------------------------------------------")

# readline() 函数读取文件一行内容 返回一行内容的字符串(包含换行符)
file = open("./test.txt", "r", encoding="utf-8")
print(file.readline())
file.close()

print("--------------------------------------------------")

# readlines() 函数读取文件所有行内容 返回行列表(每行一个元素)
file = open("./test.txt", "r", encoding="utf-8")
for line in file.readlines():
    print(line)
file.close()

print("--------------------------------------------------")

# with 语句读取文件 自动关闭文件
with open("./test.txt", "r", encoding="utf-8") as file:
    for line in file:
        print(line)


