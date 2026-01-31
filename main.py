import os, requests, re, hashlib, json
from bs4 import BeautifulSoup
from datetime import datetime
from openai import OpenAI

SOURCE_NAME = "J-Net21（中小機構）"
SOURCE_URL = "https://j-net21.smrj.go.jp/"
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

os.makedirs("articles", exist_ok=True)

def get_badge_info(amount_str, category):
    """金額とカテゴリからアイコンとバッジ色を論理的に決定"""
    # 金額判定（「万」を考慮した数値化）
    num_match = re.search(r'(\d+)', amount_str)
    val = int(num_match.group(1)) if num_match else 0
    if "万" not in amount_str and val > 0: val = val / 10000 # 円単位の場合

    # アイコン判定
    icons = {"IT・DX": "💻", "製造・建設": "🏗️", "商業・サービス": "🛍️", "その他": "💡"}
    icon = icons.get(category, "💡")

    # バッジ色判定
    if val >= 500: return icon, "大規模", "#6B46C1" # 紫（高額）
    if val >= 100: return icon, "中規模", "#2B6CB0" # 青（標準）
    return icon, "少額支援", "#2F855A" # 緑（手軽）

def ai_analyze(title):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": """補助金を分析しJSONで返せ。'参照'禁止。
項目: cat(製造・建設, IT・DX, 商業・サービス, その他), target, usage, amount(具体的な〜万円), score(1-5)"""},
                {"role": "user", "content": title}
            ]
        )
        data = json.loads(response.choices[0].message.content)
        s = int(data.get("score", 3))
        return {
            "cat": data.get("cat", "その他"),
            "target": data.get("target", "事業者"),
            "usage": data.get("usage", "詳細を確認"),
            "amount": data.get("amount", "10万円〜"),
            "score": '★' * s + '☆' * (5 - s)
        }
    except:
        return {"cat": "その他", "target": "要確認", "usage": "詳細を確認", "amount": "10万円〜", "score": "★★★☆☆"}

def generate_individual_page(item, info, file_id):
    file_path = f"articles/{file_id}.html"
    icon, b_name, b_color = get_badge_info(info['amount'], info['cat'])
    
    html = f"""<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{item['title']}</title></head>
<body style="max-width:600px; margin:0 auto; padding:40px 20px; font-family:sans-serif; background:#F7FAFC; color:#1A202C;">
    <a href="../index.html" style="color:#2B6CB0; text-decoration:none; font-weight:bold;">← 戻る</a>
    <div style="margin:25px 0;">
        <span style="background:{b_color}; color:white; padding:6px 14px; border-radius:6px; font-weight:bold; font-size:0.8rem;">{icon} {b_name}</span>
    </div>
    <h1 style="font-size:1.3rem; line-height:1.4; margin-bottom:30px;">{item['title']}</h1>
    
    <div style="background:white; padding:30px; border-radius:15px; box-shadow:0 4px 20px rgba(0,0,0,0.08); border:1px solid #E2E8F0;">
        <h3 style="margin-top:0; font-size:0.9rem; color:#718096; border-bottom:1px solid #EDF2F7; padding-bottom:10px;">制度の簡易要約（AI推定）</h3>
        <table style="width:100%; border-collapse:collapse;">
            <tr><td style="padding:15px 0; color:#718096; width:45%;">支援対象</td><td style="font-weight:bold;">{info['target']}</td></tr>
            <tr><td style="padding:15px 0; color:#718096;">活動内容</td><td style="font-weight:bold;">{info['usage']}</td></tr>
            <tr><td style="padding:15px 0; color:#718096;">推定金額</td><td style="font-weight:bold; color:#C53030; font-size:1.1rem;">{info['amount']}</td></tr>
            <tr><td style="padding:15px 0; color:#718096;">おすすめ度</td><td style="font-weight:bold; color:#D69E2E; letter-spacing:2px;">{info['score']}</td></tr>
        </table>
    </div>

    <div style="margin-top:30px; background:#2B6CB0; padding:35px; border-radius:12px; text-align:center;">
        <a href="{item['link']}" target="_blank" style="display:block; background:white; color:#2B6CB0; padding:20px; text-decoration:none; border-radius:8px; font-weight:bold; font-size:1.1rem;">J-Net21で一次資料を確認</a>
    </div>
    <p style="font-size:0.75rem; color:#A0AEC0; margin-top:30px; text-align:center;">出典：{SOURCE_NAME}</p>
</body></html>"""
    with open(file_path, "w", encoding="utf-8") as f: f.write(html)
    return file_path

def generate_html(subsidies):
    list_items = ""
    for i, item in enumerate(subsidies):
        info = ai_analyze(item['title'])
        file_id = hashlib.md5(item['title'].encode()).hexdigest()[:12] + f"_{i}"
        path = generate_individual_page(item, info, file_id)
        icon, b_name, b_color = get_badge_info(info['amount'], info['cat'])
        
        list_items += f"""
        <article style="border:1px solid #E2E8F0; padding:25px; margin-bottom:20px; border-radius:16px; background:white; position:relative;">
            <div style="display:flex; justify-content:space-between; margin-bottom:15px;">
                <span style="font-size:0.75rem; font-weight:bold; color:#2B6CB0;">{icon} {info['cat']}</span>
                <span style="background:{b_color}; color:white; font-size:0.65rem; padding:3px 10px; border-radius:4px; font-weight:bold;">{b_name}</span>
            </div>
            <h2 style="font-size:1.05rem; margin:0 0 20px 0; color:#2D3748; line-height:1.5;">{item['title']}</h2>
            <div style="display:flex; gap:12px;">
                <a href="{path}" style="flex:1; text-align:center; background:#EDF2F7; color:#4A5568; padding:12px; text-decoration:none; border-radius:8px; font-size:0.85rem; font-weight:bold;">詳細解析</a>
                <a href="{item['link']}" target="_blank" style="flex:1; text-align:center; background:#2B6CB0; color:white; padding:12px; text-decoration:none; border-radius:8px; font-size:0.85rem; font-weight:bold;">公式サイト</a>
            </div>
        </article>"""
    
    html_content = f"""<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>AI補助金ナビ</title></head>
<body style="max-width:600px; margin:0 auto; background:#F7FAFC; padding:20px; font-family:sans-serif;">
    <header style="margin-bottom:40px; text-align:center;">
        <h1 style="color:#2B6CB0; font-size:1.8rem;">AI補助金ナビ</h1>
        <div style="background:#E53E3E; color:white; font-size:0.8rem; font-weight:bold; padding:5px 15px; border-radius:20px; display:inline-block; margin-top:10px;">毎日AM9:00更新。ブックマーク推奨</div>
    </header>
    <main>{list_items}</main>
</body></html>"""
    with open("index.html", "w", encoding="utf-8") as f: f.write(html_content)
