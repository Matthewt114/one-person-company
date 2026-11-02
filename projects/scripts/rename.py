import argparse
import datetime
import os
import sys

ILLEGAL_CHARS = set('\\/:*?"<>|')
IMAGE_EXTS = (".jpg", ".png", ".jpeg")


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="批量重命名图片")
    parser.add_argument("folder", help="要处理的文件夹")
    parser.add_argument("prefix", nargs="?", default="photo", help="新文件名前缀，默认 photo")
    parser.add_argument("--by-date", action="store_true", help="按文件修改日期命名")
    parser.add_argument("--dry-run", action="store_true", help="只显示会怎么改，不真的改名")
    parser.add_argument("--verbose", action="store_true", help="打印更多过程信息")
    return parser.parse_args(argv)


def list_images(folder):
    """按修改时间排序，只返回图片文件名。不做任何修改。"""
    names = [n for n in os.listdir(folder) if n.lower().endswith(IMAGE_EXTS)]
    return sorted(names, key=lambda n: os.path.getmtime(os.path.join(folder, n)))


def build_plan(folder, names, prefix="photo", by_date=False):
    """算出 [(旧名, 新名), ...]。纯计算，不碰磁盘。"""
    plan = []
    for i, name in enumerate(names, start=1):
        ext = os.path.splitext(name)[1]
        if by_date:
            ts = os.path.getmtime(os.path.join(folder, name))
            date_part = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
            new_name = f"{date_part}-{i:03d}{ext}"
        else:
            new_name = f"{prefix}-{i:03d}{ext}"
        plan.append((name, new_name))
    return plan


def find_conflicts(folder, plan):
    """返回冲突说明列表。空列表表示可以安全执行。"""
    existing = {os.path.normcase(n): n for n in os.listdir(folder)}
    problems = []
    seen = {}
    for old, new in plan:
        k_old, k_new = os.path.normcase(old), os.path.normcase(new)
        if k_old == k_new:
            continue
        if k_new in existing and existing[k_new] != old:
            problems.append(f"「{old}」想改成 {new}，但这个名字已经被「{existing[k_new]}」占用")
        if k_new in seen:
            problems.append(f"「{old}」和「{seen[k_new]}」都算成了 {new}")
        seen[k_new] = old
    return problems


def apply_plan(folder, plan, dry_run=False, echo=print):
    """执行改名，返回 (改了, 跳过)。"""
    changed = 0
    skipped = 0
    for old, new in plan:
        if os.path.normcase(old) == os.path.normcase(new):
            skipped += 1
            continue

        old_path = os.path.join(folder, old)
        new_path = os.path.join(folder, new)

        if dry_run:
            echo(f"[演练] {old}  ->  {new}")
            changed += 1
            continue

        try:
            os.rename(old_path, new_path)
            echo(f"{old}  ->  {new}")
            changed += 1
        except PermissionError:
            echo(f"跳过（文件被占用，先关掉打开它的程序）：{old}")
            skipped += 1
        except OSError as e:
            echo(f"跳过（系统拒绝）：{old} —— {e}")
            skipped += 1
    return changed, skipped


def main(argv=None):
    args = parse_args(argv)

    # ① 目录必须存在
    if not os.path.isdir(args.folder):
        print(f"找不到文件夹：{args.folder}")
        return 1

    # ② 前缀里不能有文件名非法字符
    if not args.by_date:
        if not args.prefix:
            print("前缀不能为空。如果不想加前缀，用 --by-date。")
            return 1
        bad = ILLEGAL_CHARS & set(args.prefix)
        if bad:
            print("前缀里有不能用在文件名里的字符：" + " ".join(sorted(bad)))
            print('不能用的字符：\\ / : * ? " < > |')
            return 1

    if args.verbose:
        print(f"[verbose] 目录：{os.path.abspath(args.folder)}")
        print(f"[verbose] 命名方式：{'按修改日期' if args.by_date else '前缀 ' + args.prefix}")
        print("[verbose] 排序依据：文件修改时间")

    names = list_images(args.folder)
    print(f"{args.folder} 里有 {len(names)} 张图片")

    # ③ 先算后改
    plan = build_plan(args.folder, names, prefix=args.prefix, by_date=args.by_date)
    if args.verbose:
        print(f"[verbose] 算出 {len(plan)} 条改名计划")

    problems = find_conflicts(args.folder, plan)
    if problems:
        print("\n发现冲突，整个任务取消（一个文件都没有改动）：")
        for p in problems[:5]:
            print("  -", p)
        if len(problems) > 5:
            print(f"  …… 还有 {len(problems) - 5} 处")
        print("\n怎么办：换一个前缀，或者先把占用名字的文件挪走。")
        return 1

    # ④ 执行
    changed, skipped = apply_plan(args.folder, plan, dry_run=args.dry_run)
    print(f"\n完成：改了 {changed} 个，跳过 {skipped} 个")
    return 0


if __name__ == "__main__":
    sys.exit(main())
