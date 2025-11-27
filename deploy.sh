#!/bin/bash

REPO_URL="https://github.com/jeffery9316-boop/ME2025_Midterm3.git"
PROJECT_DIR="ME2025_Midterm3"

echo "===== 自動部署開始 ====="

# 第一次執行：如果資料夾不存在 → clone + 建立環境
if [ ! -d "$PROJECT_DIR" ]; then
    echo "[第一次執行] Clone 專案到本機..."
    git clone $REPO_URL
    cd $PROJECT_DIR || exit 1

    echo "[第一次執行] 建立虛擬環境 .venv ..."
    python3 -m venv .venv
    source .venv/bin/activate

    echo "[第一次執行] 安裝 requirements.txt 套件 ..."
    pip install -r requirements.txt

    echo "[第一次執行] 啟動 app.py ..."
    python3 app.py
    exit 0
fi

# 第二次執行：資料夾已存在 → git pull + 安裝缺少套件
cd $PROJECT_DIR || exit 1

echo "[第二次執行] 更新專案版本..."
git pull

echo "[第二次執行] 啟動虛擬環境..."
source .venv/bin/activate

echo "[第二次執行] 檢查與安裝缺少的套件..."
pip install -r requirements.txt

echo "[第二次執行] 啟動 app.py ..."
python3 app.py

echo "===== 自動部署完成 ====="
