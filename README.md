# twins-notifier-via-line-official
 TWINSの新規通知をLINE公式アカウント経由で送信するプログラムです。


## 導入手順
1. 仮想環境の構築とライブラリのインストール
仮想環境を構築したら最初にターミナルから以下を実行してライブラリをインストールしてください。
```
pip install -r requirements.txt
```

2. LINE公式アカウントの用意
公式ドキュメント等を参考に、LINE公式アカウントを用意してください。

3. メッセージ送信先の　LINE User ID を取得。
このサイト(https://zenn.dev/akid/scraps/273eaa58e3be58)を参考に、メッセージを送りたい全てのユーザーのIDを取得してください。

4. .envファイルの準備
.env-example ファイルの各変数をあなた自身の情報に書き換え、.env ファイルとして保存してください。

5. プログラムの実行
main.py をcronなどで定時実行してください！
