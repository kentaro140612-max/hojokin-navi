import os, requests, re
from bs4 import BeautifulSoup

# 設定の厳格化：AI依存を完全に断ち切り、物理的なデータ取得のみを行う
SOURCE_NAME = "J-Net21（独立行政法人 中小企業基盤整備機構）"
SOURCE_URL = "https://j-net21.smrj.go.jp/snavi/articles"

def fetch_data():
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
        print(f"Error: {e}")
        return []

def generate_html(subsidies):
    """
    色彩（青）と文言の削除を物理的に適用したHTMLを生成。
    """
    list_items = ""
    for item in subsidies:
        # 青色(#2B6CB0)を最優先で適用し、冗長な文言を排除したボタン
        list_items += f"""
        <div style="padding:24px 0; border-bottom:1px solid #E2E8F0;">
            <h2 style="font-size:1.1rem; line-height:1.6; margin:0 0 16px 0; color:#1A202C; font-weight:700;">{item['title']}</h2>
            <a href="{item['link']}" target="_blank" style="background-color:#2B6CB0 !important; color:#FFFFFF !important; padding:12px 24px; text-decoration:none; border-radius:6px; font-size:0.9rem; font-weight:bold; display:inline-block;">公募要領を確認する</a>
        </div>"""
    
    html_content = f"""<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>補助金速報</title></head>
<body style="max-width:600px; margin:0 auto; background-color:#F7FAFC; padding:40px 20px; font-family:sans-serif;">
    <header style="margin-bottom:40px; border-left:5px solid #2B6CB0; padding-left:15px;">
        <h1 style="font-size:1.8rem; margin:0; color:#1A202C;">補助金速報</h1>
        <p style="font-size:1rem; color:#718096; margin-top:10px;">J-Net21 公募情報：最新30件</p>
    </header>
    <main style="background-color:#FFFFFF; padding:10px 30px; border-radius:12px; border:1px solid #E2E8F0; box-shadow:0 4px 6px rgba(0,0,0,0.05);">
        {list_items}
    </main>
    <footer style="margin-top:60px; text-align:center; font-size:0.8rem; color:#A0AEC0;">
        <p>出典：{SOURCE_NAME}</p>
        <p style="margin-top:8px;">24時間ごとに自動更新中</p>
    </footer>
</body></html>"""
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    data = fetch_data()
    if data:
        generate_html(data)
