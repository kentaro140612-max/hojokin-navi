import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def run_scraper():
    AIRTABLE_TOKEN = os.getenv('AIRTABLE_TOKEN')
    AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
    AIRTABLE_TABLE_NAME = os.getenv('AIRTABLE_TABLE_NAME')
    
    # 2026年時点の最新URL（支援情報ヘッドライン）
    TARGET_URL = "https://j-net21.smrj.go.jp/snavi/support/index.html"
    
    try:
        print(f"DEBUG: {TARGET_URL} を解析中...")
        res = requests.get(TARGET_URL, timeout=15)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        records = []
        # 論理的アプローチ: 特定のclassではなく、補助金詳細へのリンクを持つ要素を網羅的に探す
        # J-Net21の標準的なリンク形式 '/snavi/support/entry/...' を対象にする
        links = soup.find_all('a', href=True)
        
        seen_urls = set()
        for link in links:
            href = link.get('href')
            # 補助金詳細ページへのリンクパターンを特定
            if '/snavi/support/entry/' in href:
                full_url = "https://j-net21.smrj.go.jp" + href
                if full_url in seen_urls: continue
                
                # タイトル取得（リンク内テキストまたは親要素から）
                title = link.get_text(strip=True)
                if len(title) < 5: continue # 短すぎるテキストは除外
                
                records.append({
                    "fields": {
                        "title": title[:100], # Airtableの制限考慮
                        "region": "全国・広域",
                        "source_url": full_url
                    }
                })
                seen_urls.add(full_url)
                if len(records) >= 5: break # 負荷軽減のため5件

        if not records:
            # バックアッププラン：別のセレクタを試行
            print("DEBUG: 予備の解析ロジックを実行中...")
            # ここでHTML全体を出力して構造を確認（デバッグ用）
            print(f"HTML概要(先頭500文字): {soup.prettify()[:500]}")
            return

        # 3. Airtableへの送信
        airtable_url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
        headers = {"Authorization": f"Bearer {AIRTABLE_TOKEN}", "Content-Type": "application/json"}
        response = requests.post(airtable_url, headers=headers, json={"records": records})
        
        print(f"DEBUG: ステータスコード: {response.status_code}")
        if response.status_code == 200:
            print(f"【成功】{len(records)}件の最新情報を保存しました。")
        else:
            print(f"【失敗】Airtableエラー: {response.text}")
            
    except Exception as e:
        print(f"【致命的エラー】: {e}")

if __name__ == "__main__":
    run_scraper()
