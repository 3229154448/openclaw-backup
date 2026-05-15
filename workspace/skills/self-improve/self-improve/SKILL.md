---
name: self-improve
description: A pluggable self-improvement framework for AI agents. Automatically learns from mistakes, corrections, and feedback to continuously improve execution quality. Runs every 3 days via Cron, extracts reusable experience rules, and proposes improvements to system files with approval workflow.
---

# Self-Improve Framework

A pluggable self-improvement framework for AI agents. Automatically learns from mistakes, corrections, and feedback to continuously improve execution quality.

## Description

Self-Improve enables your agent team to evolve over time:
- Scans agent memory logs for learning signals
- Extracts reusable experience rules
- **直接修改系统文件**（无需等待用户批准）
- 每次修改必须记录到变更日志 `data/changelog.md`
- Maintains a 3-tier memory system (HOT/WARM/COLD)

## ⚠️ 用户授权规则

用户已授权：自我改进循环可以直接修改系统文件（AGENTS.md、TOOLS.md、MEMORY.md、SOUL.md等），**无需等待批准**。

但必须：
1. 每次修改前记录到 `data/changelog.md`，包含：修改时间、修改文件、修改内容摘要、修改原因
2. 修改完成后同步推送到 GitHub 记忆仓库

### 🚫 需要用户批准的操作

**Gateway 重启**：任何涉及 `openclaw gateway restart` 或服务重启的操作，必须先用 message 工具通知用户并获得明确同意后才能执行。

## When to Use

- **Automatic (Cron)**: Runs every 3 days by default
- **Manual trigger**: When user asks to "run self-improve" or "learn and improve"
- **After significant events**: User can request immediate run after major corrections

## Installation

```bash
clawhub install self-improve
```

Or with OpenClaw CLI:
```bash
openclaw skills install self-improve
```

## Quick Start

### 1. Configure Paths

Edit user-config.yaml:

```yaml
storage:
  root: "/path/to/self-improve"
  knowledge_root: "/path/to/learned"
  workspace_root: "/path/to/.openclaw"

owner:
  name: "YourName"
  timezone: "Asia/Shanghai"
```

### 2. Run Setup

```bash
node scripts/setup.mjs --config user-config.yaml
```

### 3. Approve Cron Task

Check proposals/PENDING.md for the suggested Cron task.

## How It Works

```
Scan memory logs -> Extract signals -> Classify by theme
       |
Promote/demote rules between memory tiers
       |
Propose outputs:
  -> System file changes (needs approval)
  -> Knowledge base entries
  -> Blog drafts / methodologies
```

## Memory Tiers

| Tier | Location | Purpose |
|------|----------|---------|
| HOT | data/hot.md | Frequently used rules |
| WARM | data/themes/ | Theme-based rules |
| COLD | data/archive/ | Archived rules |

## Dependencies

- OpenClaw >= 2026.3.0
- Node.js >= 18.0.0

## License

MIT License