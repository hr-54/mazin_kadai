from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

app = FastAPI()

# メモのデータモデル
class Memo(BaseModel):
    id: int
    content: str

# メモを保存するリスト（仮のデータベース）
memos = []

# メモ登録
@app.post("/memos")
def create_memo(memo: Memo):
    if any(m.id == memo.id for m in memos):
        raise HTTPException(status_code=400, detail="ID already exists")
    memos.append(memo)
    return {"message": "Memo created", "memo": memo}

# メモ検索（キーワードでフィルタ）
@app.get("/memos")
def list_memos(keyword: str = Query(None, description="検索キーワード")):
    if keyword:
        result = [m for m in memos if keyword.lower() in m.content.lower()]
        return {"memos": result}
    return {"memos": memos}

# メモ削除
@app.delete("/memos/{memo_id}")
def delete_memo(memo_id: int):
    global memos
    memos = [m for m in memos if m.id != memo_id]
    return {"message": f"Memo {memo_id} deleted"}

# メモ要約（30文字以内で切り出す簡易版）
@app.post("/memos/{memo_id}/summary")
def summarize_memo(memo_id: int):
    for m in memos:
        if m.id == memo_id:
            content = m.content
            summary = content[:30] + "..." if len(content) > 30 else content
            return {"id": memo_id, "summary": summary}
    raise HTTPException(status_code=404, detail="Memo not found")