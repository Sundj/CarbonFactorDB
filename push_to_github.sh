#!/bin/bash
# CarbonFactorDB 推送脚本

cd /home/sundj/.openclaw/workspace/carbon-factor-db

# 移除旧的remote
git remote remove origin 2>/dev/null

# 配置GitHub用户名和邮箱
git config user.name "SunDongJie"
git config user.email "sundj@example.com"

# 请在这里输入你的GitHub Personal Access Token
# 获取方式: GitHub Settings -> Developer settings -> Personal access tokens -> Generate new token
# 需要的权限: repo (完整仓库访问)
echo "请打开GitHub生成Personal Access Token"
echo "访问: https://github.com/settings/tokens"
echo "需要勾选 'repo' 权限"
echo ""
read -p "请输入你的GitHub Token: " TOKEN

# 添加remote
if [ -n "$TOKEN" ]; then
    git remote add origin https://sundj:${TOKEN}@github.com/Sundj/CarbonFactorDB.git
    
    # 推送
    echo "正在推送到GitHub..."
    git push -u origin master
    
    if [ $? -eq 0 ]; then
        echo "✅ 推送成功！"
        echo "访问: https://github.com/Sundj/CarbonFactorDB"
    else
        echo "❌ 推送失败，请检查token权限"
    fi
else
    echo "❌ 未输入token，取消推送"
fi
