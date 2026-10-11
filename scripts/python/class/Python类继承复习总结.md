# Python 类继承与面向对象核心知识总结（复习用）

> 本笔记基于同目录下的 `class.py` 与 `extend.py` 两个示例代码整理，适合复盘与复习。

---

## 一、两个文件在知识上的定位

| 文件 | 演示重点 |
|------|----------|
| `class.py` | **基础类**：类的创建、`__init__` 构造方法、`self`、实例属性、实例方法 |
| `extend.py` | **继承**：父类/子类、`super()` 调用父类构造、方法重写（Override）、多态 |

---

## 二、基础类（`class.py`）

### 1. 类的定义与构造函数

```python
class Student:
    def __init__(self, name, id):  # 构造函数，创建对象时自动调用
        self.name = name
        self.id = id
        self.grades = {"chinese": 0, "math": 0, "english": 0}
```

- `class Student:` 定义一个类。
- `__init__` 是**构造方法**（初始化器），`__xxx__` 形式叫**魔法方法/双下方法**，Python 会在 `Student("张三","001")` 时自动调用它。
- 第一次 `self.xxx = xxx` 的赋值，就动态创建了**实例属性**（Python 不需要预先声明字段）。

### 2. `self` 的本质

```python
def set_grade(self, subject, score):
    self.grades[subject] = score
```

- `self` **永远指向"当前对象实例"本身**（等价于 Java/C# 的 `this`）。
- 它是**第一个形参**，但**调用时不需要手动传**——`student1.set_grade("math",80)` 中 Python 自动把 `student1` 作为 `self` 传入。
- 所有"属于对象"的属性和方法，都必须通过 `self.` 访问。

### 3. 实例方法

```python
def print_grades(self):
    for subject in self.grades.keys():
        print(subject + ":" + str(self.grades[subject]))
```

- 第一个参数是 `self` 的函数就是**实例方法**，只能由对象调用。
- `student1.set_grade("history", 85)` 中 `"history"` 不在字典里，触发了 `else` 分支的"科目不存在"提示——这是**防御式参数校验**的小技巧。

### 4. 创建对象与使用

```python
student1 = Student("张三", "001")   # 实例化
student1.set_grade("chinese", 90)   # 调方法 → 改属性
student1.print_grades()             # 调方法 → 读属性
```

---

## 三、继承（`extend.py`）

### 1. 父类（基类 / 超类）

```python
class Employee:
    def __init__(self, name, id):
        self.name = name
        self.id = id

    def print_info(self):
        print("姓名:", self.name, "工号:", self.id)

    def calculate_monthly_pay(self):   # 父类只给"空壳"
        pass
```

- `Employee` 把**所有员工共有的**属性（name、id）和行为（print_info）抽象出来。
- `calculate_monthly_pay` 用 `pass` 占位：说明"子类必须各自实现"，这是**模板方法/接口预留**的写法。

### 2. 子类定义与 `super()`

```python
class FullTimeEmployee(Employee):          # 括号里写父类 = 继承
    def __init__(self, name, id, monthly_salary):
        super().__init__(name, id)        # 先调用父类构造，复用共有属性初始化
        self.monthly_salary = monthly_salary
```

- `class 子类(父类)` 即建立继承关系，子类**自动拥有父类的所有属性和方法**。
- `super().__init__(name, id)` 是**关键**：子类重写了 `__init__`，必须**显式调用父类构造**来初始化继承来的 `name/id`，否则父类的属性不会被创建。
- `super()` 返回一个"代理对象"，用来访问父类定义的内容，避免硬编码父类名。

### 3. 方法重写（Override）

```python
class FullTimeEmployee(Employee):
    def calculate_monthly_pay(self):          # 重写：月薪 = 固定月薪
        return self.monthly_salary

class PartTimeEmployee(Employee):
    def calculate_monthly_pay(self, work_days):  # 重写：月薪 = 日薪 × 天数
        return self.daily_salary * work_days
```

- **重写**：子类提供与父类同名的方法，从而"覆盖"父类实现。
- 注意：两个子类的 `calculate_monthly_pay` **参数不同**——这是允许的（Python 不强制签名一致），但这也意味着**多态调用时要清楚每个子类的方法签名差异**（见下文多态注意事项）。

### 4. 统一接口调用（多态）

```python
full_time_employee.print_info()             # 继承自父类，无需重写
print(full_time_employee.calculate_monthly_pay())
part_time_employee.print_info()
print(part_time_employee.calculate_monthly_pay(20))
```

- `print_info` 子类**没有重写**，直接复用父类逻辑——体现**代码复用**。
- `calculate_monthly_pay` 各自实现、**对外名称一致**——这就是**多态**："同一消息，不同对象给出不同响应"。

---

## 四、必须掌握的延伸知识（复盘重点）

### 1. 类属性 vs 实例属性

```python
class Student:
    school = "云大"          # 类属性：所有对象共享，定义在方法外、无 self
    def __init__(self, name):
        self.name = name     # 实例属性：每个对象独立
```

- 两个示例文件里用的都是**实例属性**（带 `self.`）。
- 类属性用 `Student.school` 或 `对象.school` 访问，但**不要用对象去修改类属性**（会悄悄创建同名实例属性遮蔽它）。

### 2. 类方法 / 静态方法

```python
class Student:
    school = "云大"
    @classmethod
    def get_school(cls):     # 第一个参数是类本身 cls，可访问/修改类属性
        return cls.school

    @staticmethod
    def is_valid_id(id):     # 无 self/cls，纯粹的工具函数，逻辑上属于这个类
        return id.isdigit()
```

- `@classmethod`：操作**类级别**数据时用，能继承、能多态。
- `@staticmethod`：只是"凑在类里"的普通函数，不能访问类/实例状态。

### 3. `@property` 把方法当属性用

```python
class FullTimeEmployee(Employee):
    @property
    def monthly_pay(self):       # 调用时像属性：emp.monthly_pay（无括号）
        return self.monthly_salary
```

- 适合"需要计算、但希望像只读属性一样访问"的场景，可把 `calculate_monthly_pay` 改为属性式访问。

### 4. 封装与私有（名称改写）

```python
class Employee:
    def __init__(self, name):
        self.__name = name      # 双下划线开头 → 伪私有
```

- `self.__name` 实际被改写成 `_Employee__name`，类外不能用 `obj.__name` 直接访问（但仍可 `obj._Employee__name` 强访问）。
- 单下划线 `_name` 是"约定私有"，提醒"别动"，但不强制。

### 5. 多继承与方法解析顺序（MRO）

```python
class A: ...
class B: ...
class C(A, B): ...       # 多继承：逗号分隔
print(C.__mro__)         # 查看方法查找顺序
```

- Python 用 **C3 线性化算法**决定"同名方法先找谁"，从左到右、深度优先（对新型类）。
- 实际工程中**慎用多继承**，优先用组合。

### 6. 类型判断

```python
isinstance(full_time_employee, Employee)   # True：对象是否某类（或其子类）的实例
issubclass(FullTimeEmployee, Employee)    # True：是否子类关系
```

### 7. 抽象基类（ABC）——更规范的"父类留空壳"

`extend.py` 里 `Employee.calculate_monthly_pay` 用 `pass` 占位，靠人工约定子类去实现。更严谨的写法是强制子类实现：

```python
from abc import ABC, abstractmethod

class Employee(ABC):
    @abstractmethod
    def calculate_monthly_pay(self):
        pass   # 含抽象方法的类不能实例化，子类必须实现，否则报错
```

> 这正好对应 `extend.py` 中"父类只定义、子类必须各自实现"的设计意图。

---

## 五、易错点 / 面试常考点（重点复盘）

1. **`self` 不是关键字**，只是约定俗成的第一个参数名，改成 `this` 也能跑，但千万别改（破坏可读性）。
2. **重写 `__init__` 必须 `super().__init__()`**，否则继承来的属性（如 `name/id`）是 `None` 或未定义，后续访问会 `AttributeError`。
3. **`__init__` 不是真正的构造函数**，它只是初始化器；真正的构造（内存分配）是 `__new__`。
4. **子类重写父类方法时签名可不同**：`PartTimeEmployee.calculate_monthly_pay(work_days)` 多了参数——调用方必须知道差异，否则运行时才报错。这提醒我们：真正的多态接口，最好**保持签名一致**（可把 `work_days` 放到构造里，或设默认值）。
5. **`super()` 在单继承等同于父类，多继承时按 MRO 找下一个**。
6. **类属性不要在实例上改**，会创建遮蔽用的实例属性。

---

## 六、一句话知识地图

```
面向对象三大特性（在这两个文件里都能看到）：
  封装  → 类把数据(self.xxx)和行为(方法)捆在一起
  继承  → FullTimeEmployee(Employee) 复用 + 扩展
  多态  → 同名 calculate_monthly_pay，不同对象不同实现

关键语法：
  class / __init__ / self / super() / 方法重写 /
  @classmethod / @staticmethod / @property / ABC
```

---

## 七、示例对照速查

| 概念 | 出现在哪个文件 | 对应代码 |
|------|----------------|----------|
| 类定义 | 两个文件 | `class Student:` / `class Employee:` |
| 构造函数 `__init__` | 两个文件 | `def __init__(self, ...)` |
| `self` 指向实例 | 两个文件 | 所有方法首参 |
| 实例属性 | 两个文件 | `self.name = name` |
| 继承语法 | `extend.py` | `class FullTimeEmployee(Employee)` |
| `super()` 调父类构造 | `extend.py` | `super().__init__(name, id)` |
| 方法重写 | `extend.py` | `calculate_monthly_pay` |
| 多态 | `extend.py` | 同名方法不同实现 |
| 父类空壳占位 | `extend.py` | `def calculate_monthly_pay(self): pass` |
