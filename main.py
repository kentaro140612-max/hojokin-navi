import os, requests, re, hashlib, glob
from bs4 import BeautifulSoup
from datetime import datetime
from openai import OpenAI

# 基本設定
SOURCE_NAME = "J-Net21（独立行政法人 中小企業基盤整備機構）"
SOURCE_URL = "https://j-net21.smrj.go.jp/"
now_dt = datetime.now()
now = now_dt.strftime('%Y年%m月%d日 %H:%M')
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

os.makedirs("articles", exist_ok=True)

def cleanup_old_files():
    """英数字ID以外のファイルを物理削除しディレクトリを浄化"""
    for f in glob.glob("articles/*.html"):
        if not re.match(r'^[a-f0-9]{12}_\d+\.html$', os.path.basename(f)):
            try: os.remove(f)
            except: pass

def ai_analyze(title):
    """思考の連鎖を用いてタイトルから深層情報を推論"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": """補助金タイトルを精密に分析し、公的支援の文脈で以下を推論せよ。
1.カテゴリ:[製造・建設, IT・DX, 商業・サービス, その他]
2.対象者:(例:中小企業, 個人事業主, 特定の自治体企業)
3.活用内容:(15文字以内。何に使えるか)
4.概算金額:(タイトルに無ければ'一次資料参照')
5.推奨度:(★1-5)
形式：カテゴリ/対象者/活用内容/概算金額/推奨度"""},
                {"role": "user", "content": title}
            ]
        )
        # スラッシュ区切りで分割
        res = response.choices[0].message.content.split("/")
        if len(res) < 5: return "その他", "要確認", "公式ページを参照", "一次資料参照", "★★★"
        return res[0], res[1], res[2], res[3], res[4]
    except Exception:
        return "その他", "要確認", "公式ページを参照", "一次資料参照", "★★★"

def generate_individual_page(item, cat, target, usage, amount, score, file_id):
    """テーブル構造を採用し情報密度を高めた詳細ページ"""
    file_path = f"articles/{file_id}.html"
    html = f"""<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{item['title']}</title></head>
<body style="max-width:600px; margin:0 auto; padding:40px 20px; font-family:sans-serif; line-height:1.6; color:#333; background:#f9f9f9;">
    <a href="../index.html" style="color:#1a73e8; text-decoration:none; font-weight:bold;">← 補助金一覧に戻る</a>
    <h1 style="font-size:1.4rem; margin:25px 0; color:#202124; line-height:1.4;">{item['title']}</h1>
    
    <div style="background:#fff; padding:25px; border-radius:12px; box-shadow:0 4px 12px rgba(0,0,0,0.08); margin-bottom:30px;">
        <h3 style="margin:0 0 15px 0; font-size:1rem; color:#1a73e8; border-bottom:2px solid #e8f0fe; padding-bottom:8px;">AIクイック解析結果</h3>
        <table style="width:100%; border-collapse:collapse; font-size:0.95rem;">
            <tr style="border-bottom:1px solid #f0f0f0;"><td style="padding:12px 0; color:#666; width:35%;">カテゴリ</td><td style="padding:12px 0; font-weight:bold; color:#1a73e8;">{cat}</td></tr>
            <tr style="border-bottom:1px solid #f0f0f0;"><td style="padding:12px 0; color:#666;">主な対象者</td><td style="padding:12px 0; font-weight:bold;">{target}</td></tr>
            <tr style="border-bottom:1px solid #f0f0f0;"><td style="padding:12px 0; color:#666;">想定される使い道</td><td style="padding:12px 0; font-weight:bold;">{usage}</td></tr>
            <tr style="border-bottom:1px solid #f0f0f0;"><td style="padding:12px 0; color:#666;">助成・補助金額</td><td style="padding:12px 0; font-weight:bold; color:#d32f2f;">{amount}</td></tr>
            <tr><td style="padding:12px 0; color:#666;">AI推奨スコア</td><td style="padding:12px 0; font-weight:bold; color:#fbc02d; font-size:1.1rem;">{score}</td></tr>
        </table>
    </div>

    <div style="background:#e8f0fe; padding:25px; border-radius:12px; border:1px solid #1a73e8;">
        <p style="font-size:0.85rem; color:#1967d2; font-weight:bold; margin:0 0 15px 0;">📍 公的機関の一次情報を確認する</p>
        <a href="{item['link']}" target="_blank" style="display:block; text-align:center; background:#1a73e8; color:#fff; padding:18px; text-decoration:none; border-radius:8px; font-weight:bold; font-size:1.1rem; box-shadow:0 4px 6px rgba(26,115,232,0.2);">公式サイト(J-Net21)で詳細を見る</a>
        <p style="font-size:0.7rem; color:#5f6368; margin-top:12px; text-align:center;">出典元：{SOURCE_NAME}</p>
    </div>
    <p style="font-size:0.75rem; color:#999; margin-top:20px; text-align:center;">※本解析はAIがタイトル情報を基に生成したものであり、実態と異なる場合があります。</p>
</body></html>"""
    with open(file_path, "w", encoding="utf-8") as f: f.write(html)
    return file_path

def generate_html(subsidies):
    cleanup_old_files()
    list_items = ""
    article_urls = []
    for i, item in enumerate(subsidies):
        # AI分析を実行し各項目を取得
        cat, target, usage, amount, score = ai_analyze(item['title'])
        file_id = hashlib.md5(item['title'].encode()).hexdigest()[:12] + f"_{i}"
        
        # 取得した全項目を個別ページ生成に渡す
        page_path = generate_individual_page(item, cat, target, usage, amount, score, file_id)
        article_urls.append(page_path)
        
        list_items += f"""
        <article style="border:1px solid #e0e0e0; padding:20px; margin-bottom:15px; border-radius:12px; background:#fff; box-shadow:0 1px 3px rgba(0,0,0,0.05);">
            <div style="font-size:0.65rem; color:#1a73e8; font-weight:bold; margin-bottom:8px;">{cat} | {target}</div>
            <h2 style="font-size:1.05rem; margin:0 0 15px 0; color:#202124; line-height:1.5;">{item['title']}</h2>
            <div style="display:flex; gap:10px;">
                <a href="{page_path}" style="flex:1; text-align:center; background:#f8f9fa; border:1px solid #dadce0; color:#3c4043; padding:12px; text-decoration:none; border-radius:8px; font-size:0.85rem; font-weight:bold;">クイック確認</a>
                <a href="{item['link']}" target="_blank" style="flex:1; text-align:center; background:#1a73e8; color:#fff; padding:12px; text-decoration:none; border-radius:8px; font-size:0.85rem; font-weight:bold;">公式サイト</a>
            </div>
        </article>"""
    
    html_content = f"""<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI補助金ナビ | 公的支援情報をAIが最速解析</title></head>
<body style="max-width:600px; margin:0 auto; background:#f1f3f4; padding:20px; font-family:-apple-system,sans-serif;">
    <header style="margin-bottom:30px; text-align:center; border-bottom:2px solid #1a73e8; padding-bottom:15px;">
        <h1 style="margin:0; font-size:1.6rem; color:#1a73e8;">AI補助金ナビ</h1>
        <p style="font-size:0.85rem; color:#d32f2f; font-weight:bold; margin:8px 0;">📍 毎日AM9:00更新。ブックマークしてご活用ください。</p>
        <p style="font-size:0.7rem; color:#5f6368; margin:0;">データ出典：中小機構 J-Net21</p>
    </header>
    <main>{list_items}</main>
</body></html>"""
    with open("index.html", "w", encoding="utf-8") as f: f.write(html_content)

def fetch_data():
    url = "https://j-net21.smrj.go.jp/snavi/articles"
    res = requests.get(url, timeout=30)
    res.encoding = res.apparent_encoding
    soup = BeautifulSoup(res.text, 'html.parser')
    all_links = soup.find_all('a', href=re.compile(r'/snavi/articles/\d+'))
    data = []
    seen = set()
    for a in all_links:
        t = a.get_text(strip=True)
        h = a.get('href')
        if len(t) > 5 and t not in seen:
            f_url = h if h.startswith('http') else "https://j-net21.smrj.go.jp" + h
            data.append({"title": t, "link": f_url})
            seen.add(t)
            if len(data) >= 10: break
    return data

if __name__ == "__main__":
    try:
        subsidies = fetch_data()
        if subsidies: generate_html(subsidies)
    except Exception as e: print(f"Error: {e}")
