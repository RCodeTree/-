# 文件写入

# w 覆盖写入，a 追加写入 如果没有目标写入文件，在文件写入时会自动创建
# file = open("./test.txt", "w", encoding="utf-8")
# file.write("床前明月光，疑是地上霜。\n")
# file.write("举头望明月，低头思故乡。\n")
# file.close()

file = open("./test.txt", "a", encoding="utf-8")
file.write("千山鸟飞绝，万径人踪灭。\n")
file.write("孤舟蓑笠翁，独钓寒江雪。\n")
file.close()

# r+ 读写模式
file = open("./test.txt", "r+", encoding="utf-8")
file.write("春风又绿江南岸，明月何时照我还。\n")
file.close()


with open("./test.txt", "r+", encoding="utf-8") as file:
    file.write("春风又绿江南岸，明月何时照我还。\n")
    print(file.read())

