from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from database import save_message, get_messages
from ai_core import process_message
import asyncio

app = FastAPI(title="OpenClaw")

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    messages = get_messages()
    rows = ""
    for m in messages:
        rows += f"""
        <tr>
            <td>{m.created_at.strftime('%m/%d %H:%M')}</td>
            <td>{m.content[:30]}...</td>
            <td>{m.category}</td>
            <td>{m.priority}</td>
            <td>{'🤖' if m.engine=='claude' else '💻'}</td>
        </tr>"""
    return f"""
    <html>
    <head>
        <title>OpenClaw Dashboard</title>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial; padding: 20px; background: #1a1a2e; color: white; }}
            h1 {{ color: #00d4ff; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th {{ background: #16213e; padding: 10px; }}
            td {{ padding: 8px; border-bottom: 1px solid #333; }}
        </style>
    </head>
    <body>
        <h1>🦀 OpenClaw Dashboard</h1>
        <table>
            <tr>
                <th>時間</th><th>メッセージ</th>
                <th>カテゴリ</th><th>優先度</th><th>AI</th>
            </tr>
            {rows}
        </table>
    </body>
    </html>"""

@app.post("/message")
async def receive_message(request: Request):
    data = await request.json()
    text = data.get("message", "")
    result = await process_message(text)
    
    # DB保存
    save_message(
        content=text,
        category=result.get("result", "その他"),
        summary=result.get("result", ""),
        priority="高" if result["engine"] == "claude" else "中",
        eng=result["engine"]
    )
    return {"status": "ok", "result": result}
