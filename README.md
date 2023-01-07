# gcf-daily_update_redmine
GCF-daily_update_redmine

main.py -> 
    daily_update_redmine.py ->
         duplicate_issues.py ->
            chrome_scraping.py


# deploy in Google Cloud SHELL GPCにログインし、クラウドSHELLにて以下の操作をする！
git clone https://github.com/takumihomma/gcf-daily_update_redmine　（最初だけ。Gitに同期したあと、そのファイルをGCPにアップロード）
cd gcf-daily_update_redmine
git pull
sh deploy.sh