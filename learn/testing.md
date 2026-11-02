# 测试笔记

## 2026-11-02 第一次写测试

### 一、为什么要有测试

改代码最怕的不是写错，是**写错了不知道**。

没有测试时：改完跑一下，看着没报错，提交。至于别的地方有没有被弄坏——不知道。

有测试时：改完跑一次，**绿的就说明还没弄坏**。这比“感觉对”可靠得多。

### 二、今天卡在哪：代码根本没法测

第一次尝试：

```powershell
python -c "import sys; sys.path.insert(0, 'projects/scripts'); import rename"
```

结果：

```
usage: -c [-h] [--by-date] [--dry-run] folder [prefix]
-c: error: the following arguments are required: folder
```

**一 import 它就开始解析命令行参数了。**

原因是所有代码都写在模块顶层，`import` 时从头执行一遍。它能不真的去改文件，纯粹是因为 `argparse` 先发现参数不够、直接退出——**不是安全，是还没来得及出事。**

修法两件事：

1. 把逻辑包进函数（`build_plan` / `find_conflicts` / `apply_plan`）
2. 加 `if __name__ == "__main__":` 守卫

改完再 import，**什么都不发生**。这时才有资格写测试。

> **能被测试的代码，必须先能被安全地导入。**

### 三、先红后绿

第一个测试（`test_build_plan_by_index`）写完直接绿了——因为功能早就写好了。

但一个**永远通过**的测试什么都没测。

所以第二个测试专门找一个还没实现的规则：**前缀不能为空**。

```python
def test_empty_prefix_rejected(tmp_path):
    assert rename.main([str(tmp_path), ""]) != 0
```

跑 → **红**：

```
assert 0 != 0
Captured stdout: ... 完成：改了 0 个，跳过 0 个
```

意思是：代码把“空前缀”当成正常情况，还打印了“完成”。

然后加 3 行代码让它变成非 0 → 再跑 → **绿**。

**红不是坏事，红说明测试真的在检查东西。**

### 四、三个测试各测什么

| 测试 | 测什么 |
|---|---|
| `test_build_plan_by_index` | 算新名字对不对（纯计算，不碰磁盘） |
| `test_empty_prefix_rejected` | 错误输入会被拒绝 |
| `test_find_conflicts_detects_occupied` | 目标名被占用时能发现 |

### 五、两个坑

**1. 缩进错误会让整个文件跑不起来**

```
IndentationError: expected an indented block after function definition on line 13
```

`def` 顶格，函数体必须比它多缩进（4 格）。

**2. VS Code 粘贴时自动继承缩进**

在缩进块末尾粘贴，新代码会自动带上前面的缩进，结果函数套函数。
修法：选中那几行按 `Shift + Tab` 反缩进。

### 六、一条规矩

> **提交前，跑一次测试。**

今天实际发生的事：代码改完了、测试写完了，**跳过 pytest 直接 commit + push**。

那次运气好，代码是对的。但习惯养坏了，下次改坏了也会照样提交。

```powershell
python -m pytest projects/scripts/test_rename.py -v
git add -A
git commit -m "..."
git push
```

### 七、还没做的

- [ ] 真正的 TDD：**先写测试、再写功能**（今天是先有功能、后补测试）
- [ ] 测试覆盖率：现在只测了三个点，`apply_plan` 还没测
- [ ] 测试失败时怎么快速定位（现在靠读 traceback）
