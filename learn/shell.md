# Shell 笔记

## 2026-10-29 第一次

| 命令 | 我用它干了什么 |
|---|---|
| `pwd` | 确认自己在哪个目录 |
| `ls -Force` | 列文件，看见了隐藏的 `.git`——昨晚丢历史就因为它被漏掉 |
| `ls -Recurse -File` | 递归列出所有文件，含子目录 |
| `ls \| Sort-Object Length -Descending` | 按大小倒序排，找最大的文件 |
| `Select-String -Path README.md -Pattern "三条"` | 搜关键词，输出格式是 `文件:行号:内容` |
| `(ls -Recurse -Filter *.md).Count` | 数 md 文件个数，答案 16 |

## 今天学到的三件事

1. **`ls` 默认只看一层楼**，`-Recurse` 才会把子目录翻一遍。日志往往在子目录里，这条以后天天用。
2. **`ls -Force` 里 `d--h--` 的 `h` 是 hidden**。`.git` 就藏在这，移文件夹时最容易漏掉它——漏一次，历史全丢。
3. **别猜，去看**。我猜仓库有 13 个 md，实际 16 个。一个 `(ls ...).Count` 三秒出结果，比推断可靠。

## 待补

- [ ] 管道 `|` 串三个命令的写法还没练熟
- [ ] `Select-String` 的 `-Recurse` 用在整库搜索
