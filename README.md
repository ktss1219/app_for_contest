# app_for_contest
"ヒリつき"によって起床を促進するbot

## 環境設定
リポジトリのクローン
```python
git clone https://github.com/ktss1219/app_for_contest
cd app_for_contest
```
環境変数の設定(Mac)
```python
export "SLACK_BOT_TOKEN" = <ボットトークン>
export "SLACK_APP_TOKEN" = <アプリレベルトークン>
export "FIREBASE_KEY" = <鍵>
```

各種パッケージのダウンロード
```python
pip install slack_bolt
pip install firebase
```

