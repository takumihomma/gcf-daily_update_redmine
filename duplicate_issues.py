from datetime import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

#%% ----- Chrome Driver Start -----
import chrome_scraping
driver = chrome_scraping.Chrome().driver
"""上の一行があるために、importしただけで動いてしまう。
これをdef関数化するためには、他の関数で使っている変数をすべて修正する必要がある。
"""

#%% -------LOGIN--------
def login_redmine(url, username, password):
    driver.get(url)
    WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located)
    driver.find_element(by=By.ID, value='username').send_keys(username)
    driver.find_element(by=By.ID, value='password').send_keys(password)
    driver.find_element(by=By.ID, value='login-submit').click()
    WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located)

#%% -------Duplicate Isuue--------
def duplicate_issue(page,start_dateY, start_dateM, start_dateD, due_dateY, due_dateM, due_dateD):
    driver.get(page)
    WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located)
    driver.find_element(by=By.ID, value='issue_start_date').send_keys(start_dateY,Keys.TAB, start_dateM, start_dateD)
    driver.find_element(by=By.ID, value='issue_due_date').send_keys(due_dateY, Keys.TAB, due_dateM, due_dateD)
    time.sleep(1)
    driver.find_element(by=By.NAME, value='commit').click()
    WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located)

#%% -----日付型を文字列に変更------
def date2str(date: datetime):
    year = date.strftime("%Y")
    month = date.strftime("%m")
    day = date.strftime("%d")
    return [year, month, day]

def quit_chrome():
    driver.quit()

#%%
if __name__ == '__main__':
    pass
