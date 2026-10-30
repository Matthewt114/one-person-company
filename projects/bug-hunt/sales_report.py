# -*- coding: utf-8 -*-
"""销售报表汇总。

这是"客户"发来的原始版本——在他电脑上跑不起来，让你帮忙看看。
"""
import csv

DATA = r"D:\客户资料\销售数据\sales.csv"


def load(path):
    with open(path, "r") as f:
        return list(csv.DictReader(f))


def to_number(text):
    return int(text)


def main():
    rows = load(DATA)
    total = 0
    for r in rows:
        price = to_number(r["单价"])
        qty = to_number(r["数量"])
        total += price * qty
    print(f"总销售额：{total}")


if __name__ == "__main__":
    main()
