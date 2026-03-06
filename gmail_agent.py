import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import anthropic
import base64
import re

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify'
]

client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

def get_gmail_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def get_email_body(message):
    if 'parts' in message['payload']:
        for part in message['payload']['parts']:
            if part['mimeType'] == 'text/plain':
                data = part['body'].get('data', '')
                return base64.urlsafe_b64decode(data).decode('utf-8')
    else:
        data = message['payload']['body'].get('data', '')
        if data:
            return base64.urlsafe_b64decode(data).decode('utf-8')
    return ''

def analyze_email(subject, body, sender):
    prompt = f"""以下のメールを分析してください。

送信者: {sender}
件名: {subject}
本文: {body[:1000]}

以下のJSON形式で返してください：
{{
    "category": "仕事/個人/広告/通知/緊急",
    "priority": "高/中/低",
    "summary": "メールの要約（2-3文）",
    "action_needed": true/false,
    "suggested_reply": "返信が必要な場合の返信文（不要な場合はnull）"
}}"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    try:
        result = json.loads(response.content[0].text)
    except:
        result = {
            "category": "不明",
            "priority": "中",
            "summary": response.content[0].text,
            "action_needed": False,
            "suggested_reply": None
        }
    return result

def process_emails(max_emails=5):
    service = get_gmail_service()
    results = service.users().messages().list(
        userId='me', 
        maxResults=max_emails,
        q='is:unread'
    ).execute()
    
    messages = results.get('messages', [])
    
    if not messages:
        print('📭 未読メールはありません')
        return
    
    print(f'📬 未読メール {len(messages)}件を処理します\n')
    
    for msg in messages:
        message = service.users().messages().get(
            userId='me', 
            id=msg['id'],
            format='full'
        ).execute()
        
        headers = message['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '件名なし')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), '不明')
        body = get_email_body(message)
        
        print(f'📧 件名: {subject}')
        print(f'👤 送信者: {sender}')
        
        analysis = analyze_email(subject, body, sender)
        
        print(f'📁 カテゴリ: {analysis["category"]}')
        print(f'⚡ 優先度: {analysis["priority"]}')
        print(f'📝 要約: {analysis["summary"]}')
        print(f'✅ 対応必要: {analysis["action_needed"]}')
        
        if analysis.get('suggested_reply'):
            print(f'💬 返信案: {analysis["suggested_reply"][:100]}...')
        
        print('-' * 50)

if __name__ == '__main__':
    process_emails()
