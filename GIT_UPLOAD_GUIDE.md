# 🚀 Git仓库上传指南

本指南将帮助你将OKX LP管理系统的代码上传到Git远程仓库。

## ✅ 已完成的本地Git设置

我们已经为你完成了以下步骤：

1. ✅ 创建了 `.gitignore` 文件
2. ✅ 初始化了Git仓库 (`git init`)
3. ✅ 添加了所有文件到暂存区 (`git add .`)
4. ✅ 创建了首次提交 (`git commit`)

## 🎯 下一步：创建远程仓库并上传

### 方案一：使用自动化脚本 (推荐)

我们为你创建了一个自动化脚本 `scripts/git_setup.sh`，可以快速完成上传：

```bash
# 1. 先在Git平台创建空仓库，获取仓库URL
# 2. 运行脚本 (替换成你的实际仓库URL)
./scripts/git_setup.sh https://github.com/YOUR_USERNAME/okx-lp-manager.git
```

### 方案二：手动操作

#### 第一步：选择Git托管平台

| 平台 | 网址 | 特点 |
|------|------|------|
| **GitHub** | https://github.com | 全球最大的代码托管平台，社区活跃 |
| **GitLab** | https://gitlab.com | 功能完整，支持CI/CD，有免费私有仓库 |
| **Gitee** | https://gitee.com | 国内平台，访问速度快，对中文友好 |
| **Bitbucket** | https://bitbucket.org | Atlassian产品，与Jira集成良好 |

#### 第二步：创建远程仓库

以**GitHub**为例：

1. 访问 https://github.com
2. 登录你的账户
3. 点击右上角的 "+" → "New repository"
4. 填写仓库信息：
   - **Repository name**: `okx-lp-manager`
   - **Description**: `OKX钱包LP管理系统 - 基于OKX API和PancakeSwap V3的流动性管理工具`
   - **Public/Private**: 根据需要选择
   - **⚠️ 重要**: 不要勾选任何初始化选项 (README, .gitignore, license)
5. 点击 "Create repository"

#### 第三步：连接并推送到远程仓库

创建仓库后，按照以下命令操作：

```bash
# 添加远程仓库 (替换成你的实际URL)
git remote add origin https://github.com/YOUR_USERNAME/okx-lp-manager.git

# 确保在main分支
git branch -M main

# 推送到远程仓库
git push -u origin main
```

## 🔧 不同平台的具体操作

### GitHub 操作步骤

```bash
# 示例URL
git remote add origin https://github.com/YOUR_USERNAME/okx-lp-manager.git
git branch -M main
git push -u origin main
```

### GitLab 操作步骤

```bash
# 示例URL
git remote add origin https://gitlab.com/YOUR_USERNAME/okx-lp-manager.git
git branch -M main
git push -u origin main
```

### Gitee 操作步骤

```bash
# 示例URL
git remote add origin https://gitee.com/YOUR_USERNAME/okx-lp-manager.git
git branch -M main
git push -u origin main
```

## 🔐 SSH密钥设置 (推荐)

为了避免每次推送都输入密码，建议设置SSH密钥：

### 1. 生成SSH密钥

```bash
# 生成新的SSH密钥
ssh-keygen -t ed25519 -C "your_email@example.com"

# 启动ssh-agent
eval "$(ssh-agent -s)"

# 添加SSH密钥到ssh-agent
ssh-add ~/.ssh/id_ed25519
```

### 2. 添加公钥到Git平台

```bash
# 复制公钥到剪贴板 (macOS)
pbcopy < ~/.ssh/id_ed25519.pub

# 或者查看公钥内容
cat ~/.ssh/id_ed25519.pub
```

然后在Git平台的Settings → SSH Keys中添加这个公钥。

### 3. 使用SSH URL

```bash
# GitHub SSH URL示例
git remote add origin git@github.com:YOUR_USERNAME/okx-lp-manager.git

# 或者修改现有的远程仓库URL
git remote set-url origin git@github.com:YOUR_USERNAME/okx-lp-manager.git
```

## 🚀 推送后的操作

### 验证上传成功

```bash
# 查看远程仓库信息
git remote -v

# 查看提交历史
git log --oneline

# 查看仓库状态
git status
```

### 设置仓库信息

1. **编辑README.md**: 根据项目实际情况更新文档
2. **添加标签**: 为重要版本创建标签
3. **设置分支保护**: 保护main分支
4. **配置Issues**: 启用问题跟踪
5. **设置Wiki**: 编写详细文档

## 📝 常用Git命令

### 日常开发

```bash
# 查看状态
git status

# 添加文件
git add .
git add filename.py

# 提交更改
git commit -m "feat: 添加新功能"

# 推送到远程
git push

# 拉取远程更改
git pull

# 查看历史
git log --oneline
```

### 分支管理

```bash
# 创建并切换到新分支
git checkout -b feature/new-feature

# 切换分支
git checkout main

# 合并分支
git merge feature/new-feature

# 删除分支
git branch -d feature/new-feature
```

## 🛡️ 安全注意事项

### 敏感信息保护

确保以下文件不会被提交到远程仓库：

- ✅ `.env` 文件 (已在.gitignore中)
- ✅ `config.env` 文件 (已在.gitignore中)  
- ✅ 私钥文件
- ✅ 数据库密码
- ✅ API密钥

### 检查提交内容

```bash
# 推送前检查将要提交的内容
git diff --cached

# 查看最近的提交
git show HEAD
```

## 🔧 故障排除

### 常见错误及解决方案

#### 推送被拒绝

```bash
# 错误: Updates were rejected because the remote contains work
# 解决: 先拉取远程更改
git pull origin main --rebase
git push origin main
```

#### 远程仓库不为空

```bash
# 如果远程仓库已有内容，强制推送 (谨慎使用)
git push -u origin main --force
```

#### 用户认证失败

```bash
# 配置用户信息
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

## 🎉 上传完成后的下一步

1. **访问仓库**: 在浏览器中查看你的代码
2. **更新文档**: 完善README.md和其他文档
3. **设置CI/CD**: 配置自动化测试和部署
4. **邀请协作者**: 如果是团队项目
5. **创建第一个Issue**: 记录待完成的功能

---

## 📧 需要帮助？

如果在上传过程中遇到问题，可以：

1. 查看Git官方文档: https://git-scm.com/docs
2. 查看平台帮助文档 (GitHub Help, GitLab Docs等)
3. 检查网络连接和权限设置 