# 异常处理
try:
    # print(1/0)
    print(1/1)
except ZeroDivisionError:
    print("除零错误")
except Exception as e:
    print("其他错误",e)
else:
    print("没有发生异常")
finally:
    print("无论是否发生异常都会执行")
