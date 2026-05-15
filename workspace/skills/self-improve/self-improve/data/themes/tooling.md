# WARM 规则：工具使用

> 按主题分类的工具使用经验和最佳实践

## 工具调用最佳实践

### 工具参数验证
**原则**：工具参数必须严格遵循文档定义，避免猜测

**常见错误**：
```javascript
// ❌ 错误：猜测参数值
dir_list({ node: "auto", path: "/some/path" }) // "auto" 不是有效值

// ❌ 错误：缺少必需参数
exec({ command: "ls -la" }) // 缺少 workdir

// ❌ 错误：参数类型错误
sessions_history({ limit: "10" }) // 应该是数字，不是字符串
```

**正确做法**：
```javascript
// ✅ 正确：使用文档定义的值
dir_list({ node: "sandbox", path: "/some/path" })

// ✅ 正确：提供所有必需参数
exec({ command: "ls -la", workdir: "/root/.openclaw/workspace-main" })

// ✅ 正确：使用正确的类型
sessions_history({ limit: 10, sessionKey: "..." })
```

### 工具错误处理
**原则**：每个工具调用都应该有错误处理策略

**标准错误处理流程**：
1. 检查工具是否可用（使用 `which`）
2. 验证参数是否正确
3. 使用 try-catch 或检查返回的错误
4. 提供备用方案

**示例**：
```javascript
// 检查工具可用性
const tool = which("pnpm");
if (!tool) {
  // 尝试备用方案
  corepack enable;
  corepack prepare pnpm@latest --activate;
}

// 验证参数
if (!path || !command) {
  throw new Error("参数不完整");
}

// 检查返回结果
const result = exec({ command });
if (result.status === "error") {
  // 处理错误
  console.error(result.error);
}
```

## exec 工具深度指南

### 后台任务管理
**场景**：执行长时间运行的任务（构建、部署、数据处理）

**标准流程**：
```javascript
// 1. 启动后台任务
const sessionId = exec({
  command: "pnpm build",
  workdir: "/root/.openclaw/workspace-main/pixel-astro-blog",
  background: true,
  yieldMs: 10000
}).sessionId;

// 2. 轮询结果
const result = process({
  action: "poll",
  sessionId: sessionId,
  timeout: 60000
});

// 3. 检查结果
if (result.status === "completed") {
  console.log("任务完成", result);
} else if (result.status === "failed") {
  console.error("任务失败", result.error);
}
```

**注意事项**：
- 使用 `background: true` 启动后台任务
- 使用 `yieldMs` 设置轮询间隔（10-30秒）
- 使用 `process(action="poll")` 轮询结果
- 使用 `timeout` 设置最大等待时间

### 链式命令 vs 分步执行
**原则**：避免链式命令，拆分为多个步骤

**错误示例**：
```javascript
// ❌ 链式命令：一个失败全失败
exec({
  command: "cd /root/.openclaw/workspace-main/pixel-astro-blog && pnpm build && git add . && git commit -m '...' && git push ..."
});
```

**正确示例**：
```javascript
// ✅ 分步执行：每个步骤独立验证
// 步骤1：构建
exec({ command: "cd /root/.openclaw/workspace-main/pixel-astro-blog && pnpm build" });

// 步骤2：提交
exec({ command: "cd /root/.openclaw/workspace-main/pixel-astro-blog && git add . && git commit -m '...'" });

// 步骤3：推送
exec({ command: "cd /root/.openclaw/workspace-main/pixel-astro-blog && git push ..." });
```

### 脚本封装
**原则**：重复操作使用脚本封装

**示例**：
```javascript
// 写入脚本
exec({
  command: "cat > /tmp/deploy.sh << 'EOF'\n#!/bin/bash\npnpm build\ngit add .\ngit commit -m 'Build'\ngit push\nEOF\nchmod +x /tmp/deploy.sh"
});

// 执行脚本
exec({ command: "bash /tmp/deploy.sh" });
```

## process 工具深度指南

### 轮询策略
**原则**：合理设置轮询间隔和超时

**推荐配置**：
```javascript
// 短任务（< 30s）
process({
  action: "poll",
  sessionId: sessionId,
  timeout: 30000
});

// 中等任务（30s-5min）
process({
  action: "poll",
  sessionId: sessionId,
  timeout: 300000,
  yieldMs: 10000 // 每10秒轮询一次
});

// 长任务（5min-30min）
process({
  action: "poll",
  sessionId: sessionId,
  timeout: 1800000,
  yieldMs: 30000 // 每30秒轮询一次
});
```

### 日志读取
**原则**：需要查看任务日志时使用 process(action="log")

**示例**：
```javascript
// 读取最后100行
const logs = process({
  action: "log",
  sessionId: sessionId,
  limit: 100,
  offset: 0
});

// 读取特定范围
const recentLogs = process({
  action: "log",
  sessionId: sessionId,
  limit: 50,
  offset: logs.length - 50
});
```

## sessions_history 工具

### 访问限制
**原则**：会话历史有访问权限限制

**限制**：
- 只能访问当前会话树中的会话
- 其他会话返回 `forbidden` 错误

**替代方案**：
1. 使用 `cron(action="runs", jobId=...)` 查看任务执行历史
2. 使用 `exec` 读取会话日志文件
3. 使用 `sessions_list` 列出可见会话

**示例**：
```javascript
// ❌ 会失败
sessions_history({ sessionKey: "other-session" });

// ✅ 使用 cron 查看任务历史
cron({ action: "runs", jobId: "job-id" });

// ✅ 读取日志文件
exec({ command: "cat /root/.openclaw/agents/main/sessions/session-id.jsonl" });
```

## file_fetch 和 file_write 工具

### 文件传输
**原则**：使用 file_fetch 和 file_write 进行文件传输

**流程**：
```javascript
// 1. 从节点获取文件
const file = file_fetch({
  node: "sandbox",
  path: "/root/.openclaw/workspace-main/MEMORY.md"
});

// 2. 写入到目标位置
file_write({
  node: "sandbox",
  path: "/root/.openclaw/workspace-main/backup/MEMORY.md",
  contentBase64: file.contentBase64,
  mimeType: file.mimeType
});
```

### 二进制文件处理
**原则**：使用 `sourceMediaId` 进行二进制文件复制

**示例**：
```javascript
// 1. 获取文件（返回 sourceMediaId）
const original = file_fetch({
  node: "sandbox",
  path: "/path/to/image.png"
});

// 2. 复制文件（使用 sourceMediaId）
file_write({
  node: "sandbox",
  path: "/path/to/backup/image.png",
  sourceMediaId: original.sourceMediaId
});
```

## web_search 和 web_fetch 工具

### 搜索策略
**原则**：使用 web_search 获取搜索结果，web_fetch 获取页面内容

**使用场景**：
- `web_search`：搜索关键词，获取标题和链接
- `web_fetch`：获取具体页面内容，提取结构化信息

**示例**：
```javascript
// 搜索
const results = web_search({
  query: "梅州市 天气",
  count: 5
});

// 获取页面
const page = web_fetch({
  url: "https://store.steampowered.com/specials",
  extractMode: "markdown"
});
```

### 错误处理
**原则**：检查工具返回的错误信息

**示例**：
```javascript
const result = web_search({ query: "invalid" });
if (result.error) {
  console.error("搜索失败:", result.error);
  // 提供备用方案
  return fallbackData;
}
```

## dir_list 工具

### 使用限制
**问题**：多次尝试使用 `dir_list` 工具时，node 参数配置错误

**错误示例**：
```javascript
// ❌ 无效的 node 值
dir_list({ node: "auto", path: "/some/path" }); // "auto" 不是有效值
dir_list({ node: "sandbox", path: "/some/path" }); // "sandbox" 不是有效值
dir_list({ node: "host", path: "/some/path" }); // "host" 不是有效值
```

**替代方案**：
```javascript
// ✅ 使用 exec
exec({ command: "ls -la /some/path" });

// ✅ 使用 file_fetch（如果需要文件内容）
file_fetch({ node: "sandbox", path: "/some/file.txt" });
```

## 最佳实践总结

### 工具选择原则
1. **优先使用专用工具**：file_fetch/write 用于文件操作，web_search/fetch 用于网络请求
2. **检查工具可用性**：执行前使用 `which` 检查
3. **验证参数正确性**：严格遵循文档定义
4. **处理错误**：检查返回值，提供备用方案

### 执行策略
1. **避免链式命令**：拆分为多个步骤
2. **使用后台任务**：长时间任务使用 background + poll
3. **合理设置超时**：根据任务复杂度设置
4. **封装重复操作**：使用脚本

### 调试技巧
1. **查看日志**：使用 process(action="log")
2. **检查状态**：使用 process(action="list") 或 cron(action="runs")
3. **读取文件**：使用 exec 或 file_fetch
4. **验证结果**：检查返回值和错误信息

### 错误处理
1. **检查工具可用性**：避免工具缺失
2. **验证参数**：避免参数错误
3. **处理错误**：捕获异常，提供备用方案
4. **记录日志**：记录错误和解决方案
