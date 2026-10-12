# import... 方式导入模块
import mailbox
import math

value = mailbox.mboxMessage



# from...import... 方式导入模块
from mailbox import mbox
from datetime import date
from math import sqrt
m = mbox()
d = date.today()
s = sqrt(2)



# from...import * 方式导入所有模块
from math import *
l = math.log10(10)