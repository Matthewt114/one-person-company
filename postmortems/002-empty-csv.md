# 只有表头的 CSV 一跑就崩：`rows[0]` 没防空列表，以及它背后的思维盲区

## 元信息

| 项 | 内容 |
|---|---|
| 日期 | 2026-11-04 |
| 耗时 | 从起疑到修好，约 25 分钟 |
| 环境 | Windows / Python 3.12.10 / pytest 9.2.0 |
| 来源 | 自己写的 `csv_stat.py`，**读标准库源码时想到的** |
| 关键词 | `IndexError` `list index out of range` `DictReader` 空列表 边界条件 |

---

## 一、现象

`csv_stat.py` 是个读 CSV 输出每列统计的小工具。写完的第二天就出了这个 bug——而它在前一天跑得好好的。

那天我造了一个特殊的 CSV——**只有表头，没有数据行**：

```
商品,单价,数量,备注
```

跑 `summarize()`，直接崩：

```
Traceback (most recent call last):
  File "csv_stat.py", line 26, in summarize
    for col in rows[0].keys():
IndexError: list index out of range
```

**注意：这个 bug 不是我跑出来的，是我"想"出来的。**

---

## 二、排查思路

### 起点不是在修 bug，是在读源码

那天做的是另一件事：读 Python 标准库的 `csv.py`（451 行），想搞清楚"为什么我的 CSV 有 5 行数据，`DictReader` 只读出 4 行"。

读到 `DictReader.__next__` 这一段：

```python
row = next(self.reader)
...
while row == []:
    row = next(self.reader)
d = dict(zip(self.fieldnames, row))
lf = len(self.fieldnames)
lr = len(row)
if lf < lr:
    d[self.restkey] = row[lf:]
elif lf > lr:
    for key in self.fieldnames[lr:]:
        d[key] = self.restval
```

看到 `while row == []` 的时候，我突然想：

> **如果文件只有表头、一行数据都没有，`DictReader` 会返回什么？**

答案是：**空列表 `[]`**。

### 然后回看自己的代码

我的 `summarize()` 第一件事就是：

```python
rows = list(csv.DictReader(f))
...
for col in rows[0].keys():
```

**`rows` 可能是空的，但我在第一行就取了 `rows[0]`。**

### 验证而不是猜测

没有凭想象去改，而是**先写一个测试**：

```python
def test_summarize_empty_file(tmp_path):
    """只有表头、没有数据的 CSV，应该返回空列表，不是崩溃"""
    csv_file = tmp_path / "empty.csv"
    csv_file.write_text("a,b\n", encoding="utf-8")

    assert csv_stat.summarize(str(csv_file)) == []
```

跑 → 红。**测试精确复现了我想的那个假设。**

```
1 failed, 6 passed
E  IndexError: list index out of range
```

---

## 三、根因

`csv.DictReader` 在"只有表头、没有数据行"时返回**空列表**，这是它的正常行为，不是 bug。

问题在我的代码：**默认了"一定有数据"**。

```python
rows = list(...)      # 可能是 []
for col in rows[0]    # 直接取第一个，没检查
```

---

## 四、修法

```diff
     with open(path, encoding="utf-8", newline="") as f:
         rows = list(csv.DictReader(f))

+    if not rows:
+        return []
+
     report = []
     for col in rows[0].keys():
```

同时在 `main()` 里补上，否则打印那一层还会崩：

```diff
     report = summarize(DATA)
+    if not report:
+        print(f"{DATA} 里没有数据行")
+        return 1
+
     print(f"读了 {report[0]['total']} 行，列名：...")
```

**修了两层，因为崩点有两层。** 只修 `summarize()` 的话，`main()` 里的 `report[0]` 还是会炸。

---

## 五、验证

**A：先红后绿**

```
修之前： 1 failed, 6 passed
修之后： 7 passed
```

**B：确认没弄坏原有功能**

```
$ python csv_stat.py
读了 4 行，列名：['商品', '单价', '数量', '备注']
商品: 文本 4 个非空，空 0 个，最常见「笔记本」×1
...
```

输出和修复前一模一样。

**C：直接打空文件**

```python
>>> csv_stat.summarize("empty.csv")
[]
```

---

## 六、预防

### 1. 测试数据要包含"空"

我原来的测试数据是 `a,b\n1,x\n2,y\n`——**永远有数据**。所以三种边界（空文件、只有表头、全空值）一个都没覆盖到。

**教训：测试数据不能只造"正常情况"，还要造"什么都没有"。**

### 2. 函数第一行就下标访问，就要警惕

```python
rows[0]
items[0]
parts[0]
```

看到这种写法，问自己一句：**这个集合会不会是空的？**

### 3. 读别人的代码，重点看它怎么处理边界的

`DictReader` 里那句 `while row == []` 就是标准库作者在防边界。**我读到它，才想到自己的代码没防。**

> **别人踩过的坑写在代码里，你读到了，就等于自己也踩过一次——只是没付代价。**

---

## 一句话

这个 bug 没有从报错开始，是从"如果……会怎样"开始的。

**大部分线上事故不是不会写，是没想到那种情况会发生。**
