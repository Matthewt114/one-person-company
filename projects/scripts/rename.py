import os

TARGET = r"F:\一人公司创业项目\测试素材"

files = sorted(os.listdir(TARGET))
print(f"这个文件夹里有 {len(files)} 个东西")

count = 1
for name in files:
    if name.lower().endswith((".jpg", ".png", ".jpeg")):
        ext = os.path.splitext(name)[1]
        new_name = f"photo-{count:03d}{ext}"
        old_path = os.path.join(TARGET, name)
        new_path = os.path.join(TARGET, new_name)
        os.rename(old_path, new_path)
        print(f"{name}  ->  {new_name}  完成")
        count += 1