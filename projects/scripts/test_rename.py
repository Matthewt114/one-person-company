import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import rename


def test_build_plan_by_index():
    """a.jpg -> trip-001.jpg，b.jpg -> trip-002.jpg"""
    plan = rename.build_plan("任意目录", ["a.jpg", "b.jpg"], prefix="trip")
    assert plan == [("a.jpg", "trip-001.jpg"), ("b.jpg", "trip-002.jpg")]
def test_empty_prefix_rejected(tmp_path):
    """空前缀会生成 '-001.jpg' 这种怪名字，应该直接拒绝"""
    assert rename.main([str(tmp_path), ""]) != 0