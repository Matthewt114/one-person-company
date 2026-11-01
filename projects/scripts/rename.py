import argparse
import datetime
import os
import sys

ILLEGAL_CHARS = set('\\/:*?"<>|')
IMAGE_EXTS = (".jpg", ".png", ".jpeg")

parser = argparse.ArgumentParser(description="批量重命名图片")
parser.add_argument("folder", help="要处理的文件夹")
parser.add_argument("prefix", nargs="?", default="photo", help="新文件名前缀，默认 photo")
parser.add_argument("--by-date", action="store_true", help="按文件修改日期命名")
parser.add_argument("--dry-run", action="store_true", help="只显示会怎么改，不真的改名")
args = parser.parse_args()

# ① 目录必须存在
if not os.path.isdir(args.folder):
    print(f"找不到文件夹：{args.folder}")
    sys.exit(1)

# ② 前缀里不能有文件名非法字符
if not args.by_date:
    bad = ILLEGAL_CHARS & set(args.prefix)
    if bad:
        print("前缀里有不能用在文件名里的字符：" + " ".join(sorted(bad)))
        print('不能用的字符：\\ / : * ? " < > |')
        sys.exit(1)

files = sorted(
    os.listdir(args.folder),
    key=lambda n: os.path.getmtime(os.path.join(args.folder, n)),
)
print(f"{args.folder} 里有 {len(files)} 个东西")

# ---------- 第一阶段：只算，不动手 ----------
plan = []          # [(old_name, new_name), ...]
count = 1
for name in files:
    if not name.lower().endswith(IMAGE_EXTS):
        continue

    ext = os.path.splitext(name)[1]
    if args.by_date:
        ts = os.path.getmtime(os.path.join(args.folder, name))
        date_part = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
        new_name = f"{date_part}-{count:03d}{ext}"
    else:
        new_name = f"{args.prefix}-{count:03d}{ext}"

    plan.append((name, new_name))
    count += 1

# ---------- 第二阶段：全部校验，有冲突就整批取消 ----------
existing = {os.path.normcase(n): n for n in os.listdir(args.folder)}
problems = []
seen_target = {}

for old, new in plan:
    key_old, key_new = os.path.normcase(old), os.path.normcase(new)
    if key_new == key_old:
        continue                                  # 名字没变，不参与改名
    if key_new in existing and existing[key_new] != old:
        problems.append(f"「{old}」想改成 {new}，但这个名字已经被「{existing[key_new]}」占用")
    if key_new in seen_target:
        problems.append(f"「{old}」和「{seen_target[key_new]}」都算成了 {new}")
    seen_target[key_new] = old

if problems:
    print("\n发现冲突，整个任务取消（一个文件都没有改动）：")
    for p in problems[:5]:
        print("  -", p)
    if len(problems) > 5:
        print(f"  …… 还有 {len(problems) - 5} 处")
    print("\n怎么办：换一个前缀，或者先把占用名字的文件挪走。")
    sys.exit(1)

# ---------- 第三阶段：执行 ----------
changed = 0
skipped = 0

for old, new in plan:
    key_old, key_new = os.path.normcase(old), os.path.normcase(new)
    if key_new == key_old:
        skipped += 1
        continue

    old_path = os.path.join(args.folder, old)
    new_path = os.path.join(args.folder, new)

    if args.dry_run:
        print(f"[演练] {old}  ->  {new}")
        changed += 1
        continue

    # ③ 系统级错误变成人话
    try:
        os.rename(old_path, new_path)
        print(f"{old}  ->  {new}")
        changed += 1
    except PermissionError:
        print(f"跳过（文件被占用，先关掉打开它的程序）：{old}")
        skipped += 1
    except OSError as e:
        print(f"跳过（系统拒绝）：{old} —— {e}")
        skipped += 1

print(f"\n完成：改了 {changed} 个，跳过 {skipped} 个")
