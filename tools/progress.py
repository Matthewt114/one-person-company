# -*- coding: utf-8 -*-
"""三年进度条生成器。

数据来源全部是真实的：
  - 提交记录  ← git log
  - 里程碑    ← ROADMAP.md 里的 - [ ] / - [x]
  - 今天      ← 系统日期

用法：
  python progress.py
  python progress.py --repo "F:\\一人公司创业项目\\gihub本地仓库" --out "C:\\...\\进度图"
"""
import argparse
import os
import re
import subprocess
import sys
from datetime import date, datetime

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- 配置
GIT = r"C:\Program Files\Git\cmd\git.exe"

SEMESTERS = [
    ("大一上", date(2026, 9, 1), date(2027, 1, 15)),
    ("大一下", date(2027, 2, 20), date(2027, 7, 10)),
    ("大二上", date(2027, 9, 1), date(2028, 1, 15)),
    ("大二下", date(2028, 2, 20), date(2028, 7, 10)),
    ("大三上", date(2028, 9, 1), date(2029, 1, 15)),
    ("大三下", date(2029, 2, 20), date(2029, 6, 30)),
]

W, H = 1400, 900
MARGIN = 60

C_BG = (255, 255, 255)
C_INK = (0x1F, 0x38, 0x64)
C_MID = (0x2F, 0x54, 0x96)
C_SOFT = (0x2F, 0x54, 0x96)
C_LINE = (0xD6, 0xDE, 0xEB)
C_CARD = (0xF4, 0xF6, 0xFA)
C_TRACK = (0xE8, 0xEE, 0xF7)
C_GRAY = (0x62, 0x6B, 0x7A)
C_LIGHT = (0x9A, 0xA3, 0xB2)
C_OK = (0x2E, 0x7D, 0x5B)


def font(size, bold=False):
    p = r"C:\Windows\Fonts\msyhbd.ttc" if bold else r"C:\Windows\Fonts\msyh.ttc"
    return ImageFont.truetype(p, size)


def text_w(draw, s, f):
    box = draw.textbbox((0, 0), s, font=f)
    return box[2] - box[0]


def wrap(draw, s, f, max_w):
    lines, cur = [], ""
    for ch in s:
        if ch == "\n":
            lines.append(cur)
            cur = ""
            continue
        if text_w(draw, cur + ch, f) <= max_w:
            cur += ch
        elif ch in "）)，。、；：":
            lines.append(cur + ch)
            cur = ""
        else:
            lines.append(cur)
            cur = ch
    if cur:
        lines.append(cur)
    return lines


def read_commits(repo):
    out = subprocess.run(
        [GIT, "-C", repo, "log", "--pretty=format:%ad", "--date=short"],
        capture_output=True, text=True, encoding="utf-8",
    )
    days = [d.strip() for d in out.stdout.splitlines() if d.strip()]
    return days


def read_milestones(repo):
    path = os.path.join(repo, "ROADMAP.md")
    items = []
    if not os.path.exists(path):
        return items
    for line in open(path, encoding="utf-8"):
        m = re.match(r"^\s*-\s*\[( |x|X)\]\s+(.+?)\s*$", line)
        if m:
            items.append((m.group(1).lower() == "x", m.group(2)))
    return items


def streak_weeks(days):
    """最长连续周数（按 ISO 周）。"""
    if not days:
        return 0
    weeks = sorted({date.fromisoformat(d).isocalendar()[:2] for d in days})
    best = run = 1
    for i in range(1, len(weeks)):
        y0, w0 = weeks[i - 1]
        y1, w1 = weeks[i]
        n0 = date.fromisocalendar(y0, w0, 1)
        n1 = date.fromisocalendar(y1, w1, 1)
        if (n1 - n0).days == 7:
            run += 1
            best = max(best, run)
        else:
            run = 1
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=r"F:\一人公司创业项目\gihub本地仓库")
    ap.add_argument("--out", default=r"C:\Users\545\Documents\deepseek-harness\default-workspace\进度图")
    ap.add_argument("--today", default="", help="YYYY-MM-DD，默认今天")
    args = ap.parse_args()

    today = date.fromisoformat(args.today) if args.today else date.today()
    days = read_commits(args.repo)
    milestones = read_milestones(args.repo)
    done = sum(1 for ok, _ in milestones if ok)
    total = len(milestones) or 1

    plan_start = SEMESTERS[0][1]
    plan_end = SEMESTERS[-1][2]
    span = (plan_end - plan_start).days
    elapsed = max(0, min(span, (today - plan_start).days))
    pct = elapsed / span

    os.makedirs(args.out, exist_ok=True)
    img = Image.new("RGB", (W, H), C_BG)
    d = ImageDraw.Draw(img)

    # ---------- 标题
    d.text((MARGIN, 40), "一人公司 · 三年进度", font=font(34, True), fill=C_INK)
    sub = f"2026.09 → 2029.06   ·   第 {(today - plan_start).days + 1} 天   ·   更新于 {datetime.now():%Y-%m-%d %H:%M}"
    d.text((MARGIN, 92), sub, font=font(16), fill=C_GRAY)

    # ---------- 时间条
    d.text((MARGIN, 140), "时间进度", font=font(17, True), fill=C_MID)
    right = f"{pct*100:.0f}%"
    d.text((W - MARGIN - text_w(d, right, font(38, True)), 130), right,
           font=font(38, True), fill=C_INK)

    x0, x1 = MARGIN, W - MARGIN
    by, bh = 206, 40
    gap = 6
    seg_w = (x1 - x0 - gap * (len(SEMESTERS) - 1)) / len(SEMESTERS)

    for i, (name, sd, ed) in enumerate(SEMESTERS):
        sx = x0 + i * (seg_w + gap)
        d.rounded_rectangle([sx, by, sx + seg_w, by + bh], radius=9, fill=C_TRACK)
        s_span = (ed - sd).days
        if today >= ed:
            frac = 1.0
        elif today <= sd:
            frac = 0.0
        else:
            frac = (today - sd).days / s_span
        if frac > 0:
            d.rounded_rectangle([sx, by, sx + max(12, seg_w * frac), by + bh],
                                radius=9, fill=C_SOFT)
        # 标签
        cur = sd <= today <= ed
        f = font(16, True) if cur else font(15)
        col = C_INK if cur else (C_GRAY if today > ed else C_LIGHT)
        d.text((sx + seg_w / 2 - text_w(d, name, f) / 2, by + bh + 12), name, font=f, fill=col)

    # 今天标记
    tx = x0 + (x1 - x0) * pct
    d.line([(tx, by - 14), (tx, by + bh + 6)], fill=(0xC0, 0x39, 0x2B), width=3)
    d.text((tx + 8, by - 30), "今天", font=font(13, True), fill=(0xC0, 0x39, 0x2B))

    # ---------- 里程碑
    my = 320
    d.text((MARGIN, my), "里程碑", font=font(17, True), fill=C_MID)
    ms = f"{done}/{total} 完成"
    d.text((W - MARGIN - text_w(d, ms, font(17, True)), my), ms,
           font=font(17, True), fill=(C_OK if done else C_GRAY))

    cards_top = my + 42
    cols, cgap = 3, 20
    cw = (W - MARGIN * 2 - cgap * (cols - 1)) / cols
    ch = 96
    f_ms = font(14)
    for i, (ok, label) in enumerate(milestones):
        label = label.replace("`", "")
        r, c = divmod(i, cols)
        cx = MARGIN + c * (cw + cgap)
        cy = cards_top + r * (ch + 14)
        if ok:
            d.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=12, fill=C_OK)
            tc = (255, 255, 255)
        else:
            d.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=12, fill=C_CARD,
                                outline=C_LINE, width=1)
            tc = C_GRAY
        mark = "√" if ok else "○"
        d.text((cx + 16, cy + 14), mark, font=font(16, True), fill=tc)
        lines = wrap(d, label, f_ms, cw - 70)[:3]
        for j, ln in enumerate(lines):
            d.text((cx + 40, cy + 12 + j * 20), ln, font=f_ms, fill=tc)

    # ---------- 数字
    ny = cards_top + ((len(milestones) + cols - 1) // cols) * (ch + 14) + 34
    stats = [
        ("提交", str(len(days))),
        ("活跃天数", str(len(set(days)))),
        ("连续周", f"{streak_weeks(days)} 周"),
    ]
    sc, sgap = 3, 20
    sw = (W - MARGIN * 2 - sgap * (sc - 1)) / sc
    for i, (k, v) in enumerate(stats):
        sx = MARGIN + i * (sw + sgap)
        d.rounded_rectangle([sx, ny, sx + sw, ny + 104], radius=12, fill=C_CARD)
        d.text((sx + 24, ny + 20), v, font=font(32, True), fill=C_INK)
        d.text((sx + 24, ny + 64), k, font=font(15), fill=C_GRAY)

    d.text((MARGIN, H - 44),
           "数据来自 git 记录与 ROADMAP.md  ·  tools/progress.py 生成",
           font=font(13), fill=C_LIGHT)

    out = os.path.join(args.out, f"进度-{today.isoformat()}.png")
    img.save(out)

    print(f"图片: {out}")
    print(f"时间进度 : {pct*100:.1f}%  （第 {(today-plan_start).days+1} 天，共 {span+1} 天）")
    print(f"里程碑   : {done}/{total}")
    print(f"提交     : {len(days)}")
    print(f"活跃天数 : {len(set(days))}")
    print(f"连续周   : {streak_weeks(days)}")


if __name__ == "__main__":
    main()
