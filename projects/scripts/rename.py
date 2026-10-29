import argparse
import datetime
import os
import sys

parser = argparse.ArgumentParser(description="批量重命名图片")
parser.add_argument("folder", help="要处理的文件夹")
parser.add_argument("prefix", nargs="?", default="photo", help="新文件名前缀，默认 photo")
parser.add_argument("--by-date", action="store_true", help="按文件修改日期命名")
parser.add_argument("--dry-run", action="store_true", help="只显示会怎么改，不真的改名")
args = parser.parse_args()

if not os.path.isdir(args.folder):
    print(f"找不到文件夹：{args.folder}")
    sys.exit(1)

files = sorted(
    os.listdir(args.folder),
    key=lambda n: os.path.getmtime(os.path.join(args.folder, n)),
)
print(f"{args.folder} 里有 {len(files)} 个东西")

count = 1
for name in files:
    if name.lower().endswith((".jpg", ".png", ".jpeg")):
        ext = os.path.splitext(name)[1]
        old_path = os.path.join(args.folder, name)

        if args.by_date:
            ts = os.path.getmtime(old_path)
            date_part = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
            new_name = f"{date_part}-{count:03d}{ext}"
        else:
            new_name = f"{args.prefix}-{count:03d}{ext}"

        new_path = os.path.join(args.folder, new_name)
        if args.dry_run:
            print(f"[演练] {name}  ->  {new_name}")
        else:
            os.rename(old_path, new_path)
            print(f"{name}  ->  {new_name}")
        count += 1