import os
import base64
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify'
]

ACCOUNTS = {
    1: 'ipa.aka.try@gmail.com',
    2: 'syorinmedical@gmail.com',
    3: 'hti.ippa@gmail.com',
    4: 'hainan.hti.ippa@gmail.com',
    5: 'hainan.ippa@gmail.com',
}

def get_service(account_num):
    token_file = f'token_{account_num}.json'
    creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return build('gmail', 'v1', credentials=creds)

def get_unread_emails(account_num, max_results=3):
    service = get_service(account_num)
    results = service.users().messages().list(
        userId='me', q='is:unread', maxResults=max_results
    ).execute()
    
    messages = results.get('messages', [])
    emails = []
    for msg in messages:
        message = service.users().messages().get(
            userId='me', id=msg['id'], format='full'
        ).execute()
        headers = message['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '件名なし')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), '不明')
        emails.append({'subject': subject[:40], 'sender': sender[:40]})
    return emails

if __name__ == '__main__':
    print('=== 全アカウント未読メール確認 ===\n')
    for num, email in ACCOUNTS.items():
        print(f'📧 アカウント{num}: {email}')
        try:
            emails = get_unread_emails(num)
            if emails:
                for e in emails:
                    print(f'  - {e["subject"]}')
            else:
                print('  未読メールなし')
        except Exception as ex:
            print(f'  エラー: {ex}')
        print()
