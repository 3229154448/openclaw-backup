# WARM 规则：Cron 任务管理

> 按主题分类的 cron 任务管理经验和最佳实践

## 任务配置

### 定时任务调试流程
**场景**：cron 任务执行失败或未按预期工作

**标准调试流程**：
1. **查看任务列表**：`cron(action="list")` - 检查任务是否启用、调度是否正确
2. **查看执行历史**：`cron(action="runs", jobId=...)` - 检查最近执行状态和错误
3. **检查会话日志**：`exec(command="cat sessions/...jsonl")` - 查看详细执行过程
4. **验证任务配置**：检查 payload、delivery、timeoutSeconds 等参数
5. **手动触发测试**：`cron(action="run", jobId=...)` - 验证修复是否生效

**常见问题**：
- 任务未投递：检查 delivery 配置
- 任务超时：增加 timeoutSeconds
- 任务失败：查看错误信息，检查 payload 是否正确

### 任务超时配置原则
**原则**：根据任务复杂度合理设置超时时间

| 任务类型 | 复杂度 | 推荐超时 | 模型选择 |
|---------|--------|---------|---------|
| 简单查询/搜索 | 低 | 60s | 任意 |
| 数据处理/转换 | 中 | 180s | glm-4.7-flash |
| 构建部署 | 高 | 900s | nvidia/z-ai/glm5 |
| 长时间计算 | 很高 | 1800s | nvidia/z-ai/glm5 |

**配置示例**：
```json
{
  "payload": {
    "kind": "agentTurn",
    "message": "任务描述",
    "model": "nvidia/z-ai/glm5",
    "timeoutSeconds": 900
  }
}
```

### delivery 配置指南

**后台任务（不需要推送结果）**：
```json
{
  "delivery": {
    "mode": "none"
  }
}
```

**需要推送结果的任务**：
```json
{
  "delivery": {
    "mode": "announce",
    "channel": "qqbot",
    "to": "qqbot:c2c:083093B7151A3F93C9D91136183DCF75",
    "accountId": "default"
  }
}
```

**注意事项**：
- delivery 配置必须与任务类型匹配
- 后台任务不要配置 delivery，避免投递失败
- 需要推送的任务必须提供正确的 channel 和 to 参数

## 常见任务类型

### 每日文章撰写任务

**任务描述**：为像素风博客撰写新文章并部署

**配置要点**：
```json
{
  "schedule": {
    "kind": "cron",
    "expr": "0 10 * * *",
    "tz": "Asia/Shanghai"
  },
  "payload": {
    "kind": "agentTurn",
    "message": "撰写文章并部署...",
    "model": "nvidia/z-ai/glm5",
    "timeoutSeconds": 900
  },
  "delivery": {
    "mode": "announce",
    "channel": "qqbot",
    "to": "qqbot:c2c:083093B7151A3F93C9D91136183DCF75",
    "accountId": "default"
  }
}
```

**常见问题**：
1. **超时**：构建部署耗时长，需要足够超时时间
2. **pnpm 不可用**：先检查并启用 corepack
3. **链式命令失败**：构建和推送分开执行

**修复案例**：
- 问题：deepseek-v3.2 模型慢，600s 超时不够
- 修复：换用 glm5 模型，超时增加到 900s
- 问题：pnpm 不可用
- 修复：执行 `corepack enable && corepack prepare pnpm@latest --activate`

### 记忆同步 GitHub 任务

**任务描述**：将工作区记忆同步到 GitHub 仓库

**配置要点**：
```json
{
  "schedule": {
    "kind": "cron",
    "expr": "0 */6 * * *",
    "tz": "Asia/Shanghai"
  },
  "payload": {
    "kind": "agentTurn",
    "message": "执行记忆同步到 GitHub...",
    "model": "nvidia/z-ai/glm5",
    "timeoutSeconds": 300
  },
  "delivery": {
    "mode": "none"
  }
}
```

**配置要点**：
- 使用 `mode: "none"`，因为是后台任务
- 脚本优先运行，失败时回退手动步骤
- 超时时间 300s 足够

**常见问题**：
1. **投递失败**：delivery 配置缺失或不正确
2. **脚本错误**：检查脚本权限和路径

**修复案例**：
- 问题：delivery 配置缺失，任务未投递
- 修复：添加 `delivery: { mode: "none" }`

### 每日早报任务

**任务描述**：生成每日早报（运势、天气、新闻等）

**配置要点**：
```json
{
  "schedule": {
    "kind": "cron",
    "expr": "0 7 * * *",
    "tz": "Asia/Shanghai"
  },
  "payload": {
    "kind": "agentTurn",
    "message": "生成每日早报...",
    "model": "nvidia/z-ai/glm5",
    "timeoutSeconds": 300
  },
  "delivery": {
    "mode": "announce",
    "channel": "qqbot",
    "to": "qqbot:c2c:083093B7151A3F93C9D91136183DCF75",
    "accountId": "default"
  }
}
```

**配置要点**：
- 使用 `web_search` 或 `web_fetch` 获取实时数据
- 格式化输出，严格按模板
- 必须通过搜索获取真实数据，不要编造

**常见问题**：
1. **数据不准确**：没有使用搜索，直接编造
2. **格式错误**：没有按模板输出

### 自我改进循环任务

**任务描述**：定期扫描会话日志，提取学习信号，改进系统

**配置要点**：
```json
{
  "schedule": {
    "kind": "cron",
    "expr": "0 4 */3 * *",
    "tz": "Asia/Shanghai"
  },
  "payload": {
    "kind": "agentTurn",
    "message": "执行 Self-Improve 自我改进循环...",
    "timeoutSeconds": 600
  },
  "delivery": {
    "mode": "none"
  }
}
```

**配置要点**：
- 扫描 `/root/.openclaw/agents/main/sessions/` 日志
- 提取学习信号：错误、纠正、工具失败、重复错误
- 分类存储到 hot.md、themes/ 目录
- 记录改进建议到 suggestions.md
- 不要直接修改系统文件

**常见问题**：
1. **编辑失败**：尝试直接编辑系统文件
2. **超时**：扫描日志和分类耗时较长

**修复案例**：
- 问题：尝试编辑 AGENTS.md 失败
- 修复：改为只记录建议到 suggestions.md

## 任务优化技巧

### 模型选择策略
- **快速响应**：glm-4.7-flash（适合简单查询）
- **稳定可靠**：nvidia/z-ai/glm5（适合复杂任务）
- **速度优先**：deepseek-v3.2（不推荐，响应慢）

### 超时设置策略
- **简单任务**：60-120s
- **中等任务**：180-300s
- **复杂任务**：600-900s
- **长时间任务**：1200-1800s

### 任务拆分策略
- 避免链式命令（可能导致一个失败全失败）
- 复杂任务拆分为多个步骤
- 使用脚本封装重复操作

### 错误处理策略
- 检查工具可用性
- 准备替代方案
- 记录错误和解决方案
- 定期回顾和优化

## 监控和告警

### 任务状态监控
- 使用 `cron(action="list")` 查看所有任务
- 使用 `cron(action="runs", jobId=...)` 查看执行历史
- 使用 `exec` 查看会话日志

### 异常检测
- 连续失败：检查配置和错误信息
- 超时频繁：增加超时时间或优化任务
- 未投递：检查 delivery 配置

### 定期维护
- 每周检查任务执行状态
- 每月审查和优化任务配置
- 定期更新学习规则和最佳实践
