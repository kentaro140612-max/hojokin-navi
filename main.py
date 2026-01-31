import os, requests, re, json
from bs4 import BeautifulSoup
from datetime import datetime

DATA_FILE = "subsidies_db.json"

def fetch_and_merge():
    # 初回実行時：ファイルがなければ空のリストで作成する
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
    
    db = []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            db = json.load(f)
    except:
        db = []

    # （以下、データ取得ロジックは継続）
