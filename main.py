import os
import requests
import xml.etree.ElementTree as ET

def run_scraper():
    AIRTABLE_TOKEN = os.getenv('AIRTABLE_TOKEN')
    AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
    AIRTABLE_TABLE_NAME = os.getenv('AIRTABLE_TABLE_NAME')
    
    # 作用機序: 遮断の多い政府系を避け、API的に開放されているPR TIMESの「補助金・助成金」タグを利用
    RSS_URL = "https://prtimes.jp/main/html/searchrlp/kw/%E8%A3%9C%E5%8A%A9%E9%87%91?output=rss"
    
    try:
        print(f"DEBUG: PR TIMES 補助金フィードを取得中...")
        res = requests.get(RSS_URL, timeout=20)
        res.encoding = 'utf-8'
        
        # 応答がHTML（エラー画面）でないか確認
        if "<html" in res.text.lower():
            print("【失敗】依然としてクラウドIPが制限されています。")
            return

        root = ET.fromstring(res.text)
        records = []
        
        # RSS構造から最新の補助金プレスリリースを5件抽出
        for item in root.findall('.//item')[:5]:
            title = item.find('title').text
            link = item.find('link').text
            
            records.append({
                "fields": {
                    "title": title[:100],
                    "region": "新着プレスリリース",
                    "source_url": link
                }
            })

        if not records:
            print("【失敗】RSSの中身が空でした。")
            return

        airtable_url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
        headers = {"Authorization": f"Bearer {AIRTABLE_TOKEN}", "Content-Type": "application/json"}
        response = requests.post(airtable_url, headers=headers, json={"records": records})
        
        if response.status_code == 200:
            print(f"【成功】PR TIMESから {len(records)} 件取得し、Airtableへ保存しました。")
        else:
            print(f"【エラー】Airtable: {response.text}")
            
    except Exception as e:
        print(f"【致命的エラー】: {e}")

if __name__ == "__main__":
    run_scraper()
