from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

app = FastAPI()

# メモのデータモデル
class Memo(BaseModel):
    id: int
    content: str
    # BaseModelによって、idが整数で、内容が文字列を満たしてるかチェック

# メモを保存するリスト（仮のデータベース）
memos = []

# メモ登録
@app.post("/memos")  #@app.post()を使って登録のエンドポイントを定義
def create_memo(memo: Memo):
    for m in memos:
        if m.id == memo.id:
            raise HTTPException(status_code=400, detail="ID already exists")
            #すでに保存しているidで登録しようとしたら例外発生
    memos.append(memo)
    return {"message": "Memo created", "memo": memo}

# メモ検索（キーワードでフィルタ）
@app.get("/memos")
def read_memos(keyword: str = Query(None, description="検索キーワード")):
    if keyword:
        # result = [m for m in memos if keyword in m.content]
        result = []
        for m in memos:
            if keyword in m.content:
                result.append(m)
        return {"memos": result} #キーワードがあればそれを含むものだけのresultを表示
    return {"memos": memos} #キーワードがなければすべて含んだmemeosを表示

# メモ削除
@app.delete("/memos/{id}")
def delete_memo(id: int):
    for m in memos:
        if m.id == id:   #保存してあるメモの中の、入力したidと同じものを削除
            memos.remove(m)
            return {"message": "Memo deleted"}
    raise HTTPException(status_code=404, detail="Memo not found")

# メモ要約
import google.generativeai as genai

# 取得したAPIキーを設定
genai.configure(api_key="取得した実際のAPIキーを入力")  #置き換え

@app.post("/memos/{id}/summary")
def summarize_memo(id: int):
    for m in memos:
        if m.id == id:
            prompt = f"以下のメモを簡潔に要約してください:\n\n{m.content}"
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(prompt)
            return {"id": id, "summary": response.text}
    raise HTTPException(status_code=404, detail="Memo not found")