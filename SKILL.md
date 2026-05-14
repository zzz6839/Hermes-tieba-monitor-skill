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

通用贴吧监控 skill，配合 `scripts/tieba_monitor.py` 脚本工作。

## 何时使用

用户要求监控某个百度贴吧（新帖推送、关键词过滤）时使用。

## 工作流程

### 第一步：收集配置

向用户收集以下信息（已有明确信息的直接使用，不需要问）：

| 参数 | 说明 | 必填 |
|------|------|------|
| `forum_name` | 贴吧名（如 `LOL台服`、`原神`） | ✅ |
| `filterout_keywords` | 过滤关键词（标题含任意一个则跳过），用逗号分隔（可选，不填则不过滤） | ❌ |
| `filter_keywords` | 筛选关键词（标题含任意一个才推送），用逗号分隔（可选，不填则推送全部） | ❌ |
| `schedule` | Cron 表达式，默认 `37 10,22 * * *`（每天10:37和22:37） | ❌ |
| `delivery` | 推送目标，默认 `origin`（回到当前对话） | ❌ |

**filterout 关键词参考：**
- 收一个、收个、私聊

### 第二步：生成监控脚本

脚本已模板化，位于仓库 `scripts/tieba_monitor.py`，使用时直接引用：

```
Hermes-tieba-monitor-skill/scripts/tieba_monitor.py
```

脚本接受以下参数：

| 参数 | 说明 |
|------|------|
| `--forum` | 贴吧名称（必填） |
| `--filterout` | 过滤关键词，逗号分隔（标题含这些词→跳过） |
| `--filter` | 筛选关键词，逗号分隔（标题含这些词→推送，不填则推送全部） |
| `--cache` | 缓存文件路径（可选，默认 ~/.cron/state/tieba_<forum>_last_tid.txt） |

示例命令：
```bash
# filterout 模式：过滤掉含关键词的帖子，推送其余
python3 scripts/tieba_monitor.py --forum LOL台服 --filterout 收一个,私聊,收个

# filter 模式：只推送含关键词的帖子
python3 scripts/tieba_monitor.py --forum LOL台服 --filter 轮换,换肤

# 两者结合：只推送含"轮换"且不含"收一个"的帖子
python3 scripts/tieba_monitor.py --forum LOL台服 --filter 轮换 --filterout 收一个
```

### 第三步：创建 Cronjob

使用 `cronjob` 工具创建定时任务：

- **script**: `scripts/tieba_monitor.py`
- **prompt**（供 no_agent=false 时用）：
  ```
  运行 /opt/data/scripts/tieba_monitor.py --forum {forum_name} --filterout {filterout_keywords}
  ```
- **schedule**: 用户提供的 schedule，默认 `37 10,22 * * *`
- **deliver**: `origin`
- **no_agent**: `true`

job name 格式：`{forum_name}贴吧监控`

### 第四步：确认

告诉用户：
- 脚本路径：`Hermes-tieba-monitor-skill/scripts/tieba_monitor.py`
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