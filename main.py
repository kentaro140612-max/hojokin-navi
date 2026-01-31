import os, requests, re, json
from bs4 import BeautifulSoup
from datetime import datetime

DATA_FILE = "subsidies_db.json"

def fetch_and_merge():
    # 1. 既存データの読み込み
    db = []
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                db = json.load(f)
        except: db = []

    # 2. 新着データの取得
    try:
        res = requests.get("https://j-net21.smrj.go.jp/snavi/articles", timeout=20)
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, 'html.parser')
        links = soup.find_all('a', href=re.compile(r'/snavi/articles/\d+'))
        
        new_count = 0
        seen_titles = {item['title'] for item in db}
        
        for a in links:
            title = a.get_text(strip=True)
            if len(title) > 12 and title not in seen_titles:
                href = a.get('href')
                url = href if href.startswith('http') else "https://j-net21.smrj.go.jp" + href
                db.insert(0, {
                    "title": title, 
                    "link": url, 
                    "date": datetime.now().strftime("%Y-%m-%d")
                })
                seen_titles.add(title)
                new_count += 1
        
        # 3. 最大1000件でカット（パフォーマンス維持）
        db = db[:1000]
        
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
        print(f"Update Complete: {new_count} new items added.")
        return db
    except Exception as e:
        print(f"Error: {e}")
        return db

# HTML生成部分は前回のコードを継承
