---
name: tieba-monitor
description: 贴吧监控 — 定时抓取百度贴吧新帖子，有新帖推送、过滤关键词、静默无新帖。用于监控任意百度贴吧，当用户说"帮我监控XX贴吧"、"监控XX贴吧关键词"时触发。配置后自动生成脚本并创建 cronjob，全自动无需人工介入。
version: 1.0.0
metadata:
  hermes:
    tags: [tieba, cron, monitoring, baidu]
    category: monitoring
---

# 贴吧监控 (Tieba Monitor)

## 何时使用
用户要求监控某个百度贴吧（新帖推送、关键词过滤）时使用。

## 工作流程

### 第一步：收集配置

向用户收集以下信息（已有明确信息的直接使用，不需要问）：

| 参数 | 说明 | 必填 |
|------|------|------|
| `forum_name` | 贴吧名（如 `LOL台服`、`原神`） | ✅ |
| `filterout_keywords` | 过滤关键词列表（标题含任意一个则跳过），用逗号分隔 | ✅ |
| `schedule` | Cron 表达式，默认 `37 10,22 * * *`（每天10:37和22:37） | ❌ |
| `delivery` | 推送目标，默认 `origin`（回到当前对话） | ❌ |

**filterout 关键词参考：**
- 收一个、收个、私聊

### 第二步：生成监控脚本

在 `/opt/data/scripts/` 目录下创建 `tieba_<forum_name>.py`：

```python
#!/opt/data/hermes-aiotieba-venv/bin/python3
# -*- coding: utf-8 -*-
"""
{forum_name} 贴吧监控
"""

import asyncio, os, sys

_venv_site = "/opt/data/hermes-aiotieba-venv/lib/python3.13/site-packages"
if _venv_site not in sys.path:
    sys.path.insert(0, _venv_site)

CACHE_FILE = "/opt/data/./cron/state/tieba_{forum_name}_last_tid.txt"

FILTEROUT_KEYWORDS = [
{items}
]

def is_filtered(title: str) -> bool:
    for kw in FILTEROUT_KEYWORDS:
        if kw in title:
            return True
    return False

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

def format_post(thread) -> str:
    title = thread.text[:60].replace("\n", " ").strip() if thread.text else "(无标题)"
    url = f"https://tieba.baidu.com/p/{thread.tid}"
    return f"📌 {title}\n🔗 {url}"

async def main():
    last_tid = load_last_tid()

    try:
        import aiotieba
        async with aiotieba.Client() as client:
            threads = await client.get_threads(
                "{forum_name}",
                pn=1,
                rn=20,
                sort=aiotieba.ThreadSortType.CREATE,
            )
            thread_list = list(threads)
    except Exception as e:
        print(f"API_ERROR: {{e}}", file=sys.stderr)
        sys.exit(1)
    finally:
        import gc; gc.collect()

    new_threads = [t for t in thread_list if not t.is_top and not t.is_good]
    if not new_threads:
        return

    latest_tid = new_threads[0].tid
    if last_tid is None:
        save_last_tid(latest_tid)
        return

    new_posts = [t for t in new_threads if t.tid > last_tid]
    if not new_posts:
        return

    filtered_posts = [t for t in new_posts if not is_filtered(t.text or "")]
    if not filtered_posts:
        return

    for t in filtered_posts:
        print(format_post(t))

    save_last_tid(latest_tid)

if __name__ == "__main__":
    asyncio.run(main())
```

### 第三步：创建 Cronjob

使用 `cronjob` 工具创建定时任务：

- **script**: `tieba_{forum_name}.py`（路径相对于 `~/./scripts/`）
- **schedule**: 用户提供的 schedule，默认 `37 10,22 * * *`
- **deliver**: `origin`
- **no_agent**: `true`

job name 格式：`{forum_name}贴吧监控`

### 第四步：确认

告诉用户：
- 脚本路径：`/opt/data/scripts/tieba_{forum_name}.py`
- cron 表达式及含义
- 已配置的过滤关键词数量
- job_id（用于后续管理）

## 验证

创建后手动运行一次验证：
```bash
hermes cron run <job_id>
```
确认新帖被正确推送、过滤关键词被正确跳过。

## 管理命令

告诉用户如何管理：
- `hermes cron pause <job_id>` — 暂停
- `hermes cron resume <job_id>` — 恢复
- `hermes cron remove <job_id>` — 删除

## 依赖

脚本依赖 `aiotieba` 库（百度贴吧异步 API 客户端）：
- PyPI: https://pypi.org/project/aiotieba/
- GitHub: https://github.com/yyuueexxiinngg/aiotieba

运行环境已有：`/opt/data/hermes-aiotieba-venv`