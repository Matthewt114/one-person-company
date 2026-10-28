# 把仓库发到 GitHub

> 目标：让 `one-person-company` 这个文件夹变成 `github.com/你的用户名/one-person-company`。
> 全程 4 条命令，不用配 SSH 密钥、不用生成 token。
> 适用：Windows + PowerShell（你的环境已确认 winget 可用）。

---

## 第 0 步：先确认你在哪

打开 PowerShell（开始菜单搜 "PowerShell"，**不要用 CMD**），然后：

```powershell
cd C:\Users\545\Documents\deepseek-harness\default-workspace
pwd
```

`pwd` 输出的应该是 `C:\Users\545\Documents\deepseek-harness\default-workspace`。
后面所有命令都在这个目录下执行。

---

## 第 1 步：装 Git 和 GitHub CLI

```powershell
winget install --id Git.Git -e --source winget
winget install --id GitHub.cli -e --source winget
```

- 可能会弹 UAC 授权框，点"是"。
- 装完**必须关掉 PowerShell 再重新开一个**，否则新装的命令找不到（PATH 要重新加载）。
- 重开后验证：

```powershell
git --version
gh --version
```

两条都能打印版本号，才算成功。

> 如果 winget 报错 `无法识别`，说明系统版本太旧，改用浏览器下载：
> Git → <https://git-scm.com/download/win>
> GitHub CLI → <https://cli.github.com/>

---

## 第 2 步：设置你的名字和邮箱

只做一次，以后不需要再设。

```powershell
git config --global user.name "你的拼音"
git config --global user.email "你的邮箱"
git config --global init.defaultBranch main
git config --global core.quotepath false
```

最后一条是给你这种中文文件名仓库准备的：不设的话，`git status` 里会把
`一人公司` 显示成 `\344\270\200\344\272\272...`，看着像乱码。

验证：

```powershell
git config --global --list
```

---

## 第 3 步：登录 GitHub

```powershell
gh auth login
```

它会依次问你四个问题，按这个选（用方向键选，回车确认）：

| 问题 | 选什么 |
|---|---|
| What account do you want to log into? | **GitHub.com** |
| What is your preferred protocol for Git operations? | **HTTPS** |
| Authenticate Git with your GitHub credentials? | **Yes** |
| How would you like to authenticate GitHub CLI? | **Login with a web browser** |

然后它会显示一个 **one-time code**（形如 `A1B2-C3D4`）：

1. 把这串码复制下来（或记住）
2. 按回车，浏览器会自动打开 GitHub 授权页
3. 粘贴那串码，点 **Authorize**
4. 回到 PowerShell，看到 `✓ Logged in as 你的用户名` 就成了

> 还没有 GitHub 账号？先去 <https://github.com/signup> 注册。
> **用户名用真名拼音**——以后要给客户和面试官看。

---

## 第 4 步：建仓库并推上去（一条命令）

```powershell
cd C:\Users\545\Documents\deepseek-harness\default-workspace\one-person-company
gh repo create one-person-company --public --source=. --remote=origin --push
```

这一条命令做了四件事：在 GitHub 上建仓库 → 把本地目录和它关联 → 推送 → 自动设好分支。

看到类似 `✓ Created repository 你的用户名/one-person-company` 就成功了。

如果你想把仓库改成别的名字，把命令里的两个 `one-person-company` 换成你要的名字
（第二个是本地目录名，不用改）。

---

## 第 5 步：验证，然后做第一次修改

```powershell
gh repo view --web
```

浏览器会打开你的仓库页面。应该能看到 README 渲染出来的样子、17 个文件、1 次 commit。

**接着做一次真实修改**，把"推送"练成肌肉记忆：

1. 用 VS Code 打开 `README.md`
2. 把第一行的名字改成你的真名
3. 回到 PowerShell：

```powershell
git add -A
git commit -m "改了自己的名字"
git push
```

刷新网页，看到 2 次 commit —— 到这里，这条路你就彻底跑通了。

---

## 日常三件套

以后每次改完东西，都是这三条：

```powershell
git add -A
git commit -m "说清楚这次改了什么"
git push
```

**commit message 的写法**：写"做了什么"，不写"更新"。
- 好：`第 1 周：装好环境，写完 hello.py`
- 差：`update`

三个月后你会感谢自己——`git log` 就是你的工作日志。

---

## 出错了看这里

| 报错 | 原因 | 怎么办 |
|---|---|---|
| `git : 无法将"git"项识别为...` | 装完没重开终端，PATH 没加载 | 关掉 PowerShell 重开一个 |
| `fatal: not a git repository` | 当前目录不是仓库 | `pwd` 看路径，`cd` 到 `one-person-company` |
| `remote: Support for password authentication was removed` | 输了 GitHub 密码 | 改用 `gh auth login`（本指南的方式） |
| `Permission denied (publickey)` | 走了 SSH 但没配密钥 | 重跑 `gh auth login`，选 **HTTPS** |
| `error: src refspec main does not match any` | 还没有任何 commit | 先 `git add -A` + `git commit`，再 push |
| `git status` 里中文变 `\344\270\200...` | 没设 quotepath | `git config --global core.quotepath false` |
| 推送卡住 / 超时 | 国内网络到 GitHub 不稳 | 换个网络重试；或开了代理后设 `git config --global http.proxy http://127.0.0.1:端口` |
| `repository not found` | 用户名拼错，或仓库名写错 | `git remote -v` 看看，`git remote set-url origin 正确地址` |

---

## 一条底线

**永远不要把密钥提交上去。** 仓库里的 `.gitignore` 已经排除了
`.env`、`*.pem`、`*.key`、`secrets.json`。
但只要你不确定，推之前跑一次：

```powershell
git status
```

看清楚里面有没有你不该公开的东西。推到 GitHub 上的东西，就算删了，历史里还在。
