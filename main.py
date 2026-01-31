import os, requests, re
from bs4 import BeautifulSoup

# 構成設定：外部依存（OpenAI）をあえて排除し、速度と安定性を物理的に保証
SOURCE_NAME = "J-Net21（中小機構）"
SOURCE_URL = "https://j-net21.smrj.go.jp/snavi/articles"

def fetch_clean_data():
    """J-Net21から最新30件を、脚色なく物理的に取得する"""
    try:
        res = requests.get(SOURCE_URL, timeout=20)
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, 'html.parser')
        links = soup.find_all('a', href=re.compile(r'/snavi/articles/\d+'))
        
        data = []
        seen = set()
        for a in links:
            t = a.get_text(strip=True)
            if len(t) > 12 and t not in seen:
                h = a.get('href')
                full_url = h if h.startswith('http') else "https://j-net21.smrj.go.jp" + h
                data.append({"title": t, "link": full_url})
                seen.add(t)
                if len(data) >= 30: break
        return data
    except Exception as e:
        print(f"Fetch Error: {e}")
        return []

def generate_html(subsidies):
    """装飾を捨て、情報の『鮮度』と『可読性』を最大化したHTMLを生成"""
    list_items = ""
    for item in subsidies:
        # 物理的な区切り線と余白だけで情報を整理
        list_items += f"""
        <article style="padding:24px 0; border-bottom:1px solid #eaecef;">
            <h2 style="font-size:1.1rem; line-height:1.6; margin:0 0 16px 0; color:#1a1d21; font-weight:600;">
                {item['title']}
            </h2>
            <div style="display:flex; justify-content:flex-start;">
                <a href="{item['link']}" target="_blank" style="background-color:#1a1d21; color:#ffffff; padding:12px 24px; text-decoration:none; border-radius:6px; font-size:0.85rem; font-weight:bold;">
                    公式サイトで要項を確認
                </a>
            </div>
        </article>"""
    
    html_content = f"""<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>補助金速報</title></head>
<body style="max-width:600px; margin:0 auto; background-color:#ffffff; padding:40px 20px; font-family:-apple-system, sans-serif; color:#1a1d21;">
    <header style="margin-bottom:40px;">
        <h1 style="font-size:1.8rem; margin:0; letter-spacing:-0.03em;">補助金速報</h1>
        <p style="font-size:0.9rem; color:#6a737d; margin-top:8px;">J-Net21最新30件：余計な加工を省いた最短アクセス</p>
    </header>
    <main>{list_items}</main>
    <footer style="margin-top:60px; padding-bottom:40px; text-align:center; border-top:1px solid #eaecef; padding-top:20px;">
        <p style="font-size:0.75rem; color:#6a737d;">出典：{SOURCE_NAME}<br>データ更新：毎日自動実行</p>
    </footer>
</body></html>"""
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    subsidies = fetch_clean_data()
    if subsidies:
        generate_html(subsidies)
