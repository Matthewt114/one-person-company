\# Shell 笔记



\## 2026-10-29 第一次



| 命令 | 我用它干了什么 |

|---|---|

| `pwd` | 确认自己在哪个目录 |

| `ls -Force` | 列文件，看见了隐藏的 `.git`——昨晚丢历史就因为它被漏掉 |

| `ls -Recurse -File` | 递归列出所有文件，含子目录 |

| `ls \\| Sort-Object Length -Descending` | 按大小倒序排，找最大的文件 |

| `Select-String -Path README.md -Pattern "三条"` | 搜关键词，输出格式是 `文件:行号:内容` |

| `(ls -Recurse -Filter \*.md).Count` | 数 md 文件个数，答案 16 |

