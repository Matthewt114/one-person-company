import csv
import os
from collections import Counter

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sales.csv")


def to_number(text):
    """'1,200' -> 1200.0；空字符串或非数字 -> None"""
    text = text.strip().replace(",", "")
    if text == "":
        return None
    try:
        return float(text)
    except ValueError:
        return None


with open(DATA, encoding="utf-8", newline="") as f:
    rows = list(csv.DictReader(f))

print(f"读了 {len(rows)} 行，列名：{list(rows[0].keys())}")
print()

columns = list(rows[0].keys())

for col in columns:
    values = [row[col] for row in rows]
    blanks = sum(1 for v in values if v == "")
    numbers = [n for n in (to_number(v) for v in values) if n is not None]

    if numbers and len(numbers) == len(values) - blanks:
        avg = sum(numbers) / len(numbers)
        distinct = len(set(numbers))
        print(f"{col}: 数字 {len(numbers)} 个，空 {blanks} 个，不同值 {distinct} 个，"
              f"最小 {min(numbers):g}，最大 {max(numbers):g}，平均 {avg:.2f}")
    else:
        counter = Counter(v for v in values if v != "")
        if counter:
            top_value, top_count = counter.most_common(1)[0]
            top_text = f"最常见「{top_value}」×{top_count}"
        else:
            top_text = "全空"
        print(f"{col}: 文本 {len(values) - blanks} 个非空，空 {blanks} 个，{top_text}")