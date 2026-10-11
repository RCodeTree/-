# 类继承练习：人力系统
# - 员工分为两类：全职员工 FullTimeEmployee、兼职员工 PartTimeEmployee。
# - 全职和兼职都有"姓名 name"、"工号 id"属性，
#   都具备"打印信息 print_info"（打印姓名、工号）方法。
# - 全职有"月薪 monthly_salary"属性，
#   兼职有"日薪 daily_salary"属性、"每月工作天数 work_days"的属性。
# - 全职和兼职都有"计算月薪 calculate_monthly_pay"的方法，但具体计算过程不一样
class Employee:
    def __init__(self, name, id):
        self.name = name
        self.id = id

    def print_info(self):
        print("姓名:", self.name, "工号:", self.id)

    def calculate_monthly_pay(self):
        pass



class FullTimeEmployee(Employee):
    def __init__(self, name, id, monthly_salary):
        super().__init__(name, id)
        self.monthly_salary = monthly_salary

    def calculate_monthly_pay(self):
        return self.monthly_salary



class PartTimeEmployee(Employee):
    def __init__(self, name, id, daily_salary):
        super().__init__(name, id)
        self.daily_salary = daily_salary

    def calculate_monthly_pay(self, work_days):
        return self.daily_salary * work_days



# 实例化
full_time_employee = FullTimeEmployee("张三", "001", 5000)
part_time_employee = PartTimeEmployee("李四", "002", 200)

full_time_employee.print_info()
print("全职员工月薪:", full_time_employee.calculate_monthly_pay())
part_time_employee.print_info()
print("兼职员工月薪:", part_time_employee.calculate_monthly_pay(20))
