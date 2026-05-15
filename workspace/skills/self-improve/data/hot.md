# HOT Rules（高频使用规则）

## 工具调用错误处理

### 错误1：dir_list 工具参数错误
- **错误描述**：多次尝试使用 dir_list 工具时，node 参数不正确
  - 尝试 node="auto" → 错误 "unknown node: auto"
  - 尝试 node="host" → 错误 "unknown node: host"
  - 尝试 node="sandbox" → 错误 "unknown node: sandbox"
  - 尝试 node="gateway" → 错误 "unknown node: gateway"
- **解决方法**：使用 exec 命令替代 dir_list 工具
- **来源**：会话 ID 891db4b7-1776-4a4c-879c-72a90112e387
- **建议**：当 dir_list 工具不可用时，优先使用 exec 命令进行目录操作

### 错误2：速率限制错误
- **错误描述**：出现 "429 您的账户已达到速率限制，请您控制请求频率"
- **解决方法**：等待一段时间后重试
- **来源**：会话 ID 09759429-8194-4c3f-9a1f-dfcacdc77d97
- **建议**：监控 API 调用频率，避免短时间内大量请求

### 错误3：LLM idle timeout
- **错误描述**：LLM idle timeout (120s): no response from model
- **解决方法**：切换模型或等待
- **来源**：会话 ID 425935e0-b5a9-461f-99cd-428682707ed0
- **建议**：当模型无响应时，考虑切换到备用模型

## 文件操作模式

### 模式1：批量检查目录内容
- **场景**：需要查看目录内容但工具不可用
- **方法**：使用 `ls -lt` 按时间排序查看
- **示例**：`ls -lt /root/.openclaw/agents/main/sessions/ | head -30`
- **来源**：会话 ID 891db4b7-1776-4a4c-879c-72a90112e387
