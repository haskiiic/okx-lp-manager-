#!/bin/bash

# Git仓库设置脚本
# 使用方法: ./scripts/git_setup.sh https://github.com/YOUR_USERNAME/YOUR_REPO.git

echo "🚀 OKX LP管理系统 - Git仓库设置脚本"
echo "=================================="

# 检查是否提供了远程仓库URL
if [ -z "$1" ]; then
    echo "❌ 错误: 请提供远程仓库URL"
    echo "用法: ./scripts/git_setup.sh https://github.com/YOUR_USERNAME/YOUR_REPO.git"
    exit 1
fi

REMOTE_URL=$1

echo "📋 配置信息:"
echo "远程仓库: $REMOTE_URL"
echo ""

# 配置Git用户信息 (可选)
read -p "🔧 是否要配置Git用户信息? (y/n): " configure_user
if [ "$configure_user" = "y" ]; then
    read -p "请输入你的Git用户名: " git_username
    read -p "请输入你的Git邮箱: " git_email
    
    git config --global user.name "$git_username"
    git config --global user.email "$git_email"
    echo "✅ Git用户信息配置完成"
fi

# 检查是否已经有远程仓库
if git remote get-url origin 2>/dev/null; then
    echo "⚠️  远程仓库已存在，移除旧的配置..."
    git remote remove origin
fi

# 添加远程仓库
echo "🔗 添加远程仓库..."
git remote add origin "$REMOTE_URL"

# 确保在main分支
echo "🌿 切换到main分支..."
git branch -M main

# 推送到远程仓库
echo "⬆️  推送代码到远程仓库..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 成功! 代码已上传到远程仓库"
    echo "📝 仓库地址: $REMOTE_URL"
    echo ""
    echo "📊 仓库统计:"
    echo "提交数量: $(git rev-list --count HEAD)"
    echo "文件数量: $(git ls-files | wc -l)"
    echo "仓库大小: $(du -sh .git | cut -f1)"
    echo ""
    echo "🔗 下一步操作:"
    echo "1. 访问你的Git仓库网页查看代码"
    echo "2. 编辑README.md添加更多项目信息"
    echo "3. 设置仓库的Issues和Wiki (如果需要)"
    echo "4. 邀请团队成员协作 (如果是团队项目)"
else
    echo "❌ 推送失败，请检查:"
    echo "1. 网络连接是否正常"
    echo "2. 远程仓库URL是否正确"
    echo "3. 是否有推送权限"
    echo "4. 远程仓库是否为空仓库"
fi 