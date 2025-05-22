import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


# Chromeドライバーを起動してie-loveにアクセスする
chrome_options = Options()  # Chromeオプションを作成
# chrome_options.add_argument("--headless")  # headlessモードを有効にするオプションを追加
service = Service('/Users/kota/chromedriver')
service.start()
driver = webdriver.Chrome(service=service, options=chrome_options)  # オプションを指定してChromeドライバーを起動
driver.get('https://cloud.ielove.jp/')

# IDとパスワードを入力してログインする
id_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, '_4407f7df050aca29f5b0c2592fb48e60')))
id_input.send_keys('fukuyama2')
password_input = driver.find_element(By.NAME, '_81fa5c7af7ae14682b577f42624eb1c0')
password_input.send_keys('chubus3601')
login_button = driver.find_element(By.ID, 'loginButton')
login_button.click()

# 2秒待って指定されたページにアクセスする
time.sleep(2)
driver.get('https://cloud.ielove.jp/rent/')
time.sleep(5)

# <span class="ui-icon ui-icon-triangle-1-s"></span> をクリックする
span_locator = (By.CSS_SELECTOR, 'span.ui-icon.ui-icon-triangle-1-s')
span_element_to_click = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(span_locator))
span_element_to_click.click()

# <input id="ui-multiselect-stcd-option-0" name="multiselect_stcd" type="checkbox" value="1" title=""> をクリックする
input_locator = (By.XPATH, '//*[@id="ui-multiselect-stcd-option-0"]')
input_element_to_click = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(input_locator))
input_element_to_click.click()


# 検索ボタンをクリックする
search_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'searchButton')))
search_button.click()

time.sleep(3)

# 件数選択ドロップダウンで500を選択
# 件数選択ドロップダウンを見つける
num_select = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'num')))

# Selectクラスを使用してドロップダウンを操作する
select = Select(num_select)

# "500"というvalueを持つオプションを選択
select.select_by_value("500")

time.sleep(3)

# ダウンロードボタンを選択
list_download = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'listDownload')))
list_download.click()

# ダウンロードするボタンをクリック
download_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'bukkaku_csv_download')))
download_button.click()

# ページャのリンクを取得
pager_links = driver.find_elements(By.CSS_SELECTOR, "p.pagerLink a")

for link in pager_links:
    link.click()
    
    # 1秒待つ
    time.sleep(1)
    
    # ダウンロードボタンをクリック
    list_download = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'listDownload')))
    list_download.click()
    
    # ダウンロードリンクをクリック
    download_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'bukkaku_csv_download')))
    download_button.click()
    
    # ダウンロードが完了するまで待つ
    download_dir = "/Users/kota/Documents/python_code/"
    timeout = 60
    start_time = time.time()
    filename = ""
    
    while not filename:
        elapsed_time = time.time() - start_time
        if elapsed_time > timeout:
            raise TimeoutError("Timeout occurred while waiting for file download.")
        
        files = os.listdir(download_dir)
        for file in files:
            if file.endswith(".csv"):
                filename = file
                break

        time.sleep(1)
    
    # ダウンロードされたファイル名を取得する
    filepath = os.path.join(download_dir, filename)
    
    # CSVファイルを削除する
    os.remove(filepath)
    
# ブラウザを終了する
driver.quit()
