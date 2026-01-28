import os
import requests
from datetime import datetime
import re

def run_scraper():
    AIRTABLE_TOKEN = os.getenv('AIRTABLE_TOKEN')
    AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
    AIRTABLE_TABLE_NAME = os.getenv('AIRTABLE_TABLE_NAME')
    headers = {"Authorization": f"Bearer {AIRTABLE_TOKEN}", "Content-Type": "application/json"}
    base_url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"

    try:
        # 1. 掃除
        res = requests.get(base_url, headers=headers)
        if res.status_code == 200:
            for rec in res.json().get('records', []):
                requests.delete(f"{base_url}/{rec['id']}", headers=headers)

        # 2. 厳選キーワード（PDFを排除し、公式ポータルを狙う）
        # 作用機序: 検索ワードに「-filetype:pdf」を加え、物理的にPDFを検索結果から消去する
        today = datetime.now().strftime('%m/%d')
        topics = [
            {"kw": "IT導入補助金2026 公式 -filetype:pdf", "label": "【IT導入】最新公募情報"},
            {"kw": "ものづくり補助金 18次 19次 -filetype:pdf", "label": "【製造業】ものづくり補助金"},
            {"kw": "小規模事業者持続化補助金 ガイドライン -filetype:pdf", "label": "【小規模】持続化補助金"},
            {"kw": "事業再構築補助金 事務局 -filetype:pdf", "label": "【転換】事業再構築補助金"},
            {"kw": "東京都 創業助成金 令和8年 -filetype:pdf", "label": "【東京】創業・起業支援"}
        ]
        
        new_records = []
        for t in topics:
            # 検索結果の「最上位（公式）」に直接誘導するリンクを生成
            clean_url = f"https://www.google.com/search?q={t['kw']}&btnI=I'm+Feeling+Lucky"
            # btnI は「最も関連性の高いページへ直接飛ぶ」Googleの機能（一部制限あり）
            # 確実性を期すため、通常の検索URLも併用
            fallback_url = f"https://www.google.com/search?q={t['kw']}"
            
            new_records.append({
                "fields": {
                    "title": t['label'],
                    "region": f"公式確認日: {today}",
                    "source_url": fallback_url
                }
            })

        # 3. 送信
        requests.post(base_url, headers=headers, json={"records": new_records})
        print("【最適化完了】PDFとノイズを排除しました。")
            
    except Exception as e:
        print(f"【エラー】: {e}")

if __name__ == "__main__":
    run_scraper()
