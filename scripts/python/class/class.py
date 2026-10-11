# 定义一个学生类
# 要求：
# 1. 属性包括学生姓名、学号，以及语数英三科的成绩
# 2. 能够设置学生某科目的成绩
# 3. 能够打印该学生的所有科目成绩
class Student:
    # 设置类属性
    def __init__(self, name, id):  # 构造函数 self指代类的实例，即指代对象本身
        self.name = name
        self.id = id
        self.grades = {"chinese": 0, "math": 0, "english": 0}

    # 设置类方法
    def set_grade(self, subject, score):  # 设置成绩的方法
        if subject in self.grades.keys():
            self.grades[subject] = score
        else:
            print(subject + " 科目不存在")

    def print_grades(self):  # 打印成绩的方法
        print(self.name + "的学号是：" + self.id + "，各科成绩是：")
        for subject in self.grades.keys():
            print(subject + ":" + str(self.grades[subject]))


# 创建学生对象
student1 = Student("张三", "001")
student1.set_grade("chinese", 90)
student1.set_grade("math", 80)
student1.set_grade("english", 75)
student1.set_grade("history", 85)
student1.print_grades()
