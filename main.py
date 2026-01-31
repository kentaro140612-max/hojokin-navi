import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from openai import OpenAI

# 物理定数・単位の厳守: 日本標準時
now = datetime.now().strftime('%Y年%m月%d日 %H:%M')
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def ai_summarize(title):
    """
    OpenAI APIを用いて、経営者が反応するキーワード（返済不要等）を抽出要約する。
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "補助金タイトルから、経営者が知るべき要点を3箇条で出力せよ。特に『返済不要』『受給額』『対象』に触れ、15文字以内で簡潔に。形式：・項目名：内容"},
                {"role": "user", "content": title}
            ],
            max_tokens=200
        )
        return response.choices[0].message.content.replace('\n', '<br>')
    except Exception as e:
        print(f"AI Error: {e}")
        return "・内容：詳細は公式URLを確認してください。"

def generate_html_and_sitemap(subsidies):
    # 確定したGoogleフォームURL
    google_form_url = "https://docs.google.com/forms/d/e/1FAIpQLSddIW5zNLUuZLyQWIESX0EOZWZUM3dGM6pdW9Luw20YTiEuwg/viewform?usp=dialog"
    
    list_items = ""
    for item in subsidies:
        summary = ai_summarize(item['title'])
        list_items += f"""
        <article style="border: 1px solid #eee; padding: 25px; margin-bottom: 25px; border-radius: 15px; background: #fff; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
            <h2 style="color: #1a73e8; margin-top: 0; font-size: 1.3rem; line-height: 1.4;">{item['title']}</h2>
            <div style="background: #fff9f9; border: 1px solid #ffebee; padding: 15px; border-radius: 10px; margin: 15px 0; font-size: 0.95rem; line-height: 1.8;">
                <strong style="color: #d93025;">▼ AIによる3秒要約（返済不要情報など）</strong><br>
                {summary}
            </div>
            <div style="display: flex; gap: 10px;">
                <a href="{item['link']}" target="_blank" style="flex: 1; text-align: center; border: 1px solid #dadce0; padding: 12px; text-decoration: none; border-radius: 8px; color: #3c4043; font-weight: bold; font-size: 0.9rem;">公式資料を見る</a>
                <a href="{google_form_url}" target="_blank" style="flex: 1; text-align: center; background: #1a73e8; color: white; padding: 12px; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 0.9rem;">プロに無料相談</a>
            </div>
        </article>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="google-site-verification" content="qDKunZB9hZN753KuLftIbJUXeWBi3bA-HfSS-gej1KA" />
        <title>AI補助金要約ナビ | 返済不要の最新支援情報</title>
        <meta name="description" content="全国の補助金をAIが即座に要約。返済不要な資金調達情報を最短3秒で把握できます。">
    </head>
    <body style="max-width: 600px; margin: 0 auto; background: #f1f3f4; padding: 20px; font-family: sans-serif; color: #202124;">
        <header style="text-align: center; padding: 30px 0;">
            <h1 style="font-size: 1.8rem; margin-bottom: 5px;">AI補助金要約ナビ</h1>
            <p style="color: #5f6368; font-size: 0.9rem;">最終更新：{now}</p>
        </header>
        <main>{list_items}</main>
        <footer style="text-align: center; margin-top: 50px; color: #70757a; font-size: 0.8rem;">
            &copy; 2026 AI Subsidy Navigation.<br>
            AI要約の正確性は保証されません。必ず公式資料をご確認ください。
        </footer>
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    # SEO対策：サイトマップの自動生成
    sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        <url>
            <loc>https://kentaro140612-max.github.io/subsidy-checker/</loc>
            <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
            <priority>1.0</priority>
        </url>
    </urlset>"""
    with open("sitemap.xml", "w", encoding="utf-8") as f:
        f.write(sitemap_content)

def fetch_data():
    res = requests.get("https://j-net21.smrj.go.jp/snavi/articles", timeout=30)
    soup = BeautifulSoup(res.text, 'html.parser')
    articles = soup.select('h3')[:10]
    return [{"title": a.get_text(strip=True), "link": "https://j-net21.smrj.go.jp" + a.find('a')['href']} for a in articles if a.find('a')]

if __name__ == "__main__":
    try:
        data = fetch_data()
        generate_html_and_sitemap(data)
        print("Success: Automated assets updated.")
    except Exception as e:
        print(f"Process Error: {{e}}")
