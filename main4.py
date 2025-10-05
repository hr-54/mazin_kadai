import os
from fastapi import FastAPI, HTTPException, Query, Depends
from pydantic import BaseModel
import google.generativeai as genai
from typing import Generator # データベースセッションで使う型

# データベース設定をインポート
# Note: ファイル名の頭に . を付けることで、同じフォルダ内のファイルを指定
from database import SessionLocal, engine, DBMemo, Base 
from sqlalchemy.orm import Session # データベースセッションの型

# ----------------------------------------------------
# 初期化と依存性注入
# ----------------------------------------------------

app = FastAPI()

# データベースを初期化し、テーブルを作成
Base.metadata.create_all(bind=engine) 

# --- Pydantic モデル: 入力と出力で分ける（データベース連携のため） ---

# ユーザーからの入力データ (IDは不要)
class MemoCreate(BaseModel):
    content: str

# サーバーからの出力データ (IDを含む)
class Memo(BaseModel):
    id: int
    content: str
    
    # SQLAlchemyのモデルと連携するための設定
    class Config:
        orm_mode = True 

# --- データベースセッションをリクエストごとに提供する関数 ---
def get_db() -> Generator:
    db = SessionLocal() # 接続を確立
    try:
        yield db # リクエスト処理中にdbセッションを提供
    finally:
        db.close() # 処理が終わったら接続を必ず閉じる

# ----------------------------------------------------
# LLMサービスの準備（main3.pyからコピペ）
# ----------------------------------------------------

api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# ----------------------------------------------------
# データベースを使ったCRUD (Step 1, 2)
# ----------------------------------------------------

# POST /memos: メモ登録 (リスト操作をDB操作に置き換え)
@app.post("/memos", response_model=Memo)
# Depends(get_db) でデータベース接続を受け取る
def create_memo(memo_data: MemoCreate, db: Session = Depends(get_db)):
    # データベース用オブジェクトを作成（IDはDBが自動採番）
    db_memo = DBMemo(content=memo_data.content) 
    
    db.add(db_memo) 
    db.commit() 
    db.refresh(db_memo) # データベースから自動採番されたIDを取得
    
    # DBMemoオブジェクトをPydanticモデルに変換して返す
    return db_memo

# GET /memos: メモ一覧と検索 (リスト操作をDB操作に置き換え)
@app.get("/memos", response_model=list[Memo])
def read_memos(keyword: str = Query(None, description="検索キーワード"), db: Session = Depends(get_db)):
    if keyword:
        # SQLAlchemyで検索 (LIKE %keyword% に相当)
        # .content.contains() は、大文字・小文字を区別しないことが保証されないため、
        # 厳密には .lower() を使った方が良いですが、ここではシンプルさを優先します。
        memos = db.query(DBMemo).filter(DBMemo.content.contains(keyword)).all()
        return memos
    
    # 全件取得
    memos = db.query(DBMemo).all()
    return memos

# DELETE /memos/{id}: メモ削除 (リスト操作をDB操作に置き換え)
@app.delete("/memos/{id}")
def delete_memo(id: int, db: Session = Depends(get_db)):
    # 削除対象のオブジェクトを取得
    memo_to_delete = db.query(DBMemo).filter(DBMemo.id == id).first()

    if memo_to_delete is None:
        raise HTTPException(status_code=404, detail="Memo not found")
        
    db.delete(memo_to_delete)
    db.commit()
    
    return {"message": "Memo deleted"}

# ----------------------------------------------------
# LLM連携 (要約) - データベースからメモを取得
# ----------------------------------------------------

# POST /memos/{id}/summary: メモ要約 (データベースからメモを取得するように修正)
@app.post("/memos/{id}/summary")
def summarize_memo(id: int, db: Session = Depends(get_db)):
    if not os.getenv("GEMINI_API_KEY"):
         raise HTTPException(status_code=503, detail="LLM APIキーが設定されていません。")

    # データベースからメモを取得
    memo = db.query(DBMemo).filter(DBMemo.id == id).first()

    if not memo:
        raise HTTPException(status_code=404, detail="Memo not found")

    try:
        # メモの内容は memo.content でアクセス
        prompt = f"以下のメモを簡潔に要約してください:\n\n{memo.content}"
        
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        return {"id": id, "summary": response.text}
    except Exception as e:
        print(f"LLM API呼び出しエラー: {e}")
        raise HTTPException(status_code=500, detail="要約処理中にLLM APIエラーが発生しました。")
