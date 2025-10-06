Python/FastAPIを用いて実装したAIメモアシスタントのAPIです。
必須課題の最終コードはmain3.pyに格納されています。

・POST/memosでidと内容を登録

・GET/memosで
キーワードを指定し、保存しているメモ内にそのキーワードがあればそのメモを表示（検索）、
キーワードを指定しなければ、保存しているメモをすべて表示（一覧）

・DELETEで/memos/{id}で入力したidのメモを削除

・POST/memos/{id}/summaryで入力したidのメモをgeminiで要約
