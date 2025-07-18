# RSS to X GitHub Actions

Anchor.fmのRSSフィードを取得して、新しいエピソードをX（Twitter）に自動投稿するGitHub Actionsワークフローです。

## 機能

- 10分ごとにRSSフィードをチェック
- 新しいエピソードを自動でXに投稿
- 重複投稿を防ぐためのdigest機能
- 手動実行も可能

## セットアップ

### 1. X API認証情報の取得

X Developer Portalでアプリケーションを作成し、以下の認証情報を取得してください：

1. [X Developer Portal](https://developer.twitter.com/)にアクセス
2. 新しいアプリケーションを作成
3. 以下の認証情報を取得：
   - API Key
   - API Secret
   - Access Token
   - Access Token Secret

### 2. GitHub Repository Secretsの設定

複数アカウントでの投稿に対応しています。各アカウントごとに以下のシークレットをGitHubリポジトリのSettings > Secrets and variables > Actionsで設定してください：

#### RIDDLE アカウント
| シークレット名                 | 説明                  | 保存するデータ                                  |
| ------------------------------ | --------------------- | ----------------------------------------------- |
| `X_API_KEY_RIDDLE`             | X API Key             | X Developer Portalで取得したAPI Key             |
| `X_API_SECRET_RIDDLE`          | X API Secret          | X Developer Portalで取得したAPI Secret          |
| `X_ACCESS_TOKEN_RIDDLE`        | X Access Token        | X Developer Portalで取得したAccess Token        |
| `X_ACCESS_TOKEN_SECRET_RIDDLE` | X Access Token Secret | X Developer Portalで取得したAccess Token Secret |

#### HIBINO アカウント
| シークレット名                 | 説明                  | 保存するデータ                                  |
| ------------------------------ | --------------------- | ----------------------------------------------- |
| `X_API_KEY_HIBINO`             | X API Key             | X Developer Portalで取得したAPI Key             |
| `X_API_SECRET_HIBINO`          | X API Secret          | X Developer Portalで取得したAPI Secret          |
| `X_ACCESS_TOKEN_HIBINO`        | X Access Token        | X Developer Portalで取得したAccess Token        |
| `X_ACCESS_TOKEN_SECRET_HIBINO` | X Access Token Secret | X Developer Portalで取得したAccess Token Secret |

#### アカウント数の調整

アカウント数を変更する場合は、`.github/workflows/rss-to-x.yml`の以下の部分を編集してください：

```yaml
strategy:
  matrix:
    account: [RIDDLE, HIBINO] # アカウント名を変更
```

### 3. ワークフローの実行

- 自動実行：10分ごとに自動で実行されます
- 手動実行：GitHub Actionsページから手動で実行可能です
