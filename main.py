import os
import requests
from bs4 import BeautifulSoup

def run_scraper():
    AIRTABLE_TOKEN = os.getenv('AIRTABLE_TOKEN')
    AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
    AIRTABLE_TABLE_NAME = os.getenv('AIRTABLE_TABLE_NAME')
    
    # ターゲット：東京くらしWEB（東京都 助成・補助金一覧）
    # 理由：行政サイトの中でも構造がシンプルで、スクレイピング遮断が少ない
    TARGET_URL = "https://www.shouhiseikatu.metro.tokyo.lg.jp/sodan/jyosei/"
    
    try:
        print(f"DEBUG: {TARGET_URL} をスキャン中...")
        res = requests.get(TARGET_URL, timeout=20)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        records = []
        # 東京都のサイト構造：dlタグ内のdt/ddに情報がある
        items = soup.find_all('dt')
        
        for dt in items[:5]:
            link_tag = dt.find('a')
            if link_tag:
                title = link_tag.get_text(strip=True)
                href = link_tag.get('href')
                full_url = "https://www.shouhiseikatu.metro.tokyo.lg.jp/sodan/jyosei/" + href
                
                records.append({
                    "fields": {
                        "title": title,
                        "region": "東京都",
                        "source_url": full_url
                    }
                })

        if not records:
            print("【失敗】東京都のサイトからも抽出できませんでした。")
            return

        # Airtable送信
        airtable_url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
        headers = {"Authorization": f"Bearer {AIRTABLE_TOKEN}", "Content-Type": "application/json"}
        response = requests.post(airtable_url, headers=headers, json={"records": records})
        
        if response.status_code == 200:
            print(f"【成功】東京都の情報を {len(records)} 件保存しました。")
        else:
            print(f"【エラー】Airtable: {response.text}")
            
    except Exception as e:
        print(f"【致命的エラー】: {e}")

if __name__ == "__main__":
    run_scraper()
