import os, requests, re, hashlib, json
from bs4 import BeautifulSoup
from datetime import datetime
from openai import OpenAI

SOURCE_NAME = "J-Net21（中小機構）"
SOURCE_URL = "https://j-net21.smrj.go.jp/"
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

os.makedirs("articles", exist_ok=True)

def parse_amount_to_int(amount_str):
    """
    AIが生成した日本語混じりの金額を論理的に数値化する。
    例: '100万円〜' -> 100, '50万' -> 50, '1,000,000' -> 100
    """
    try:
        # 数字と「万」以外の文字を削除
        cleaned = re.sub(r'[^\d万]', '', amount_str)
        if '万' in cleaned:
            num = re.search(r'\d+', cleaned)
            return int(num.group()) if num else 0
        else:
            # 万がない場合は円単位とみなし、万単位に変換
            num = re.search(r'\d+', cleaned)
            return int(num.group()) // 10000 if num else 0
    except:
        return 0

def get_visual_meta(amount_str, category):
    """バッジの色とアイコンを物理的にマッピングする"""
    val = parse_amount_to_int(amount_str)
    
    # カテゴリごとのアイコン定義
    icon_map = {
        "IT・DX": "💻",
        "製造・建設": "🏗️",
        "商業・サービス": "🛍️",
        "その他": "💡"
    }
    icon = icon_map.get(category, "💡")
    
    # 金額規模ごとの色定義（コントラスト重視）
    if val >= 500:
        return icon, "大規模支援", "#6B46C1" # 紫
    elif val >= 100:
        return icon, "中規模支援", "#2B6CB0" # 青
    else:
        return icon, "少額・普及枠", "#2F855A" # 緑

def ai_analyze(title):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": """補助金を分析しJSONで返せ。
項目: cat(製造・建設, IT・DX, 商業・サービス, その他), target(対象), usage(活用内容), amount(金額:必ず数字と'万円'を含める), score(1-5)"""},
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
        return {"cat": "その他", "target": "要資料確認", "usage": "詳細を確認", "amount": "10万円〜", "score": "★★★☆☆"}

def generate_individual_page(item, info, file_id):
    file_path = f"articles/{file_id}.html"
    icon, b_name, b_color = get_visual_meta(info['amount'], info['cat'])
    
    html = f"""<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{item['title']}</title></head>
<body style="max-width:600px; margin:0 auto; padding:40px 20px; font-family:sans-serif; background:#F7FAFC; color:#1A202C;">
    <a href="../index.html" style="color:#2B6CB0; text-decoration:none; font-weight:bold; font-size:0.9rem;">← 一覧に戻る</a>
    <div style="margin:20px 0;">
        <span style="background:{b_color} !important; color:#ffffff !important; padding:6px 14px; border-radius:6px; font-weight:bold; font-size:0.8rem; display:inline-block;">{icon} {b_name}</span>
    </div>
    <h1 style="font-size:1.3rem; line-height:1.4; margin-bottom:30px; color:#2D3748;">{item['title']}</h1>
    
    <div style="background:#ffffff; padding:30px; border-radius:15px; box-shadow:0 4px 20px rgba(0,0,0,0.08); border:1px solid #E2E8F0;">
        <table style="width:100%; border-collapse:collapse;">
            <tr style="border-bottom:1px solid #EDF2F7;"><td style="padding:15px 0; color:#718096; width:45%;">支援対象</td><td style="font-weight:bold;">{info['target']}</td></tr>
            <tr style="border-bottom:1px solid #EDF2F7;"><td style="padding:15px 0; color:#718096;">活動内容</td><td style="font-weight:bold;">{info['usage']}</td></tr>
            <tr style="border-bottom:1px solid #EDF2F7;"><td style="padding:15px 0; color:#718096;">推定金額</td><td style="font-weight:bold; color:#C53030; font-size:1.1rem;">{info['amount']}</td></tr>
            <tr><td style="padding:15px 0; color:#718096;">おすすめ度</td><td style="font-weight:bold; color:#D69E2E; letter-spacing:2px; font-family:monospace;">{info['score']}</td></tr>
        </table>
    </div>

    <div style="margin-top:30px; background:#2B6CB0; padding:35px; border-radius:12px; text-align:center;">
        <a href="{item['link']}" target="_blank" style="display:block; background:#ffffff; color:#2B6CB0; padding:18px; text-decoration:none; border-radius:8px; font-weight:bold; font-size:1.1rem; box-shadow:0 4px 6px rgba(0,0,0,0.1);">J-Net21で一次資料を確認する</a>
    </div>
</body></html>"""
    with open(file_path, "w", encoding="utf-8") as f: f.write(html)
    return file_path

def generate_html(subsidies):
    list_items = ""
    for i, item in enumerate(subsidies):
        info = ai_analyze(item['title'])
        file_id = hashlib.md5(item['title'].encode()).hexdigest()[:12] + f"_{i}"
        path = generate_individual_page(item, info, file_id)
        icon, b_name, b_color = get_visual_meta(info['amount'], info['cat'])
        
        list_items += f"""
        <article style="border:1px solid #E2E8F0; padding:25px; margin-bottom:20px; border-radius:16px; background:#ffffff;">
            <div style="display:flex; justify-content:space-between; margin-bottom:15px; align-items:center;">
                <span style="font-size:0.75rem; font-weight:bold; color:#2B6CB0;">{icon} {info['cat']}</span>
                <span style="background:{b_color} !important; color:#ffffff !important; font-size:0.65rem; padding:3px 10px; border-radius:4px; font-weight:bold; display:inline-block;">{b_name}</span>
            </div>
            <h2 style="font-size:1.05rem; margin:0 0 20px 0; color:#2D3748; line-height:1.5;">{item['title']}</h2>
            <div style="display:flex; gap:12px;">
                <a href="{path}" style="flex:1; text-align:center; background:#EDF2F7; color:#4A5568; padding:12px; text-decoration:none; border-radius:8px; font-size:0.85rem; font-weight:bold;">詳細解析を確認</a>
                <a href="{item['link']}" target="_blank" style="flex:1; text-align:center; background:#2B6CB0; color:#ffffff; padding:12px; text-decoration:none; border-radius:8px; font-size:0.85rem; font-weight:bold;">公式サイトへ</a>
            </div>
        </article>"""
    
    html_content = f"""<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>AI補助金ナビ</title></head>
<body style="max-width:600px; margin:0 auto; background:#F7FAFC; padding:20px; font-family:sans-serif;">
    <header style="margin-bottom:40px; text-align:center;">
        <h1 style="color:#2B6CB0; font-size:1.8rem; margin:0;">AI補助金ナビ</h1>
        <div style="background:#E53E3E; color:#ffffff; font-size:0.8rem; font-weight:bold; padding:5px 15px; border-radius:20px; display:inline-block; margin-top:10px;">毎日AM9:00更新。ブックマーク推奨</div>
    </header>
    <main>{list_items}</main>
</body></html>"""
    with open("index.html", "w", encoding="utf-8") as f: f.write(html_content)
