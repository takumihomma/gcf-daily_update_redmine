#import json
import os
import time
from selenium import webdriver
#from google.cloud import storage

#%% 標準
#! pip install python_redmine pandas
"""使い方:  $ python3 daily_update_redmine.py
"""
from datetime import datetime
import pandas as pd
from redminelib import Redmine
from pandas.tseries.offsets import DateOffset
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome import service as fs
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time

#%% ----- 設定ymlの読込 -----
import yaml
def read_yml(ymlfile):
    with open(ymlfile) as file:
        yml = yaml.safe_load(file)
    URL = yml['redmine']['url']
    API_KEY = yml['redmine']['API_key']
    USERNAME = yml['redmine']['username']
    PASSWORD = yml['redmine']['password']
    every1m = yml['redmine']['recurring']['every1m']
    every3m = yml['redmine']['recurring']['every3m']
    every6m = yml['redmine']['recurring']['every6m']
    every12m = yml['redmine']['recurring']['every12m']
    spot = yml['redmine']['recurring']['spot']
    copied = yml['redmine']['recurring']['copied']
    data = yml['redmine']['recurring']['data']
    return {'URL':URL, \
        'API_KEY':API_KEY, \
        'USERNAME':USERNAME, \
        'PASSWORD':PASSWORD, \
        'every1m':every1m, \
        'every3m':every3m, \
        'every6m':every6m, \
        'every12m':every12m, \
        'spot':spot, \
        'copied':copied, \
        'data':data}


#%% # リソースセットをデータフレームに変換
def resourceset2df(resourceset):
    df_row = pd.DataFrame([], columns=dict(resourceset[0]).keys())
    dict_array = []
    for resource in resourceset:
        data = dict(resource)
        dict_array.append(data)
    df = pd.concat([df_row, pd.DataFrame.from_dict(dict_array)])
    return df

#%% # プロジェクト一覧をｄｆとして取得（権限のあるPAYBOOK と 原則 のみ取得できる）
def projects2df(redmine):
    return resourceset2df(redmine.project.all())

#projects2df()[['id','identifier','name']]
#%% # ユーザー一覧をｄｆとして取得
def users2df(redmine):
    users2df = resourceset2df(redmine.user.all())
    return users2df

#users2df()[['id','login','lastname','firstname','mail']]

#%% # ステータス一覧をｄｆとして取得
def status2df(redmine):
    status2df = resourceset2df(redmine.issue_status.all())
    return status2df

#status2df()

#%% # トラッカー一覧をｄｆとして取得
def trackers2df(redmine):
    trackers2df = resourceset2df(redmine.tracker.all())
    return trackers2df

#trackers2df().head(2)

#%% # カスタムフィールド一覧をｄｆとして取得
def custom_fields2df(redmine):
    custom_fields2df = resourceset2df(redmine.custom_field.all())
    return custom_fields2df

#custom_fields2df()[['id','name','possible_values', 'trackers']]
#custom_fields2df()['possible_values'][0][1]['value']
#%%
# # バージョン一覧をｄｆとして取得（プロジェクトごと）
"""
def versions2df(redmine, project_id):
    result = redmine.version.filter(project_id=project_id)
    print(result)
    result = resourceset2df(result)
    result['due_date'] = pd.to_datetime(result['due_date'], format='%Y-%m-%d') #日付型に変更
    return result

versions2df('template')
# -> Requested resource is forbidden --> IDに欠損値があるから?
# project"原則"のメンバーに管理者を追加してもだめ
"""

#%%
# # チケット一覧をｄｆとして取得
def issues2df(redmine):
    issues2df = resourceset2df(redmine.issue.all())
    """ カスタムフィールド
    0 [{'id':1,  'name':'定期業務分類',  'value':'年12'}]
    1 NaN
    2 [{'id':2,  'name':'繰り返し区分',  'value':'1', 'label':'毎月'}]
    3 ...
    """

    issues2df['due_date'] = pd.to_datetime(issues2df['due_date'], format='%Y-%m-%d') #日付型に変更
    issues2df['start_date'] = pd.to_datetime(issues2df['start_date'], format='%Y-%m-%d')
    issues2df['closed_on'] = pd.to_datetime(issues2df['closed_on'], format='%Y-%m-%d').dt.date

    projects2df = resourceset2df(issues2df['project'])
    projects2df = projects2df.rename(columns={'id': 'project_id', 'name': 'project_name'})
    issues_df = pd.merge(issues2df, projects2df, left_index=True, right_index=True)

    tracker2df = resourceset2df(issues2df['tracker'])
    tracker2df = tracker2df.rename(columns={'id': 'tracker_id', 'name': 'tracker_name'})
    issues_df = pd.merge(issues_df, tracker2df, left_index=True, right_index=True)

    status2df = resourceset2df(issues2df['status']) 
    status2df = status2df.rename(columns={'id': 'status_id', 'name': 'status_name'})
    issues_df = pd.merge(issues_df, status2df, left_index=True, right_index=True)
# ----- バージョン -----
#    version2df = resourceset2df(issues2df['fixed_version']) 
#    version2df = version2df.rename(columns={'id': 'version_id', 'name': 'version_name'})
#    issues_df = pd.merge(issues_df, version2df, left_index=True, right_index=True)

#    print(issues_df[['id','custom_fields']].sample(3))
# ------カスタムフィールド------
    cf0 = issues_df['custom_fields']
    dict_array = []
    for resource in cf0:
        data = dict(resource[0])
        # 'float' object is not subscriptable --> 欠損データがNaNなのでfloatとされる
        # トラッカーやプロジェクトを追加した際にカスタムフィールドを見直し、すべて選択されていないとエラーになる
        dict_array.append(data)
    cf0 = pd.DataFrame.from_dict(dict_array)
    cf0 = cf0.rename(columns={'id': 'cf0_id', 'name': 'cf0_name', 'value': 'cf0_value'})

    issues_df = pd.merge(issues_df, cf0, left_index=True, right_index=True)

    return issues_df

#df_issues = issues2df().sample(3)
#print(df_issues[['project_id','subject','cf0_value']])
#print(df_issues[['project_name','subject']])
#print(df_issues[['start_date','due_date', 'status_name']])
#print(df_issues[['closed_on', 'id']])

#%% 
""" 行いたい作業（追加したい機能）
1. 作業を抽出（繰り返し区分「毎月〜毎年」）（ステータス未了を含む）
2.①繰り返し区分が「毎月」の場合、開始日から1ヶ月を経過したらチケットをコピー
  （新しいチケットの開始日・期日・ステータスを更新。古いチケットの繰り返し区分を「複製済」に変更）
  ②繰り返し区分が「3ヶ月ごと」の場合、開始日から3ヶ月を経過したらチケットをコピー（以下同じ）
  …
繰り返し区分value: 1毎月、5３ヶ月ごと、6半年ごと、2毎年、3SPOT、4データ、7複製済
 http://（URL)/projects/(project_name)/issues/(no.)/copy にて新規コピーできる
 project_name は identifier のほか project_id(num) でもよさげ。
"""

#%% -------LOGIN--------
def login_redmine(driver, url, username, password):
    driver.get(url)
    WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located)
    user = driver.find_element(by=By.ID, value='username')
    user.send_keys(username)
    pswd = driver.find_element(by=By.ID, value='password')
    pswd.send_keys(password)
    driver.find_element(by=By.ID, value='login-submit').click()
    WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located)

#%% -------Duplicate Issue--------
def duplicate_issue(driver, page,start_dateY, start_dateM, start_dateD, due_dateY, due_dateM, due_dateD):
    # 前回の作成で年が「2022」にならず「0002」になってしまうバグがある。年が1000未満の場合にはチケットが作成できないため、2020を加算する
    if start_dateY < 2020:
        start_dateY = start_dateY + 2020
    if due_dateY < 2020:
        due_dateY = due_dateY + 2020

    driver.get(page)
    WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located)
    target = driver.find_element(by=By.ID, value='issue_start_date')
    target.send_keys(start_dateY)
    target.send_keys(Keys.TAB)
    target.send_keys(start_dateM)
    target.send_keys(start_dateD)
    target = driver.find_element(by=By.ID, value='issue_due_date')
    target.send_keys(due_dateY)
    target.send_keys(Keys.TAB)
    target.send_keys(due_dateM)
    target.send_keys(due_dateD)
    time.sleep(1)
    driver.find_element(by=By.NAME, value='commit').click()
    WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located)

#%% -----日付型を文字列に変更------
def date2str(date: datetime):
    year = date.strftime("%Y")
    month = date.strftime("%m")
    day = date.strftime("%d")
    return [year, month, day]



def main(request):

    # chrome_options
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--hide-scrollbars')
    chrome_options.add_argument('--enable-logging')
    chrome_options.add_argument('--log-level=0')
    chrome_options.add_argument('--v=99')
    chrome_options.add_argument('--single-process')
    chrome_options.add_argument('--ignore-certificate-errors')
#    chrome_options.add_experimental_option("w3c", False)   # bug対策 headless-chromium のバージョンが合わない場合にこれを加えるといいらしい
    chrome_options.binary_location = os.getcwd() + "/headless-chromium"

#    chrome_service = fs.Service(executable_path=ChromeDriverManager().install())
#    driver = webdriver.Chrome(service = chrome_service, options=chrome_options)
    driver = webdriver.Chrome(os.getcwd() + "/chromedriver", chrome_options=chrome_options)

    setting = read_yml('setting.yml')
    URL = setting['URL']
    API_KEY = setting['API_KEY']
    USERNAME = setting['USERNAME']
    PASSWORD = setting['PASSWORD']
    every1m = setting['every1m']
    every3m = setting['every3m']
    every6m = setting['every6m']
    every12m = setting['every12m']
    spot = setting['spot']
    copied = setting['copied']
    data = setting['data']

    redmine = Redmine(URL,key=API_KEY)


    #%% ----- カスタムフィールドによるチケット抽出 -----
    df_issues = issues2df(redmine)
    df_issues = df_issues[ \
        (df_issues['cf0_value'] != spot) & \
        (df_issues['cf0_value'] != data) & \
        (df_issues['cf0_value'] != copied) ]     # 3 SPOT 4 データ 7 複製済のいずれでもないものを抽出
    print('対象data数: ', len(df_issues.index))



    #%% -----各行について複製をする日を判定し、新しい開始日と期日をセットする-----

    # -----スクレイピング開始-----
    login_redmine(driver, URL, USERNAME, PASSWORD)

    # -----データのアップデート -----
    count = 0
    info = ""
    for row in range(len(df_issues)):
        target_series = df_issues.iloc[row]
        if target_series['cf0_value'] == every1m:   #cf0_value=1 毎月
            set = 1
        elif target_series['cf0_value'] == every3m: # cf0_value=5 3ヶ月ごと
            set = 3
        elif target_series['cf0_value'] == every6m: # ch0_value=6 半年ごと
            set = 6
        elif target_series['cf0_value'] == every12m: # cf0_value=2 12ヶ月ごと
            set = 12
        else:
            continue

        # ----- duplicate_issues ----- URL, ID, PASSWORD, PROJECT_ID, ISSUE_ID, START_DATE, DUE_DATE
        lasttime = datetime.today() - DateOffset(months=set)
        if target_series['start_date'] <= lasttime:
            START = target_series['start_date'] + DateOffset(months=set)
    #        print("Due type is : " , type(target_series['due_date']))
            DUE = target_series['due_date'] + DateOffset(months=set)
    #        print(target_series[['id', 'project_id', 'cf0_value', 'start_date', 'due_date', ]])
            PROJECT = str(target_series['project_id'])
            ISSUE = str(target_series['id'])
            startY = date2str(START)[0]
            startM = date2str(START)[1]
            startD = date2str(START)[2]
            try:
                dueY = date2str(DUE)[0]
                dueM = date2str(DUE)[1]
                dueD = date2str(DUE)[2]
            except: # 期日が未指定の場合は空欄のまま
                dueY = ""
                dueM = ""
                dueD = ""

            page = URL + '/projects/' + PROJECT + '/issues/' + ISSUE + '/copy'
            duplicate_issue(driver, page, startY, startM, startD, dueY, dueM, dueD)

            # ----- 複写元チケットの「繰り返し区分」を「複写済」にする -----
            redmine.issue.update(
                df_issues.iloc[row]['id'], # issue_id (必須)
                custom_fields=[{'id': 2, 'value': '7'}],
                )
            count += 1
            info = info + "\n" + startY + startM + startD +"-"+ dueY + dueM + dueD + ":" + target_series['subject']
        else:
            pass

    driver.quit()
    return '複写処理数：' + str(count) + "\n" + info






if __name__ == '__main__':
    main('some')