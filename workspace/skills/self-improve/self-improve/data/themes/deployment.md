# WARM 规则：部署和发布

> 按主题分类的部署和发布经验和最佳实践

## 部署流程标准

### GitHub Pages 部署流程

**完整流程**：
```bash
# 1. 构建
cd /root/.openclaw/workspace-main/pixel-astro-blog
pnpm build

# 2. 提交
git add .
git commit -m "📝 新文章: [文章标题]"

# 3. 推送
git push https://3229154448:ghp_TOKEN@github.com/3229154448/pixel-astro-blog.git main

# 4. 验证
node -e "fetch('https://3229154448.github.io/pixel-astro-blog/').then(r => console.log('Status:', r.status))"
```

**注意事项**：
- 构建和推送分开执行
- 使用正确的 token 认证
- 推送后验证部署状态

### 部署验证策略

**验证方式**：
```javascript
// 方式1：HTTP 状态码
node -e "fetch('https://site-url').then(r => console.log(r.status))"

// 方式2：页面内容检查
node -e "fetch('https://site-url').then(r => r.text()).then(t => console.log(t.includes('Expected Content')))"
```

**验证内容**：
- HTTP 状态码（200）
- 关键内容是否存在
- 页面加载正常

## 认证和授权

### Git 认证方式

**方式1：URL 中包含 token**
```bash
git push https://user:token@github.com/repo.git main
```

**方式2：使用环境变量**
```bash
# 配置 credential helper
git config --global credential.helper store

# 推送（会提示输入用户名和密码）
git push https://github.com/repo.git main
```

**方式3：使用 personal access token**
```bash
# 创建 token
# Settings -> Developer settings -> Personal access tokens -> Tokens (classic)

# 使用 token
git push https://3229154448:ghp_TOKEN@github.com/repo.git main
```

### Token 安全

**最佳实践**：
1. 不要在脚本中硬编码 token（使用环境变量）
2. 定期更新 token
3. 使用最小权限原则
4. 限制 token 使用范围

**错误示例**：
```bash
# ❌ 不安全：在脚本中硬编码 token
git push https://3229154448:ghp_LONG_TOKEN_HERE@github.com/repo.git main
```

**正确示例**：
```bash
# ✅ 安全：使用环境变量
export GITHUB_TOKEN="ghp_TOKEN"
git push https://github.com/repo.git main
```

## 构建工具

### pnpm 管理

**启用 pnpm**：
```bash
# 1. 启用 corepack
corepack enable

# 2. 准备 pnpm
corepack prepare pnpm@latest --activate

# 3. 验证
which pnpm && pnpm --version
```

**常见问题**：
- pnpm 不可用：执行 corepack enable
- 版本不匹配：重新准备特定版本

### 构建优化

**优化策略**：
1. **缓存依赖**：pnpm-lock.yaml 已包含
2. **并行构建**：Astro 支持并行
3. **增量构建**：只构建变更文件
4. **压缩优化**：使用 @playform/compress 插件

**构建命令**：
```bash
# 完整构建
pnpm build

# 开发模式
pnpm dev

# 清理构建
pnpm clean
```

## 部署检查清单

### 部署前检查
- [ ] 确认 git 状态（无未提交变更）
- [ ] 确认 pnpm 可用
- [ ] 确认构建成功
- [ ] 确认 token 有效
- [ ] 确认推送目标正确

### 部署中检查
- [ ] 构建无错误
- [ ] git commit 成功
- [ ] git push 成功
- [ ] 部署脚本执行成功

### 部署后检查
- [ ] HTTP 状态码为 200
- [ ] 关键内容存在
- [ ] 页面加载正常
- [ ] 无 404 错误

## 常见问题

### 构建失败

**问题1：pnpm 不可用**
```bash
# 解决方案
corepack enable && corepack prepare pnpm@latest --activate
```

**问题2：依赖安装失败**
```bash
# 解决方案
rm pnpm-lock.yaml
pnpm install
pnpm build
```

**问题3：构建超时**
```bash
# 解决方案
# 1. 检查依赖版本
# 2. 增加超时时间
# 3. 优化构建配置
```

### 推送失败

**问题1：认证失败**
```bash
# 解决方案
# 1. 检查 token 是否有效
# 2. 检查 token 权限
# 3. 重新生成 token
```

**问题2：推送被拒绝**
```bash
# 解决方案
# 1. 检查分支名称
# 2. 检查远程仓库权限
# 3. 检查提交信息格式
```

**问题3：网络超时**
```bash
# 解决方案
# 1. 检查网络连接
# 2. 增加超时时间
# 3. 使用代理（如果需要）
```

### 部署验证失败

**问题1：HTTP 状态码非 200**
```bash
# 解决方案
# 1. 检查 GitHub Pages 配置
# 2. 检查构建输出
# 3. 检查远程仓库设置
```

**问题2：内容缺失**
```bash
# 解决方案
# 1. 检查构建输出目录
# 2. 检查文件路径
# 3. 检查权限配置
```

## 部署监控

### 自动化部署

**GitHub Actions**：
```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: pnpm/action-setup@v2
        with:
          version: 11
      - run: pnpm install
      - run: pnpm build
      - uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./dist
```

### 手动部署脚本

**封装部署流程**：
```bash
#!/bin/bash
# deploy.sh

set -e

echo "🚀 开始部署..."

# 1. 构建
echo "📦 构建..."
cd /root/.openclaw/workspace-main/pixel-astro-blog
pnpm build

# 2. 提交
echo "📝 提交变更..."
git add .
git commit -m "🚀 自动部署: $(date '+%Y-%m-%d %H:%M:%S')"

# 3. 推送
echo "📤 推送到远程..."
git push https://3229154448:ghp_TOKEN@github.com/3229154448/pixel-astro-blog.git main

# 4. 验证
echo "✅ 验证部署..."
node -e "fetch('https://3229154448.github.io/pixel-astro-blog/').then(r => console.log('Status:', r.status))"

echo "🎉 部署完成！"
```

## 最佳实践

### 部署策略
1. **自动化优先**：使用 GitHub Actions 自动部署
2. **快速反馈**：部署后立即验证
3. **回滚机制**：保留最近版本，支持快速回滚
4. **监控告警**：部署失败时及时通知

### 版本管理
1. **语义化版本**：使用版本号管理发布
2. **构建标签**：为每个版本打标签
3. **变更日志**：记录每次部署的变更

### 安全实践
1. **最小权限**：使用最小权限的 token
2. **定期轮换**：定期更新 token
3. **审计日志**：记录所有部署操作
4. **敏感信息**：使用环境变量存储敏感信息

### 性能优化
1. **缓存策略**：使用 CDN 缓存静态资源
2. **压缩优化**：启用 gzip/brotli 压缩
3. **懒加载**：延迟加载非关键资源
4. **CDN 加速**：使用 CDN 加速静态资源
