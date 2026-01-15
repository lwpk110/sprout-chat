# Git 工作流：双仓库同步

**版本**: v1.0
**更新日期**: 2026-01-15

---

## 概述

本项目使用 **GitHub** 和 **Gitee** 两个远程仓库，保持代码同步：

- **GitHub**: https://github.com/lwpk110/sprout-chat
- **Gitee**: https://gitee.com/steven_lu/sprout-chat

---

## Remote 配置

### 当前配置

```bash
$ git remote -v

gitee   https://gitee.com/steven_lu/sprout-chat.git (fetch)
gitee   https://gitee.com/steven_lu/sprout-chat.git (push)
origin  https://github.com/lwpk110/sprout-chat.git (fetch)
origin  https://github.com/lwpk110/sprout-chat.git (push)
```

- **origin**: GitHub 仓库（主仓库）
- **gitee**: Gitee 仓库（镜像仓库）

### 添加 Remote

如果您需要配置双仓库：

```bash
# 添加 GitHub
git remote add origin https://github.com/lwpk110/sprout-chat.git

# 添加 Gitee
git remote add gitee https://gitee.com/steven_lu/sprout-chat.git

# 验证配置
git remote -v
```

---

## 推送工作流

### 方式 1：一键推送（推荐）

使用项目提供的推送脚本：

```bash
# 推送当前分支到所有仓库
git push-all

# 推送指定分支
git push-all main
```

**脚本位置**: `scripts/push-all.sh`

**功能**:
1. 推送到 GitHub (`origin`)
2. 推送到 Gitee (`gitee`)
3. 显示推送结果

### 方式 2：分别推送

```bash
# 推送到 GitHub
git push origin main

# 推送到 Gitee
git push gitee main
```

### 方式 3：使用 Git Alias

项目已配置 Git alias：

```bash
# 查看已配置的 alias
git config --local --get alias.push-all

# 使用 alias 推送
git push-all
```

---

## 拉取工作流

### 从 GitHub 拉取

```bash
git pull origin main
```

### 从 Gitee 拉取

```bash
git pull gitee main
```

### 推荐做法

**默认从 GitHub 拉取**（主仓库）：

```bash
git pull origin main
```

---

## 分支管理

### 创建分支

```bash
# 从 GitHub 拉取最新代码
git pull origin main

# 创建新分支
git checkout -b feature/new-feature

# 推送到 GitHub
git push -u origin feature/new-feature
```

### 删除分支

```bash
# 删除本地分支
git branch -d feature/new-feature

# 删除 GitHub 远程分支
git push origin --delete feature/new-feature

# 删除 Gitee 远程分支
git push gitee --delete feature/new-feature
```

---

## 常见问题

### Q1: 两个仓库如何保持同步？

**A**: 使用 `git push-all` 命令同时推送到两个仓库。

### Q2: 推送到 Gitee 失败怎么办？

**A**: 检查网络连接和认证信息：

```bash
# 测试 Gitee 连接
git ls-remote gitee

# 如果需要认证
git remote set-url gitee https://username:password@gitee.com/steven_lu/sprout-chat.git
```

### Q3: 如何只推送到 GitHub？

**A**: 使用 `git push origin main` 只推送到 GitHub。

### Q4: 两个仓库的历史记录不一致怎么办？

**A**: 保持 GitHub 为主仓库，Gitee 为镜像：

```bash
# 强制同步 Gitee 到 GitHub
git fetch origin main
git push gitee main --force
```

---

## 最佳实践

1. **开发流程**:
   ```bash
   # 1. 从 GitHub 拉取最新代码
   git pull origin main

   # 2. 创建分支并开发
   git checkout -b feature/new-feature
   # ... 开发代码 ...

   # 3. 提交更改
   git add .
   git commit -m "feat: add new feature"

   # 4. 推送到 GitHub
   git push -u origin feature/new-feature

   # 5. 创建 PR 到 GitHub

   # 6. PR 合并后，推送到 Gitee
   git checkout main
   git pull origin main
   git push-all main
   ```

2. **定期同步**:
   - 每次合并 PR 后，同步到 Gitee
   - 使用 `git push-all` 确保两个仓库一致

3. **CI/CD**:
   - GitHub Actions 配置在 GitHub 仓库
   - Gitee 作为代码备份镜像

---

## 附录

### A. Git Remote 命令参考

```bash
# 查看所有 remote
git remote -v

# 添加 remote
git remote add <name> <url>

# 删除 remote
git remote remove <name>

# 修改 remote URL
git remote set-url <name> <new-url>

# 查看 remote 信息
git remote show <name>
```

### B. 推送脚本源码

**文件**: `scripts/push-all.sh`

```bash
#!/bin/bash
# 一键推送到 GitHub 和 Gitee

set -e

BRANCH=${1:-main}

echo "🚀 开始推送到所有仓库..."
echo "📌 当前分支: $BRANCH"
echo ""

# 推送到 GitHub
echo "📦 推送到 GitHub..."
git push origin $BRANCH
echo "✅ GitHub 推送完成"
echo ""

# 推送到 Gitee
echo "📦 推送到 Gitee..."
git push gitee $BRANCH
echo "✅ Gitee 推送完成"
echo ""

echo "🎉 所有仓库推送完成！"
```

---

**最后更新**: 2026-01-15
**维护者**: Steven Lu
