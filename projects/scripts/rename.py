import argparse
import os
import sys

parser = argparse.ArgumentParser(description="批量重命名图片")
parser.add_argument("folder", help="要处理的文件夹")
parser.add_argument("prefix", help="新文件名前缀，例如 photo")
args = parser.parse_args()

if not os.path.isdir(args.folder):
    print(f"找不到文件夹：{args.folder}")
    sys.exit(1)

files = sorted(os.listdir(args.folder))
print(f"{args.folder} 里有 {len(files)} 个东西")

count = 1
for name in files:
    if name.lower().endswith((".jpg", ".png", ".jpeg")):
        ext = os.path.splitext(name)[1]
        new_name = f"{args.prefix}-{count:03d}{ext}"
        old_path = os.path.join(args.folder, name)
        new_path = os.path.join(args.folder, new_name)
        os.rename(old_path, new_path)
        print(f"{name}  ->  {new_name}")
        count += 1