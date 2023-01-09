## gcf-daily_update_redmine
GCF-daily_update_redmine

main.py -> 
    daily_update_redmine.py ->
         duplicate_issues.py ->
            chrome_scraping.py


# アップデートの方法
1. Githubにアップロード
    * vscodeで
1. deploy in Google Cloud SHELL GPCにログインし、クラウドSHELLにて以下の操作をする！

    1. 一番最初だけ（2回目以降は不要）
    ```
    git clone https://github.com/takumihomma/gcf-daily_update_redmine
    （最初だけ。Gitに同期したあと、そのファイルをGCPにアップロード）
    ```
    1. 毎回行う
    ```
    cd gcf-daily_update_redmine
    git pull
    sh deploy.sh  -> cloud SHELLの承認ボタンを押す。デプロイに時間がかかる
    ```
    1. デプロイが終わったら正常稼働を確認する

    1. 不要になった古いコンテナイメージを削除する
        1. [Container Registory](https://console.cloud.google.com/gcr/images/zsol22/asia/gcf/asia-northeast2/92df3395-3fc3-400e-b7c3-ed244feca1d6?hl=ja&project=zsol22)にアクセスして古いものを削除

