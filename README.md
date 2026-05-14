# Hermes-tieba-monitor-skill

通用百度贴吧监控 Skill for [Hermes Agent](https://github.com/nousresearch/hermes-agent)。

配合 `aiotieba` 库与 Hermes cronjob 使用，一个脚本通用于所有贴吧，自动抓取最新帖子并推送，支持配置关键词过滤垃圾信息。

## 依赖

- [aiotieba](https://github.com/yyuueexxiinngg/aiotieba) — 百度贴吧异步 API 库
  - PyPI: `pip install aiotieba`
  - GitHub: https://github.com/yyuueexxiinngg/aiotieba
- Python 3.13+
- [Hermes Agent](https://github.com/nousresearch/hermes-agent)

运行环境（已配置）：`/opt/data/hermes-aiotieba-venv`

## 文件结构

```
Hermes-tieba-monitor-skill/
├── SKILL.md                    # Skill 定义文件（触发词 + 工作流）
├── scripts/
│   └── tieba_monitor.py        # 通用监控脚本（所有贴吧共用）
└── README.md                   # 本文件
```

## 两种过滤模式

脚本支持两种相反的过滤模式：

| 模式 | 参数 | 语义 |
|------|------|------|
| **filterout** | `--filterout` | 标题含关键词 → 跳过（推送其余） |
| **filter** | `--filter` | 标题含关键词 → 推送（跳过其余） |

两种模式可以结合使用：`--filter 轮换 --filterout 收一个` = 只推送含"轮换"且不含"收一个"的帖子。

## 使用方法

### 1. 安装 Skill

```bash
# 通过 Git URL 安装
hermes skills add --git https://github.com/zzz6839/Hermes-tieba-monitor-skill

# 或本地路径
hermes skills add --local /path/to/Hermes-tieba-monitor-skill
```

### 2. 创建监控任务（示例）

```bash
# LOL台服吧，每天 8:00 推送（filterout 模式：过滤掉含关键词的帖子）
hermes cronjob create \
  --name "LOL台服贴吧监控" \
  --prompt "运行 python3 /opt/data/Hermes-tieba-monitor-skill/scripts/tieba_monitor.py --forum LOL台服 --filterout 收一个,私聊,收个" \
  --schedule "0 8 * * *" \
  --deliver origin \
  --no_agent true
```

### 3. 自定义关键词

**filterout 模式**（跳过含关键词的帖子）：
```bash
# 原神吧，过滤 收一个、收个、私聊
python3 scripts/tieba_monitor.py --forum 原神 --filterout 收一个,私聊,收个

# 台服LOL，过滤 轮换、换肤、收一个
python3 scripts/tieba_monitor.py --forum LOL台服 --filterout 轮换,换肤,收一个
```

**filter 模式**（只推送含关键词的帖子）：
```bash
# 只推送含"轮换"的帖子
python3 scripts/tieba_monitor.py --forum LOL台服 --filter 轮换

# 只推送含"轮换"或"换肤"的帖子
python3 scripts/tieba_monitor.py --forum LOL台服 --filter 轮换,换肤
```

**两者结合**：
```bash
# 只推送含"轮换"且不含"收一个"的帖子
python3 scripts/tieba_monitor.py --forum LOL台服 --filter 轮换 --filterout 收一个
```

### 4. 管理任务

```bash
hermes cron list           # 查看所有定时任务
hermes cron pause <job_id> # 暂停
hermes cron resume <job_id> # 恢复
hermes cron remove <job_id> # 删除
```

## 脚本参数

| 参数 | 说明 | 必填 |
|------|------|------|
| `--forum` | 贴吧名称（如 LOL台服、原神） | ✅ |
| `--filterout` | 过滤关键词，逗号分隔（标题含这些词→跳过） | ❌ |
| `--filter` | 筛选关键词，逗号分隔（标题含这些词→推送，不填则推送全部） | ❌ |
| `--cache` | 缓存文件路径（记录最新 tid） | ❌（默认 ~/.cron/state/tieba_\<forum\>_last_tid.txt） |

## License

MIT