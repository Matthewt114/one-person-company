import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import csv_stat


def test_to_number_plain():
    """纯数字字符串"""
    assert csv_stat.to_number("89") == 89.0


def test_to_number_with_comma():
    """千分位要去掉逗号"""
    assert csv_stat.to_number("1,200") == 1200.0


def test_to_number_strips_space():
    """前后空格不算数"""
    assert csv_stat.to_number("  42  ") == 42.0


def test_to_number_empty():
    """空字符串不是数字，返回 None"""
    assert csv_stat.to_number("") is None


def test_to_number_text():
    """文本不是数字，返回 None"""
    assert csv_stat.to_number("笔记本") is None


def test_summarize_reads_columns(tmp_path):
    """整个统计流程：两列，一列数字一列文本"""
    csv_file = tmp_path / "t.csv"
    csv_file.write_text("a,b\n1,x\n2,y\n", encoding="utf-8")

    report = csv_stat.summarize(str(csv_file))

    assert [r["column"] for r in report] == ["a", "b"]
    assert report[0]["kind"] == "number"
    assert report[0]["avg"] == 1.5
    assert report[1]["kind"] == "text"
