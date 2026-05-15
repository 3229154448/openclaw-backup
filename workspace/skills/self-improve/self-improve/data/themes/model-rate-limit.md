# 模型访问限制

## 问题概述

频繁遇到 429 错误，包括：
- "该模型当前访问量过大，请您稍后再试"
- "您的账户已达到速率限制，请您控制请求频率"
- "LLM idle timeout (120s): no response from model"

## 错误统计

从最近会话日志统计：
- **会话1**: 429 错误（模型访问量过大）
- **会话2**: 429 错误（速率限制）
- **会话3**: 429 错误（模型访问量过大）
- **会话4**: 429 错误（速率限制）
- **会话5**: 429 错误（模型访问量过大）
- **会话6**: 429 错误（速率限制）
- **会话7**: 429 错误（速率限制）
- **会话8**: 429 错误（模型访问量过大）
- **会话9**: 429 错误（速率限制）
- **会话10**: 429 错误（模型访问量过大）
- **会话11**: 429 错误（速率限制）
- **会话12**: 429 错误（速率限制）
- **会话13**: 429 错误（速率限制）
- **会话14**: 429 错误（速率限制）

## 错误模式

1. **重复尝试**: 每次遇到 429 都直接报错，不尝试降级
2. **无延迟**: 立即重试同一模型，无效
3. **无日志**: 不记录错误类型和计数
4. **任务中断**: 因为模型问题导致整个任务失败

## 解决方案

### 1. 自动降级策略
```javascript
async function safeGenerate(content) {
  const models = [
    { id: 'zhipu/glm-4.7-flash', fallback: 'z-ai/glm5' },
    { id: 'z-ai/glm5', fallback: null }
  ];

  for (const model of models) {
    try {
      return await callModel(model.id, content);
    } catch (error) {
      if (error.includes('429') && model.fallback) {
        console.log(`主模型 ${model.id} 受限，切换到 ${model.fallback}`);
        continue;
      }
      throw error;
    }
  }
  throw new Error('所有模型都不可用');
}
```

### 2. 增加延迟
```javascript
async function callModel(modelId, content) {
  const result = await call(modelId, content);
  // 成功后等待一段时间
  await sleep(1000); // 1秒延迟
  return result;
}
```

### 3. 错误日志
```javascript
// 记录错误类型
if (error.includes('429')) {
  logRateLimitError(modelId);
}
```

### 4. 备用方案
如果所有模型都失败，使用 exec 方式完成：
```javascript
try {
  return await model.generate(content);
} catch (error) {
  if (error.includes('429')) {
    // 使用 exec 方式
    return await execModelGeneration(content);
  }
}
```

## 预防措施

1. **批量处理**: 一次会话中减少模型调用次数
2. **缓存结果**: 相同内容避免重复调用
3. **监控频率**: 定期检查模型使用情况
4. **提前预警**: 当错误率超过阈值时提醒用户

## 影响评估

- **正面**: 提高系统稳定性
- **负面**: 增加复杂度
- **权衡**: 值得投入，因为 429 错误频繁发生
