import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify'
]

def authenticate_account(account_num, email):
    token_file = f'token_{account_num}.json'
    creds = None
    
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_file, 'w') as f:
            f.write(creds.to_json())
    
    service = build('gmail', 'v1', credentials=creds)
    profile = service.users().getProfile(userId='me').execute()
    print(f'✅ アカウント{account_num}: {profile["emailAddress"]}')
    return service

if __name__ == '__main__':
    accounts = [
        (1, 'アカウント1'),
        (2, 'アカウント2'),
        (3, 'アカウント3'),
        (4, 'アカウント4'),
        (5, 'アカウント5'),
    ]
    
    print('=== Gmail マルチアカウント認証 ===')
    print('各アカウントのブラウザ認証画面が順番に開きます\n')
    
    services = {}
    for num, name in accounts:
        print(f'\n--- アカウント{num} ({name}) の認証 ---')
        input('Enterを押すと認証画面が開きます...')
        services[num] = authenticate_account(num, name)
    
    print('\n✅ 全アカウントの認証完了！')
