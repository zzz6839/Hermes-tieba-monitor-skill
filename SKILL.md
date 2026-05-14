---
name: tieba-monitor
description: 贴吧监控 — 定时抓取百度贴吧新帖子，有新帖推送、过滤关键词、静默无新帖。用于监控任意百度贴吧，当用户说"帮我监控XX贴吧"、"监控XX贴吧关键词"、"XX吧有新帖提醒我"、"定时抓取XX贴吧"时触发。配置后自动引用脚本并创建 cronjob，全自动无需人工介入。
version: 1.0.1
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
| `filterout_keywords` | 过滤关键词（标题含任意一个则跳过），用逗号分隔 | ❌（不填则不过滤） |
| `filter_keywords` | 筛选关键词（标题含任意一个才推送），用逗号分隔 | ❌（不填则推送全部） |
| `schedule` | Cron 表达式，默认 `37 10,22 * * *`（每天10:37和22:37） | ❌ |
| `delivery` | 推送目标，默认 `origin`（回到当前对话） | ❌ |

> **filterout 关键词参考（可自行替换）：** "收一个、收个、私聊" 等为示例，请根据实际监控的贴吧和用户需求灵活调整，勿直接照搬。

### 第二步：引用监控脚本

脚本已存在于仓库，使用时直接引用路径：

```
/opt/data/Hermes-tieba-monitor-skill/scripts/tieba_monitor.py
```

脚本接受以下参数：

| 参数 | 说明 |
|------|------|
| `--forum` | 贴吧名称（必填） |
| `--filterout` | 过滤关键词，逗号分隔（标题含这些词 → 跳过，不推送） |
| `--filter` | 筛选关键词，逗号分隔（标题含这些词 → 推送；其他跳过） |
| `--cache` | 缓存文件路径（可选，默认 ~/.cron/state/tieba_<forum>_last_tid.txt） |

> **两种模式区别：**
> - `--filterout K1,K2`：过滤模式，标题含任一关键词则跳过，推送其余帖子
> - `--filter K1,K2`：筛选模式，标题含任一关键词才推送，跳过其余帖子
> - 两者可结合使用：`--filter A --filterout B` 表示"只推含A且不含B的帖子"

示例命令（使用正确的 venv Python 路径）：

```bash
# filterout 模式：过滤掉含关键词的帖子，推送其余
/opt/data/hermes-aiotieba-venv/bin/python3 /opt/data/Hermes-tieba-monitor-skill/scripts/tieba_monitor.py --forum LOL台服 --filterout 收一个,私聊,收个

# filter 模式：只推送含关键词的帖子
/opt/data/hermes-aiotieba-venv/bin/python3 /opt/data/Hermes-tieba-monitor-skill/scripts/tieba_monitor.py --forum LOL台服 --filter 轮换,换肤

# 两者结合：只推送含"轮换"且不含"收一个"的帖子
/opt/data/hermes-aiotieba-venv/bin/python3 /opt/data/Hermes-tieba-monitor-skill/scripts/tieba_monitor.py --forum LOL台服 --filter 轮换 --filterout 收一个
```

### 第三步：创建 Cronjob

使用 `cronjob` 工具创建定时任务。**必须使用 venv 中的 Python 解释器路径**（否则找不到 aiotieba 库）：

| 字段 | 值 |
|------|------|
| **script** | `/opt/data/Hermes-tieba-monitor-skill/scripts/tieba_monitor.py` |
| **schedule** | 用户提供的 schedule，默认 `37 10,22 * * *` |
| **deliver** | `origin` |
| **no_agent** | `true` |
| **name** | `{forum_name}贴吧监控` |

> **关于 no_agent=false**：默认 `no_agent=true`（脚本直接输出结果，无需 agent 介入）。只有当用户要求复杂逻辑（如动态调整关键词、分析帖子内容）时才设为 `false`，并提供完整 prompt 模板：
> ```
> 运行 /opt/data/hermes-aiotieba-venv/bin/python3 /opt/data/Hermes-tieba-monitor-skill/scripts/tieba_monitor.py --forum {forum_name} --filterout {filterout_keywords} --filter {filter_keywords}
> 根据帖子内容判断是否相关，忽略广告和无关帖子，只推送真正有价值的內容。
> ```

### 第四步：确认

告诉用户：
- 脚本路径：`/opt/data/Hermes-tieba-monitor-skill/scripts/tieba_monitor.py`
- Python 解释器：`/opt/data/hermes-aiotieba-venv/bin/python3`
- cron 表达式及含义
- 已配置的过滤/筛选关键词（如有）
- job_id（用于后续管理）

## 验证

创建后手动运行一次验证：

```bash
hermes cron run <job_id>
```

确认：
- 新帖被正确推送
- 过滤关键词被正确跳过（标题含指定关键词的帖子没有出现）
- 筛选关键词正确生效（只有含指定关键词的帖子被推送）

## 错误处理

常见错误及处理方式：

| 错误现象 | 可能原因 | 处理方式 |
|----------|----------|----------|
| `ModuleNotFoundError: No module named 'aiotieba'` | 未使用 venv Python | 检查 script 路径是否为 `/opt/data/hermes-aiotieba-venv/bin/python3 .../tieba_monitor.py` |
| `UnicodeDecodeError` 或乱码 | 终端编码问题 | 设置 `PYTHONIOENCODING=utf-8` |
| 贴吧名找不到 / 0 帖返回 | 贴吧名输入错误 | 确认贴吧名完全匹配，如"LOL台服"而非"LOL" |
| 推送为空但实际有新帖 | 缓存文件权限或路径问题 | 检查 ~/.cron/state/ 目录是否存在、cron 执行用户是否有写权限 |

运行失败时，提示用户：`任务执行失败，请检查上述常见问题，或提供 job_id: <id> 让我帮你排查`。

## 管理命令

告诉用户：
- `hermes cron pause <job_id>` — 暂停
- `hermes cron resume <job_id>` — 恢复
- `hermes cron remove <job_id>` — 删除
- `hermes cron run <job_id>` — 手动触发一次

## 依赖

脚本依赖 `aiotieba` 库（百度贴吧异步 API 客户端）：
- PyPI: https://pypi.org/project/aiotieba/
- GitHub: https://github.com/yyuueexxiinngg/aiotieba

运行环境已有 venv：`/opt/data/hermes-aiotieba-venv`（Python 3.13，aiotieba 已安装）

> **重要**：cronjob 中必须使用 `/opt/data/hermes-aiotieba-venv/bin/python3` 调用脚本，不能用普通的 `python3`，否则 aiotieba 库找不到。