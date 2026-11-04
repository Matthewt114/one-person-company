import csv
import os
import sys
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


def summarize(path):
    """读 CSV，返回每一列的统计结果。只算，不打印。"""
    with open(path, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        return []

    report = []
    for col in rows[0].keys():
        values = [row[col] for row in rows]
        blanks = sum(1 for v in values if v == "")
        numbers = [n for n in (to_number(v) for v in values) if n is not None]

        item = {"column": col, "blanks": blanks, "total": len(values)}

        if numbers and len(numbers) == len(values) - blanks:
            item.update({
                "kind": "number",
                "count": len(numbers),
                "distinct": len(set(numbers)),
                "min": min(numbers),
                "max": max(numbers),
                "avg": sum(numbers) / len(numbers),
            })
        else:
            counter = Counter(v for v in values if v != "")
            item.update({
                "kind": "text",
                "count": len(values) - blanks,
                "top": counter.most_common(1)[0] if counter else None,
            })

        report.append(item)

    return report


def print_report(report):
    for item in report:
        col = item["column"]
        if item["kind"] == "number":
            print(f"{col}: 数字 {item['count']} 个，空 {item['blanks']} 个，"
                  f"不同值 {item['distinct']} 个，最小 {item['min']:g}，"
                  f"最大 {item['max']:g}，平均 {item['avg']:.2f}")
        else:
            top = item["top"]
            top_text = f"最常见「{top[0]}」×{top[1]}" if top else "全空"
            print(f"{col}: 文本 {item['count']} 个非空，空 {item['blanks']} 个，{top_text}")


def main():
    report = summarize(DATA)
    if not report:
        print(f"{DATA} 里没有数据行")
        return 1
    print(f"读了 {report[0]['total']} 行，列名：{[r['column'] for r in report]}")
    print()
    print_report(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
