import os, requests, re, json
from bs4 import BeautifulSoup
from datetime import datetime

# 物理定数・定数定義
SOURCE_NAME = "J-Net21"
DATA_FILE = "subsidies_db.json" # 蓄積用データベース

def fetch_and_merge():
    """過去データを読み込み、新着とマージして保存する"""
    db = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            db = json.load(f)
    
    # 新着取得
    try:
        res = requests.get("https://j-net21.smrj.go.jp/snavi/articles", timeout=20)
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, 'html.parser')
        links = soup.find_all('a', href=re.compile(r'/snavi/articles/\d+'))
        
        new_items = []
        seen = {item['title'] for item in db} # 既存タイトルをセットで高速照合
        
        for a in links:
            t = a.get_text(strip=True)
            if len(t) > 12 and t not in seen:
                h = a.get('href')
                url = h if h.startswith('http') else "https://j-net21.smrj.go.jp" + h
                new_items.append({"title": t, "link": url, "date": datetime.now().strftime("%Y-%m-%d")})
                seen.add(t)
        
        # 結合して保存
        db = new_items + db # 新着を上に
        db = db[:1000] # 最大1000件まで蓄積
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
        return db
    except Exception as e:
        print(f"Fetch Error: {e}")
        return db

def generate_html(db):
    # 汎用性の高いアフィリエイトリンク（知識不要で収益化）
    AMAZON_URL = "https://www.amazon.co.jp/s?k=起業+補助金+ガイド"
    
    list_items = ""
    for item in db[:50]: # 表示は最新50件に制限（速度維持）
        list_items += f"""
        <div style="padding:20px 0; border-bottom:1px solid #E2E8F0;">
            <p style="font-size:0.8rem; color:#A0AEC0; margin:0;">{item.get('date', '不明')}</p>
            <h2 style="font-size:1.1rem; margin:5px 0 15px 0; font-weight:700;">{item['title']}</h2>
            <a href="{item['link']}" target="_blank" style="background-color:#2B6CB0; color:#FFFFFF; padding:10px 20px; text-decoration:none; border-radius:5px; font-size:0.85rem; font-weight:bold; display:inline-block;">詳細を確認</a>
        </div>"""
    
    # 物理的デザインの構築
    html = f"""<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8">
    <title>補助金DB | 過去データ蓄積型マネタイズサイト</title></head>
    <body style="max-width:640px; margin:0 auto; padding:40px 20px; font-family:sans-serif; background-color:#F8FAFC;">
        <header style="background:#FFFFFF; padding:20px; border-radius:10px; margin-bottom:30px; border:1px solid #E2E8F0;">
            <h1 style="margin:0; font-size:1.5rem; color:#2B6CB0;">補助金速報 & データベース</h1>
            <p style="font-size:0.9rem; color:#718096;">現在 {len(db)} 件の情報を蓄積中</p>
            <div style="margin-top:15px; background:#F0FFF4; padding:10px; border-radius:5px; border:1px solid #C6F6D5;">
                <a href="{AMAZON_URL}" style="font-size:0.85rem; color:#2F855A; text-decoration:none; font-weight:bold;">[PR] 採択率を上げるための必須知識本はこちら →</a>
            </div>
        </header>
        <main style="background:#FFFFFF; padding:0 25px; border-radius:10px; border:1px solid #E2E8F0;">{list_items}</main>
    </body></html>"""
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    db = fetch_and_merge()
    if db: generate_html(db)
