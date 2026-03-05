import httpx
import anthropic
import os

# Claude APIクライアント
claude = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# メッセージの重要度を判定
def is_important(message: str) -> bool:
    keywords = ["緊急", "重要", "至急", "お願い", "締切", "urgent", "asap"]
    return any(kw in message.lower() for kw in keywords)

# ローカルAI（Ollama）で分類
async def classify_local(message: str) -> str:
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2",
                "prompt": f"""以下のメッセージを分類してください。
カテゴリ：仕事 / 友人 / 家族 / 緊急 / その他
メッセージ：{message}
カテゴリ名だけ答えてください。""",
                "stream": False
            }
        )
        return response.json()["response"].strip()

# Claude APIで高精度分析
def analyze_claude(message: str) -> str:
    response = claude.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=200,
        messages=[{
            "role": "user",
            "content": f"""以下のLINEメッセージを分析してください。
・カテゴリ（仕事/友人/家族/緊急/その他）
・要約（1行）
・優先度（高/中/低）

メッセージ：{message}"""
        }]
    )
    return response.content[0].text

# ハイブリッド判定メイン関数
async def process_message(message: str) -> dict:
    if is_important(message):
        # 重要メッセージ → Claude API（高精度）
        result = analyze_claude(message)
        engine = "claude"
    else:
        # 一般メッセージ → Ollama（ローカル・無料）
        result = await classify_local(message)
        engine = "ollama"
    
    return {
        "message": message,
        "result": result,
        "engine": engine
    }
