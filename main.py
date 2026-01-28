import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

def run_scraper():
    AIRTABLE_TOKEN = os.getenv('AIRTABLE_TOKEN')
    AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
    AIRTABLE_TABLE_NAME = os.getenv('AIRTABLE_TABLE_NAME')
    
    # ターゲット：J-Net21 支援情報一覧
    TARGET_URL = "https://j-net21.smrj.go.jp/snavi/support/index.html"
    
    try:
        print(f"DEBUG: {TARGET_URL} をスキャン中...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        res = requests.get(TARGET_URL, headers=headers, timeout=20)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        records = []
        # 修正の核：リンク（<a>タグ）の中から「support」と「entry」を含むものを全て抽出
        all_links = soup.find_all('a', href=re.compile(r'/snavi/support/entry/'))
        
        print(f"DEBUG: 候補リンクを {len(all_links)} 件発見しました。")

        seen_urls = set()
        for link in all_links:
            href = link.get('href')
            full_url = "https://j-net21.smrj.go.jp" + href if href.startswith('/') else href
            
            if full_url in seen_urls: continue
            
            # タイトル取得：リンク内、あるいは隣接するテキストから取得
            title = link.get_text(strip=True)
            if not title or len(title) < 10: # 補助金名として短すぎるものは無視
                continue

            records.append({
                "fields": {
                    "title": title,
                    "region": "全国・広域",
                    "source_url": full_url
                }
            })
            seen_urls.add(full_url)
            if len(records) >= 5: break

        if not records:
            print("【失敗】有効なデータが抽出できませんでした。HTML出力を確認してください。")
            return

        # Airtable送信
        airtable_url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
        headers = {"Authorization": f"Bearer {AIRTABLE_TOKEN}", "Content-Type": "application/json"}
        response = requests.post(airtable_url, headers=headers, json={"records": records})
        
        if response.status_code == 200:
            print(f"【成功】Airtableに {len(records)} 件保存しました。")
        else:
            print(f"【エラー】Airtableレスポンス: {response.text}")
            
    except Exception as e:
        print(f"【致命的エラー】: {e}")

if __name__ == "__main__":
    run_scraper()
