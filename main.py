import os
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

def notify_google():
    try:
        print(f"[{datetime.datetime.now()}] API送信プロセスを開始します。")
        
        # GitHub Actionsが生成した一時的な認証パスを取得
        creds_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        if not creds_path:
            raise ValueError("GOOGLE_APPLICATION_CREDENTIALS が設定されていません。")

        # 権限スコープと認証
        scopes = ['https://www.googleapis.com/auth/indexing']
        credentials = service_account.Credentials.from_service_account_file(creds_path, scopes=scopes)
        
        # Indexing API サービスの構築
        service = build('indexing', 'v1', credentials=credentials)

        # 【ここを修正】インデックスさせたいURLを正確に記述（例：https://example.com/page.html）
        target_url = "あなたのサイトのURL"
        
        body = {
            'url': target_url,
            'type': 'URL_UPDATED'
        }

        # API実行
        print(f"送信中のURL: {target_url}")
        result = service.urlNotifications().publish(body=body).execute()
        print(f"成功レスポンス: {result}")

    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        import sys
        sys.exit(1)

if __name__ == "__main__":
    notify_google()
