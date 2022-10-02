set -ex

# Set constants
REGION="asia-northeast2"
FUNCTION_NAME="gcf-daily-update-redmine"

# Deploy the Google Cloud Function
gcloud beta functions deploy ${FUNCTION_NAME} \
    --runtime python37 \
    --region ${REGION} \
    --trigger-http \
    --allow-unauthenticated \
    --memory 2GB \
    --entry-point main \
    --timeout=300s
    --source .

# --gen2
# --trigger-http            # httpトリガー
# --trigger-topic=<TOPIC_NAME>  # Pub/Subが実行されるトピックの名前
# --trigger-event=google.storage... # GCSでトリガーされる４つのトリガーのいずれかを指定
#                 google.storage.object.finalize  # 新しいオブジェクトが作成されたとき
#                 google.storage.object.delete    # オブジェクトが削除されたとき
#                 google.storage.object.archive   # オブジェクトがアーカイブまたは削除されたとき
#                 google.storage.object.metadataUpdate  # オブジェクトのメタデータが更新されたとき
# --trigger-resource        # GCSのバケット名
# --allow-unauthenticated   # パブリック関数に変更、すべての呼び出しを許可する
# --source .                # デプロイするディレクトリを指定
# --entry-point             # Cloud Functionsが実行されたときに最初に実行される関数
# --env-vars-file=.env .yaml  # すべての環境変数の定義を含むYAMLファイルへのパスを指定する
# --timeout                 # デフォルトは60秒。60秒以上かかる処理を実行したい場合に設定する。第2世代では、HTTP関数で最大60分、イベント関数で最大10分までの処理を実行できる
#                           # 第一世代は最大9分
# --memory                  # デフォルトは256MB。スクレイピングなどの重い処理を行う場合に設定する。第2世代では、128MB, 256MB, 512MB, 1024MB, 2048MB, 4096MB, 8192MB, 16384MB
# --source .                # ソースコードの場所を指定すると、関数を更新できる