import os, time, csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# --- 環境変数（Secretsに登録しておく） ---
LOGIN_USER = os.environ["LOGIN_USER"]
LOGIN_PASS = os.environ["LOGIN_PASS"]
SPREADSHEET_ID = os.environ["SHEET_ID"]
JSON_PATH = "service_account.json"

# --- 書き込み先シート名 ---
SHEET_NAME = "福山店"

# --- ダウンロード先ディレクトリ ---
download_dir = "/tmp/csv_download"
os.makedirs(download_dir, exist_ok=True)

# --- Chromeオプション ---
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}
options.add_experimental_option("prefs", prefs)

# --- Chrome起動 ---
driver = webdriver.Chrome(options=options)
driver.get('https://cloud.ielove.jp/')

# --- ログイン ---
id_input = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, '_4407f7df050aca29f5b0c2592fb48e60'))
)
id_input.send_keys(LOGIN_USER)

password_input = driver.find_element(By.ID, '_81fa5c7af7ae14682b577f42624eb1c0')
password_input.send_keys(LOGIN_PASS)

login_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, 'loginButton'))
)
login_button.click()
time.sleep(2)

# --- 物件一覧ページへ ---
driver.get('https://cloud.ielove.jp/rent/')
time.sleep(2)

# ▼ 以下、Colab版と同じ操作 ▼
triangle_icon = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, '//span[@class="ui-icon ui-icon-triangle-1-s"]'))
)
driver.execute_script("arguments[0].click();", triangle_icon)
time.sleep(2)

checkbox_element = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, '//input[@id="ui-multiselect-stcd-option-0"]'))
)
checkbox_element.click()
time.sleep(2)

search_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, 'searchButton'))
)
driver.execute_script("arguments[0].scrollIntoView(true);", search_button)
time.sleep(1)
driver.execute_script("arguments[0].click();", search_button)
time.sleep(3)

select_option = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, '//select[@class="num flt_left_imp"]/option[@value="500"]'))
)
select_option.click()
time.sleep(4)

# --- Google Sheets 書き込み関数 ---
def write_to_sheet(filename):
    data = []
    with open(filename, 'r', encoding='cp932', newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            data.append(row[0:23])

    creds = Credentials.from_service_account_file(JSON_PATH)
    service = build('sheets', 'v4', credentials=creds)

    # 既存データを消してから書き込み
    clear_range = SHEET_NAME + '!A:W'
    service.spreadsheets().values().clear(
        spreadsheetId=SPREADSHEET_ID,
        range=clear_range
    ).execute()

    range_ = SHEET_NAME + '!A1:W' + str(len(data))
    body = {'majorDimension': 'ROWS', 'values': data}
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=range_,
        valueInputOption='USER_ENTERED',
        body=body
    ).execute()

    print("✅ スプレッドシート更新完了")

# --- CSVダウンロード処理（最初のページだけ例示） ---
try:
    download_button = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, 'listDownloadFooter'))
    )
    driver.execute_script("arguments[0].click();", download_button)
    time.sleep(2)

    csv_download_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.ID, 'bukkaku_csv_download'))
    )
    driver.execute_script("arguments[0].click();", csv_download_button)
    time.sleep(3)

    # ダウンロード完了を待つ
    timeout = 30
    filename = None
    while timeout > 0:
        files = [f for f in os.listdir(download_dir) if f.endswith('.csv')]
        if files:
            filename = max([os.path.join(download_dir, f) for f in files], key=os.path.getctime)
            break
        time.sleep(1)
        timeout -= 1

    if filename:
        write_to_sheet(filename)
        os.remove(filename)
    else:
        print("⚠️ CSVが見つかりませんでした")

except Exception as e:
    print("⚠️ エラー:", e)

# --- 終了 ---
driver.quit()
