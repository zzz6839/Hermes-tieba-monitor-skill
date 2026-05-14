#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
贴吧通用监控脚本 — Universal Tieba Monitor
配合 aiotieba 库使用，通过 cronjob 定时抓取任意百度贴吧新帖。

用法：
    python3 tieba_monitor.py --forum <吧名> --filter <关键词1,关键词2,...>

示例：
    python3 tieba_monitor.py --forum LOL台服 --filter 收一个,私聊,收个
    python3 tieba_monitor.py --forum 原神 --filter 收一个,私聊

依赖：
    pip install aiotieba
    GitHub: https://github.com/yyuueexxiinngg/aiotieba
    PyPI:   https://pypi.org/project/aiotieba/

运行环境（已配置）：
    /opt/data/hermes-aiotieba-venv
"""

import argparse
import asyncio
import os
import sys

# ── venv site-packages 路径（兼容独立运行）────────────────────────
_VENV_SITE = "/opt/data/hermes-aiotieba-venv/lib/python3.13/site-packages"
if _VENV_SITE not in sys.path:
    sys.path.insert(0, _VENV_SITE)

# ── CLI 参数解析 ──────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="贴吧通用监控脚本")
parser.add_argument("--forum",  required=True, help="贴吧名称（如 LOL台服、原神）")
parser.add_argument("--filter", default="",     help="过滤关键词，逗号分隔（如 收一个,私聊）")
parser.add_argument("--cache",  default="",     help="缓存文件路径（默认：~/.cron/state/tieba_<forum>_last_tid.txt）")
args = parser.parse_args()

FORUM_NAME = args.forum.strip()
FILTEROUT_KEYWORDS = [kw.strip() for kw in args.filter.split(",") if kw.strip()]

CACHE_FILE = args.cache or os.path.expanduser(f"~/.cron/state/tieba_{FORUM_NAME}_last_tid.txt")

# ── 过滤函数 ─────────────────────────────────────────────────────
def is_filtered(title: str) -> bool:
    for kw in FILTEROUT_KEYWORDS:
        if kw in title:
            return True
    return False

# ── 缓存读写 ─────────────────────────────────────────────────────
def load_last_tid() -> int | None:
    try:
        with open(CACHE_FILE, "r") as f:
            content = f.read().strip()
            return int(content) if content else None
    except (FileNotFoundError, ValueError):
        return None

def save_last_tid(tid: int):
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        f.write(str(tid))

# ── 格式化输出 ───────────────────────────────────────────────────
def format_post(thread) -> str:
    title = thread.text[:60].replace("\n", " ").strip() if thread.text else "(无标题)"
    url   = f"https://tieba.baidu.com/p/{thread.tid}"
    return f"📌 {title}\n🔗 {url}"

# ── 主逻辑 ───────────────────────────────────────────────────────
async def main():
    last_tid = load_last_tid()

    try:
        import aiotieba
        async with aiotieba.Client() as client:
            threads = await client.get_threads(
                FORUM_NAME,
                pn=1,
                rn=20,
                sort=aiotieba.ThreadSortType.CREATE,
            )
            thread_list = list(threads)
    except Exception as e:
        print(f"API_ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        import gc; gc.collect()

    # 过滤置顶帖/精品帖
    new_threads = [t for t in thread_list if not t.is_top and not t.is_good]
    if not new_threads:
        return

    latest_tid = new_threads[0].tid

    # 首次运行：只记录最新 tid，不推送
    if last_tid is None:
        save_last_tid(latest_tid)
        return

    # 筛选新帖
    new_posts = [t for t in new_threads if t.tid > last_tid]
    if not new_posts:
        return

    # 按 filterout 关键词过滤
    filtered_posts = [t for t in new_posts if not is_filtered(t.text or "")]
    if not filtered_posts:
        return

    for t in filtered_posts:
        print(format_post(t))

    save_last_tid(latest_tid)

if __name__ == "__main__":
    asyncio.run(main())