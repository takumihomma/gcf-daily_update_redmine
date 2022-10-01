# ! pip install webdriver_manager chromedriver-binary chromedriver-binary-auto selenium
"""使い方:        driver = Chrome().driver
"""
#%%
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver  # chromedriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome import service as fs
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import base64
import time, os

#%%
class Chrome:
    # Ubuntu用 SELENIUMをあらゆる環境で起動させるCHROMEオプション
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--allowed_ips')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-extensions')
#    chrome_options.add_argument('--proxy-server="direct://"')
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument('--kiosk-printing') #印刷ダイアログが開くと、印刷ボタンを無条件に押す。
    chrome_options.add_argument('--hide-scrollbars')
    chrome_options.add_argument('--enable-logging')
    chrome_options.add_argument('--log-level=0')
    chrome_options.add_argument('--single-process')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.binary_location = os.getcwd() + "/headless-chromium"
    
    DL = os.getcwd() + '/data'
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": DL \
        })
    # -----ドライバー起動-----
    chrome_service = fs.Service(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(
        service = chrome_service,
        options=chrome_options
        )

    # 要素をクリック
    def target_click(self, targetElement):
        time.sleep(1)
        self.driver.execute_script("arguments[0].click();", targetElement)

    # 特定のVALUE属性の値を持つタグの要素を探す
    def attribute_search(self, tagname, attribute, value):
        elements = self.driver.find_elements(by=By.TAG_NAME, value=tagname)
        targetElement = 0
        for element in elements:
            target = element.get_attribute(attribute)
            if target == value:
                targetElement = element
        return targetElement

    # 特定のテキストを持つタグの要素を探す
    def tagtext_search(self, tagname, tagtext):
        elements = self.driver.find_elements(by=By.TAG_NAME, value=tagname)
        targetElement = 0
        for element in elements:
            text = element.text
            if text == tagtext:
                targetElement = element
                break
        return targetElement

    # セレクターをクリック
    def selector_click(self, selector):
        element = self.driver.find_element(by=By.CSS_SELECTOR, value=selector)
        element.click()

    # PDFに保存
    def save2pdf(self, driver, file_path):
        time.sleep(1)
        parameters = {}
        parameters = {
            "printBackground": True, # 背景画像を印刷
            "paperWidth": 8.27, # A4用紙の横 210mmをインチで指定
            "paperHeight": 11.69, # A4用紙の縦 297mmをインチで指定
            "displayHeaderFooter": True, # 印刷時のヘッダー、フッターを表示
        }
        # Chrome Devtools Protocolコマンドを実行し、取得できるBase64形式のPDFデータをデコードしてファイルに保存
        pdf_base64 = driver.execute_cdp_cmd("Page.printToPDF", parameters)
        pdf = base64.b64decode(pdf_base64["data"])
        with open(file_path, 'bw') as f:  # b:バイナリモード(t:テキスト)
            f.write(pdf)
            print(file_path, '  のPDF化が完了')

    import json
    import time
    def PrintSetUp(self):
        #印刷としてPDF保存する設定
        chopt=webdriver.ChromeOptions()
        # PDF印刷設定
        appState = {
            "recentDestinations": [
                {
                    "id": "Save as PDF",
                    "origin": "local",
                    "account":""
                }
            ],
            "selectedDestinationId": "Save as PDF",
            "version": 2,
            "isLandscapeEnabled": True, #印刷の向きを指定 tureで横向き、falseで縦向き。
            "pageSize": 'A4', #用紙タイプ(A3、A4、A5、Legal、 Letter、Tabloidなど)
            #"mediaSize": {"height_microns": 355600, "width_microns": 215900}, #紙のサイズ　（10000マイクロメートル = １cm）
            #"marginsType": 0, #余白タイプ #0:デフォルト 1:余白なし 2:最小
            #"scalingType": 3 , #0：デフォルト 1：ページに合わせる 2：用紙に合わせる 3：カスタム
            #"scaling": "141" ,#倍率
            #"profile.managed_default_content_settings.images": 2,  #画像を読み込ませない
            "isHeaderFooterEnabled": False, #ヘッダーとフッター
            "isCssBackgroundEnabled": True, #背景のグラフィック
            #"isDuplexEnabled": False, #両面印刷 tureで両面印刷、falseで片面印刷
            #"isColorEnabled": True, #カラー印刷 trueでカラー、falseで白黒
            #"isCollateEnabled": True #部単位で印刷
        }
        # ドライバへのPDF印刷設定の適用
        prefs = {'printing.print_preview_sticky_settings.appState':
                'json.dumps(appState)',
                "download.default_directory": "/projects/data"
                } #appState --> pref
        chopt.add_experimental_option('prefs', prefs) #prefs --> chopt
        chopt.add_argument('--kiosk-printing') #印刷ダイアログが開くと、印刷ボタンを無条件に押す。
        return chopt

    def html2PDF(self, source):
        #Web ページもしくはhtmlファイルをPDFにSeleniumを使って変換する
        driver = self.driver
        driver.implicitly_wait(10) # 秒 暗示的待機 
        driver.get(source) #ブログのURL 読み込み
        WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located)  # ページ上のすべての要素が読み込まれるまで待機（15秒でタイムアウト判定）
        driver.execute_script('return window.print()') #Print as PDF
        print('done')
        time.sleep(10) #ファイルのダウンロードのために10秒待機
        driver.quit() #Close Screen



#%%
if __name__ == '__main__':
    pass
