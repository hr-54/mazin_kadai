from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# データベース接続URL: 現在のフォルダに 'test.db' という名前のSQLiteファイルを作成
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# データベースエンジンを作成（FastAPIでSQLiteを使うためのおまじないを含む）
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# データベース操作（セッション）を管理するためのクラス
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 全てのデータベースモデルが継承する基底クラス
Base = declarative_base()

# データベースに保存するメモのモデル（memosテーブルの設計図）
class DBMemo(Base):
    __tablename__ = "memos" # テーブル名

    # 主キー（primary_key=True）: IDはデータベースが自動で採番します
    id = Column(Integer, primary_key=True, index=True) 
    # メモの本文
    content = Column(String, index=True) 