import os
from notion_client import Client

notion = Client(auth=os.environ.get('NOTION_API_KEY'))
DATABASE_ID = os.environ.get('NOTION_DATABASE_ID')

def add_task(title, status='未着手', priority='中'):
    notion.pages.create(
        parent={'database_id': DATABASE_ID},
        properties={
            'タスク名': {'title': [{'text': {'content': title}}]},
            'ステータス': {'status': {'name': status}},
            '優先度': {'select': {'name': priority}}
        }
    )
    print(f'✅ タスク追加完了: {title}')

def list_tasks():
    results = notion.databases.retrieve(database_id=DATABASE_ID)
    print(f'✅ データベース接続成功: {results["title"][0]["plain_text"]}')

if __name__ == '__main__':
    list_tasks()
    add_task('OpenClaw Notion連携テスト', '進行中', '高')
