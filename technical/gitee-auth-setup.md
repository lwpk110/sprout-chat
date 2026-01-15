# Gitee 认证配置指南

**版本**: v1.0
**更新日期**: 2026-01-15

---

## 概述

本文档说明如何配置 Git 与 Gitee 仓库的认证方式。

---

## 方式 1：SSH 公钥认证

### 1.1 生成 SSH 密钥对

如果还没有 SSH 密钥，先生成：

```bash
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
```

### 1.2 查看公钥

```bash
cat ~/.ssh/id_rsa.pub
```

### 1.3 添加公钥到 Gitee

1. 复制公钥内容（从 `ssh-rsa` 开始到结尾）
2. 登录 Gitee: https://gitee.com
3. 点击右上角头像 → **设置**
4. 左侧菜单选择 **SSH 公钥**
5. 点击 **添加公钥**
6. 粘贴公钥内容
7. 点击 **确定**

### 1.4 配置 Git Remote

```bash
# 设置 SSH 格式的 URL
git remote set-url gitee git@gitee.com:steven_lu/sprout-chat.git

# 验证配置
git remote -v
```

### 1.5 测试连接

```bash
ssh -T git@gitee.com
```

成功的话会显示：
```
Hi Steven! You've successfully authenticated...
```

---

## 方式 2：个人访问令牌（推荐）

### 2.1 生成个人访问令牌

1. 登录 Gitee: https://gitee.com
2. 点击右上角头像 → **设置**
3. 左侧菜单选择 **安全设置** → **私人令牌**
4. 点击 **生成新令牌**
5. 设置令牌名称（如：sprout-chat-dev）
6. 选择权限（至少需要：**projects**, **repositories**）
7. 点击 **提交**
8. **复制生成的令牌**（只显示一次！）

### 2.2 使用令牌配置 Git

```bash
# 设置 URL 格式：https://<token>@gitee.com/username/repo.git
# 替换 <your_token> 为您的令牌
git remote set-url gitee https://<your_token>@gitee.com/steven_lu/sprout-chat.git
```

**示例**：
```bash
git remote set-url gitee https://a1b2c3d4e5f6g7h8i9j0@gitee.com/steven_lu/sprout-chat.git
```

### 2.3 配置凭据存储（可选）

避免每次推送都输入令牌：

```bash
# 配置凭据助手
git config --global credential.helper store

# 首次推送时输入一次令牌后会自动保存
git push gitee main
```

### 2.4 更新推送脚本

由于 URL 中已包含令牌，推送脚本无需修改：

```bash
git push-all  # 自动推送到 GitHub 和 Gitee
```

---

## 方式 3：HTTPS + 用户名密码（不推荐）

### 3.1 配置凭据助手

```bash
git config --global credential.helper store
```

### 3.2 首次推送

```bash
git push gitee main
```

会提示输入：
- **用户名**: Gitee 用户名/邮箱
- **密码**: Gitee 密码

**注意**: 如果启用了两步验证，需要使用个人访问令牌作为密码。

---

## 当前配置状态

### GitHub
```bash
origin  https://github.com/lwpk110/sprout-chat.git (fetch)
origin  https://github.com/lwpk110/sprout-chat.git (push)
```
**认证方式**: HTTPS

### Gitee
```bash
gitee   git@gitee.com:steven_lu/sprout-chat.git (fetch)
gitee   git@gitee.com:steven_lu/sprout-chat.git (push)
```
**认证方式**: SSH 公钥 ✅

**测试结果**: ✅ SSH 认证成功，推送测试通过

---

## 推荐配置

**最简单的方案**：使用个人访问令牌

```bash
# 1. 在 Gitee 生成令牌
# 2. 配置 Git Remote
git remote set-url gitee https://<your_token>@gitee.com/steven_lu/sprout-chat.git

# 3. 测试推送
git push gitee main

# 4. 使用一键推送脚本
git push-all
```

---

## 常见问题

### Q1: SSH 认证失败 "Permission denied (publickey)"

**A**: 检查以下几点：
1. SSH 公钥是否正确添加到 Gitee
2. `~/.ssh/id_rsa` 私钥文件是否存在
3. 测试连接：`ssh -T git@gitee.com`

### Q2: 如何查看当前使用的 URL？

**A**:
```bash
git remote -v
```

### Q3: 如何切换认证方式？

**A**:
```bash
# SSH → HTTPS
git remote set-url gitee https://gitee.com/steven_lu/sprout-chat.git

# HTTPS → SSH
git remote set-url gitee git@gitee.com:steven_lu/sprout-chat.git
```

### Q4: 个人访问令牌保存在哪里？

**A**: 如果使用 `credential.helper store`，令牌会保存在 `~/.git-credentials` 文件中（明文）。

**更安全的方式**：
```bash
# 使用凭据管理器（加密存储）
git config --global credential.helper libsecret

# Linux: gnome-keyring
# Mac: osxkeychain
# Windows: wincred
```

---

## 安全建议

1. **个人访问令牌**:
   - 定期轮换（每 3-6 个月）
   - 设置合理的过期时间
   - 仅授予必要的权限
   - 不要在代码中硬编码

2. **SSH 密钥**:
   - 使用密码保护私钥
   - 不要分享私钥
   - 定期检查 `~/.ssh/authorized_keys`

3. **凭据存储**:
   - 使用加密的凭据助手
   - 不要在 CI/CD 中明文存储
   - 使用环境变量或密钥管理服务

---

## 附录

### A. 生成个人访问令牌详细步骤

1. 登录 Gitee
2. 点击右上角头像
3. 选择 **设置**
4. 左侧菜单选择 **安全设置**
5. 找到 **私人令牌** 部分
6. 点击 **生成新令牌**
7. 填写表单：
   - 令牌名称：`sprout-chat-dev`
   - 权限范围：
     - ✅ projects
     - ✅ repositories
     - ✅ user_info
   - 过期时间：`90 天` 或自定义
8. 点击 **提交**
9. **复制生成的令牌**（格式：`a1b2c3d4e5f6g7h8i9j0`）

### B. Git Remote 命令参考

```bash
# 查看所有 remote
git remote -v

# 查看 remote 详情
git remote show gitee

# 添加 remote
git remote add gitee <url>

# 删除 remote
git remote remove gitee

# 修改 remote URL
git remote set-url gitee <new-url>
```

---

**最后更新**: 2026-01-15
**维护者**: Steven Lu
