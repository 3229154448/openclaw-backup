# 心跳处理

## 问题概述

HEARTBEAT.md 为空时，仍然尝试读取不存在的 heartbeat-state.json，浪费时间且无必要。

## 错误模式

### 会话 425935e0 (2026-05-02)

**错误流程**:
1. 读取 HEARTBEAT.md → 返回空文件内容
2. 读取 heartbeat-state.json → 文件不存在，报错
3. 分析状态后返回 HEARTBEAT_OK

**代码**:
```javascript
read(HEARTBEAT.md);  // 返回空内容
read(heartbeat-state.json);  // ENOENT 错误
return "HEARTBEAT_OK";
```

## 正确做法

### 简化流程

**原则**: HEARTBEAT.md 为空 → 直接返回 HEARTBEAT_OK

```javascript
// ✅ 正确
function handleHeartbeat() {
  return "HEARTBEAT_OK";
}
```

**理由**:
1. HEARTBEAT.md 为空表示没有配置任何任务
2. heartbeat-state.json 不存在是正常的（第一次运行）
3. 不需要额外检查，直接返回即可

### 完整流程

```javascript
function handleHeartbeat() {
  // 1. 读取 HEARTBEAT.md
  const heartbeatContent = read(HEARTBEAT.md);

  // 2. 如果为空，直接返回
  if (!heartbeatContent || heartbeatContent.trim() === '') {
    return "HEARTBEAT_OK";
  }

  // 3. 否则检查是否有任务
  const tasks = parseTasks(heartbeatContent);
  if (tasks.length === 0) {
    return "HEARTBEAT_OK";
  }

  // 4. 处理任务
  return handleTasks(tasks);
}
```

## 最佳实践

### 1. 提前检查
```javascript
// 在读取之前检查文件是否存在
if (fs.existsSync(HEARTBEAT.md)) {
  const content = read(HEARTBEAT.md);
  // 处理内容
}
```

### 2. 默认返回
```javascript
// 默认行为
return "HEARTBEAT_OK";

// 只有明确需要处理时才检查
if (shouldCheckHeartbeat()) {
  // 检查
}
```

### 3. 简化状态管理
```javascript
// 不需要 heartbeat-state.json
// 只需要 HEARTBEAT.md 中的任务列表

// HEARTBEAT.md 格式
# 心跳任务
- 每日检查博客状态
- 每周备份数据库
```

## 影响评估

- **正面**: 减少不必要的文件读取和错误处理
- **负面**: 无
- **收益**: 每次心跳减少 1-2 次文件操作，提升响应速度

## 历史记录

- 425935e0: 尝试读取不存在的 heartbeat-state.json
- 425935e0: 多次心跳轮询，重复相同逻辑
