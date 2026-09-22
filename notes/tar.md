下面这份可以直接作为你的 Linux `tar` 命令学习笔记，重点放在**实际使用、参数理解和常见案例**上。

# Linux `tar` 命令学习笔记

## 一、tar 是什么？

`tar` 是 Linux 中非常常用的**归档工具**，主要用于：

* 将多个文件、目录打包成一个文件
* 解包归档文件
* 查看归档文件内容
* 配合 `gzip`、`bzip2`、`xz`、`zstd` 等进行压缩

需要注意：

> `tar` 本身主要负责“打包/归档”，不是单纯的压缩工具。

例如：

```bash
tar -cf backup.tar test/
```

这里是把 `test/` 打包成 `backup.tar`，但并没有进行压缩。

而：

```bash
tar -czf backup.tar.gz test/
```

则是：

```text
tar 负责打包
gzip 负责压缩
```

所以可以简单理解为：

```text
多个文件
   ↓
tar 打包
   ↓
一个归档文件
   ↓
gzip / bzip2 / xz 等压缩
```

---

# 二、tar 命令基本格式

最常见的格式：

```bash
tar [选项] [归档文件] [文件或目录]
```

例如：

```bash
tar -cf backup.tar /home/user/
```

含义：

* `-c`：创建归档
* `-f`：指定归档文件名称
* `backup.tar`：生成的归档文件
* `/home/user/`：需要打包的目录

---

# 三、最重要的基本参数

## 1. `-c`：创建归档

`create`

用于创建新的 `.tar` 文件。

```bash
tar -cf test.tar file1.txt file2.txt
```

把两个文件打包成：

```text
test.tar
```

---

## 2. `-x`：解包

`extract`

用于提取归档文件。

```bash
tar -xf test.tar
```

把 `test.tar` 中的内容解压出来。

---

## 3. `-t`：查看归档内容

`list`

只查看，不解包。

```bash
tar -tf test.tar
```

例如：

```text
test/
test/a.txt
test/b.txt
test/config/
test/config/app.conf
```

这个参数在实际工作中非常常用。

例如拿到一个别人提供的压缩包时，可以先：

```bash
tar -tf backup.tar.gz
```

看看里面有什么，再决定是否解压。

---

## 4. `-f`：指定文件名

`file`

表示后面跟的是归档文件名。

例如：

```bash
tar -cf backup.tar test/
```

这里：

```text
-c  创建归档
-f  指定归档文件
backup.tar  归档文件名
```

### 注意

`-f` 后面通常紧跟文件名：

```bash
tar -cf backup.tar test/
```

不要写成：

```bash
tar -c backup.tar test/
```

因为这样 `tar` 对参数的理解就不同了。

---

# 四、压缩相关参数

tar 经常和不同压缩算法配合使用。

## 1. `-z`：gzip

对应：

```text
.gz
```

打包并 gzip 压缩：

```bash
tar -czf backup.tar.gz test/
```

解压：

```bash
tar -xzf backup.tar.gz
```

查看：

```bash
tar -tzf backup.tar.gz
```

---

## 2. `-j`：bzip2

对应：

```text
.bz2
```

打包：

```bash
tar -cjf backup.tar.bz2 test/
```

解压：

```bash
tar -xjf backup.tar.bz2
```

查看：

```bash
tar -tjf backup.tar.bz2
```

---

## 3. `-J`：xz

对应：

```text
.xz
```

打包：

```bash
tar -cJf backup.tar.xz test/
```

解压：

```bash
tar -xJf backup.tar.xz
```

查看：

```bash
tar -tJf backup.tar.xz
```

---

## 4. `--zstd`：zstd

现代 Linux 环境中也经常使用 Zstandard：

```bash
tar --zstd -cf backup.tar.zst test/
```

解压：

```bash
tar --zstd -xf backup.tar.zst
```

查看：

```bash
tar --zstd -tf backup.tar.zst
```

---

# 五、`-v`：显示详细过程

`verbose`

例如：

```bash
tar -cvf backup.tar test/
```

执行时会显示：

```text
test/
test/a.txt
test/b.txt
test/config/
test/config/app.conf
```

如果不加 `-v`：

```bash
tar -cf backup.tar test/
```

通常不会显示这些过程。

所以：

```bash
-v
```

可以理解为：

> “把操作过程显示出来”。

---

# 六、最常见的参数组合

学习 `tar` 时最重要的就是下面这些组合。

| 命令     | 含义            |
| ------ | ------------- |
| `-cf`  | 创建 `.tar` 归档  |
| `-xf`  | 解开 `.tar` 归档  |
| `-tf`  | 查看 `.tar` 内容  |
| `-czf` | 创建 `.tar.gz`  |
| `-xzf` | 解压 `.tar.gz`  |
| `-tzf` | 查看 `.tar.gz`  |
| `-cjf` | 创建 `.tar.bz2` |
| `-xjf` | 解压 `.tar.bz2` |
| `-cJf` | 创建 `.tar.xz`  |
| `-xJf` | 解压 `.tar.xz`  |
| `-cvf` | 创建并显示过程       |
| `-xvf` | 解包并显示过程       |

可以重点记住：

```text
c = create       创建
x = extract      解包
t = list         查看
v = verbose      显示详细过程
f = file         指定归档文件
z = gzip
j = bzip2
J = xz
```

---

# 七、文件打包

## 1. 打包一个文件

```bash
tar -cf file.tar test.txt
```

结果：

```text
test.txt
    ↓
file.tar
```

---

## 2. 打包多个文件

```bash
tar -cf files.tar a.txt b.txt c.txt
```

---

## 3. 打包整个目录

```bash
tar -cf project.tar project/
```

---

## 4. 同时打包文件和目录

```bash
tar -cf backup.tar a.txt b.txt project/
```

---

# 八、压缩打包

实际使用中更常见的是：

```bash
tar -czf backup.tar.gz project/
```

可以理解为：

```text
project/
   ↓
tar 打包
   ↓
gzip 压缩
   ↓
backup.tar.gz
```

---

# 九、解压文件

## 1. 解压 `.tar`

```bash
tar -xf backup.tar
```

---

## 2. 解压 `.tar.gz`

```bash
tar -xzf backup.tar.gz
```

---

## 3. 解压 `.tar.bz2`

```bash
tar -xjf backup.tar.bz2
```

---

## 4. 解压 `.tar.xz`

```bash
tar -xJf backup.tar.xz
```

---

# 十、解压到指定目录

使用：

```bash
-C
```

例如：

```bash
tar -xzf backup.tar.gz -C /opt/
```

表示：

> 把 `backup.tar.gz` 的内容解压到 `/opt/`。

例如：

```bash
tar -xf backup.tar -C /tmp/
```

---

# 十一、查看压缩包内容

这是非常推荐掌握的操作。

```bash
tar -tf backup.tar
```

或者：

```bash
tar -tzf backup.tar.gz
```

例如：

```bash
tar -tzf backup.tar.gz
```

可以先确认：

```text
backup/
backup/config/
backup/config/app.conf
backup/log/
backup/log/app.log
```

再进行解压。

---

# 十二、只解压指定文件

假设压缩包中有：

```text
backup/
backup/a.txt
backup/b.txt
backup/c.txt
```

只解压 `a.txt`：

```bash
tar -xf backup.tar backup/a.txt
```

也可以指定目录中的文件：

```bash
tar -xzf backup.tar.gz backup/config/app.conf
```

---

# 十三、排除某些文件

使用：

```bash
--exclude
```

例如：

```bash
tar -czf backup.tar.gz project/ --exclude=project/log/
```

表示：

> 打包 `project/`，但是排除 `project/log/`。

还可以排除指定类型：

```bash
tar -czf backup.tar.gz project/ --exclude='*.log'
```

表示：

> 不打包 `.log` 文件。

---

# 十四、多个文件排除

例如：

```bash
tar -czf backup.tar.gz project/ \
    --exclude='*.log' \
    --exclude='*.tmp'
```

表示排除：

```text
*.log
*.tmp
```

---

# 十五、使用 `-C` 改变打包目录

例如当前结构：

```text
/home/user/project/
├── code/
├── doc/
└── config/
```

可以：

```bash
tar -czf project.tar.gz -C /home/user project/
```

这里：

```text
-C /home/user
```

表示先进入 `/home/user`，然后打包：

```text
project/
```

这个参数在控制归档内部路径时很有用。

---

# 十六、修改已有 tar 文件

## 1. `-r`：追加文件

`append`

例如：

```bash
tar -rf backup.tar new.txt
```

表示向已有的 `backup.tar` 中添加：

```text
new.txt
```

注意：

> `-r` 主要用于普通 `.tar`，不能直接用于常见的 `.tar.gz`、`.tar.xz` 等压缩归档。

---

## 2. `-u`：更新文件

`update`

例如：

```bash
tar -uf backup.tar project/
```

作用是：

> 只有当源文件比归档中的文件更新时，才进行更新。

适合简单的增量更新场景。

---

# 十七、删除归档中的文件

可以使用：

```bash
tar --delete -f backup.tar test.txt
```

表示从 `backup.tar` 中删除：

```text
test.txt
```

注意：

> `--delete` 不能直接用于压缩归档，例如 `.tar.gz`。

---

# 十八、查看文件详细信息

可以使用：

```bash
tar -tvf backup.tar
```

例如：

```text
-rw-r--r-- user user  1024 2026-09-22 a.txt
-rwxr-xr-x user user  2048 2026-09-22 run.sh
```

能够看到：

* 文件权限
* 所有者
* 所属组
* 文件大小
* 修改时间
* 文件名称

---

# 十九、常见实际案例

## 案例 1：备份一个项目

```bash
tar -czf project_backup.tar.gz project/
```

---

## 案例 2：查看备份内容

```bash
tar -tzf project_backup.tar.gz
```

---

## 案例 3：恢复备份

```bash
tar -xzf project_backup.tar.gz
```

---

## 案例 4：恢复到指定目录

```bash
tar -xzf project_backup.tar.gz -C /backup/
```

---

## 案例 5：备份时排除日志

```bash
tar -czf project.tar.gz project/ --exclude='*.log'
```

---

## 案例 6：同时备份多个目录

```bash
tar -czf backup.tar.gz /etc/nginx /var/www /home/user
```

---

# 二十、tar 文件扩展名

常见的命名方式：

| 文件名        | 含义            |
| ---------- | ------------- |
| `.tar`     | tar 归档        |
| `.tar.gz`  | tar + gzip    |
| `.tgz`     | `.tar.gz` 的简写 |
| `.tar.bz2` | tar + bzip2   |
| `.tar.xz`  | tar + xz      |
| `.tar.zst` | tar + zstd    |

看到这些文件时，可以通过扩展名快速判断使用的压缩方式。

---

# 二十一、tar 的核心逻辑

建议使用下面这套方式记忆：

```text
创建       c
解包       x
查看       t

详细       v
文件       f

gzip       z
bzip2      j
xz         J
zstd       --zstd
```

例如：

```bash
tar -czvf backup.tar.gz project/
```

拆开来看：

```text
c → 创建
z → gzip 压缩
v → 显示过程
f → 指定文件名
```

所以：

```bash
tar -czvf backup.tar.gz project/
```

就是：

> 创建一个 gzip 压缩的 tar 文件，名称为 `backup.tar.gz`，把 `project/` 打包进去，并显示过程。

---

# 二十二、最实用的 8 条命令

刚开始学习时，可以先记住这 8 个：

### 1. 创建 tar

```bash
tar -cf backup.tar project/
```

### 2. 解开 tar

```bash
tar -xf backup.tar
```

### 3. 查看 tar

```bash
tar -tf backup.tar
```

### 4. 创建 tar.gz

```bash
tar -czf backup.tar.gz project/
```

### 5. 解压 tar.gz

```bash
tar -xzf backup.tar.gz
```

### 6. 查看 tar.gz

```bash
tar -tzf backup.tar.gz
```

### 7. 解压到指定目录

```bash
tar -xzf backup.tar.gz -C /tmp/
```

### 8. 排除文件

```bash
tar -czf backup.tar.gz project/ --exclude='*.log'
```

---

# 二十三、实际学习时的推荐记忆方法

不要一开始把所有参数全部死记下来。

先掌握：

```text
c = 创建
x = 解压
t = 查看
f = 文件
v = 详细
z = gzip
```

然后重点记住这三个核心命令：

```bash
tar -czf backup.tar.gz project/
```

```bash
tar -xzf backup.tar.gz
```

```bash
tar -tzf backup.tar.gz
```

也就是：

```text
创建
  ↓
tar -czf

解压
  ↓
tar -xzf

查看
  ↓
tar -tzf
```

这三个命令已经覆盖了日常绝大部分 `tar` 使用场景。

---

# 二十四、一句话总结

`tar` 最核心的用途就是：

> **把多个文件和目录归档成一个文件，并可以结合 gzip、bzip2、xz、zstd 等工具进行压缩。**

最重要的参数：

```text
-c  创建
-x  解包
-t  查看
-v  显示详细过程
-f  指定文件
-z  gzip
-j  bzip2
-J  xz
-C  指定目录
--exclude  排除文件
```

最常用命令：

```bash
tar -czf backup.tar.gz project/
tar -xzf backup.tar.gz
tar -tzf backup.tar.gz
```

这份笔记已经按“**概念 → 参数 → 命令 → 案例 → 实际记忆方法**”整理好了，后面学习 Linux 运维时可以直接当作 `tar` 速查笔记使用。
