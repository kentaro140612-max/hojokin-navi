import os
import requests
from bs4 import BeautifulSoup

def generate_html(data_list):
    """
    蓄積データを元に、公開用のindex.htmlを作成する。
    """
    items_html = ""
    for item in data_list:
        items_html += f"""
        <div style="border: 1px solid #ccc; padding: 15px; margin-bottom: 10px; border-radius: 8px;">
            <h2 style="font-size: 1.25rem; color: #333;">{item['title']}</h2>
            <p><strong>地域:</strong> {item['region']} | <strong>カテゴリー:</strong> {item['category']}</p>
            <a href="{item['url']}" target="_blank" style="color: #007bff;">詳細を見る（外部サイト）</a>
        </div>
        """
    
    full_html = f"""
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>自治体補助金自動集約ナビ 2026</title>
        <meta name="description" content="毎日自動更新される自治体の補助金情報データベース。">
    </head>
    <body style="font-family: sans-serif; max-width: 800px; margin: 0 auto; padding: 20px;">
        <h1>自治体補助金自動集約ナビ</h1>
        <p>最終更新: 2026年01月31日</p>
        {items_html}
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(full_html)

def get_latest_subsidies():
    url = "https://j-net21.smrj.go.jp/snavi/articles"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    
    articles = soup.select('h3')[:10] 
    data_list = []
    for art in articles:
        title = art.get_text(strip=True)
        link = "https://j-net21.smrj.go.jp" + art.find('a')['href'] if art.find('a') else url
        data_list.append({"title": title, "region": "全国", "category": "経営支援", "url": link})
    
    generate_html(data_list)

if __name__ == "__main__":
    get_latest_subsidies()
