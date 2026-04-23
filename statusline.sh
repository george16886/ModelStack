#!/bin/bash
# 讀取 Claude Code 傳入的 JSON (透過 stdin)
data=$(cat)

# 透過 node 內建的 JSON.parse 來解析，不用依賴 jq！
parsed=$(echo "$data" | node -e "
let input = '';
process.stdin.on('data', chunk => input += chunk);
process.stdin.on('end', () => {
    try {
        if (!input.trim()) throw new Error('empty');
        const d = JSON.parse(input);
        const cost = d?.cost?.total_cost_usd || '0';
        const remain = d?.context_window?.used_percentage != null ? Math.round(100 - d.context_window.used_percentage) : 100;
        const model = d?.model?.display_name || d?.model || 'Unknown';
        console.log(model + '|' + (Math.round(cost * 10000) / 10000) + '|' + remain);
    } catch(e) {
        console.log('?|?|?');
    }
});
")

# 放進變數裡
model=$(echo "$parsed" | cut -d'|' -f1)
cost=$(echo "$parsed" | cut -d'|' -f2)
remain_pct=$(echo "$parsed" | cut -d'|' -f3)

# 取得目前工作目錄
cwd=$(pwd)

# 取得 Git 狀態
git_branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
if [ -n "$git_branch" ]; then
    if [ -n "$(git status --porcelain 2>/dev/null)" ]; then 
        git_status="* $git_branch"
    else 
        git_status="- $git_branch"
    fi
else 
    git_status="Not in Git"
fi

# 輸出結果
echo -e "\033[1;36m[Model: $model]\033[0m | \033[1;32m[Cost: \$$cost]\033[0m | \033[1;33m[Context: $remain_pct%]\033[0m | \033[1;34m[DIR: $cwd]\033[0m | [Git: $git_status]"
