# Hermes-tieba-monitor-skill

贴吧监控 Skill for [Hermes Agent](https://github.com/nousresearch/hermes-agent)。

配合 `aiotieba` 库与 Hermes cronjob 使用，自动抓取指定贴吧的最新帖子并推送，可配置 `filterout` 关键词过滤垃圾信息。

## 依赖

- [aiotieba](https://github.com/yyuueexxiinngg/aiotieba) — 百度贴吧异步 API 库
  - PyPI: `pip install aiotieba`
  - GitHub: https://github.com/yyuueexxiinngg/aiotieba
- Python 3.13+
- [Hermes Agent](https://github.com/nousresearch/hermes-agent)

## 使用方法

### 1. 安装 Skill

```bash
hermes skills add --local /path/to/tieba-monitor
# 或通过 Git URL
hermes skills add --git https://github.com/zzz6839/Hermes-tieba-monitor-skill
```

### 2. 创建监控任务

```bash
# 示例：创建 LOL台服吧 监控，每天 8:00 推送
hermes cronjob create \
  --name "LOL台服监控" \
  --prompt "监控百度贴吧 https://tieba.baidu.com/f?kw=LOL台服，筛选新帖，过滤关键词：收一个、收个、私聊，按格式推送：📌 {标题}\n🔗 {链接}" \
  --schedule "0 8 * * *" \
  --skills tieba-monitor \
  --script /opt/data/scripts/lol_taiwan_monitor.py
```

### 3. 自定义 filterout 关键词

编辑监控脚本中的 `FILTEROUT_KEYWORDS` 列表：

```python
FILTEROUT_KEYWORDS = [
    "收一个",
    "收个",
    "私聊",
    # 添加更多关键词...
]
```

## 文件结构

```
Hermes-tieba-monitor-skill/
├── SKILL.md          # Skill 定义文件
└── README.md         # 本文件
```

## License

MIT