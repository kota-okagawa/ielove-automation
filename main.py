import os, time, csv, sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException, NoSuchElementException
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

LOGIN_USER = os.environ["LOGIN_USER"]
LOGIN_PASS = os.environ["LOGIN_PASS"]
SPREADSHEET_ID = os.environ["SHEET_ID"]
JSON_PATH = "service_account.json"
SHEET_NAME = "福山店"

download_dir = "/tmp/csv_download"
os.makedirs(download_dir, exist_ok=True)

def start_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0")
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    options.add_experimental_option("prefs", prefs)
    return webdriver.Chrome(options=options)

def save_debug(driver, tag="debug"):
    try:
        driver.save_screenshot(f"{tag}.png")
        with open(f"{tag}.html","w",encoding="utf-8") as f:
            f.write(driver.page_source)
    except Exception:
        pass

def switch_into_login_iframe(driver):
    # 入力欄が見つからない場合に iframe を総当り
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    for i, frm in enumerate(iframes):
        driver.switch_to.default_content()
        driver.switch_to.frame(frm)
        if driver.find_elements(By.CSS_SELECTOR, "input[type='password'], input[type='text']"):
            return True
    driver.switch_to.default_content()
    return False

def set_value_via_js(driver, el, text):
    driver.execute_script(
        "arguments[0].value = arguments[1];"
        "arguments[0].dispatchEvent(new Event('input',{bubbles:true}));",
        el, text
    )

driver = start_driver()
wait = WebDriverWait(driver, 25)

try:
    # --- ログインページ ---
    driver.get("https://cloud.ielove.jp/")
    # まずは直接可視要素を探す（IDが変わっても対応できるよう幅広く）
    # 1) iframe内の可能性に備えて切替
    switch_into_login_iframe(driver)

    # 候補ロケータ（順に試す）
    user_locators = [
        (By.ID, "_4407f7df050aca29f5b0c2592fb48e60"),
        (By.NAME, "loginid"),
        (By.CSS_SELECTOR, "input[type='text']"),
        (By.CSS_SELECTOR, "input[autocomplete='username']"),
    ]
    pass_locators = [
        (By.ID, "_81fa5c7af7ae14682b577f42624eb1c0"),
        (By.NAME, "password"),
        (By.CSS_SELECTOR, "input[type='password']"),
        (By.CSS_SELECTOR, "input[autocomplete='current-password']"),
    ]

    def find_visible(locators):
        for how, what in locators:
            try:
                el = wait.until(EC.visibility_of_element_located((how, what)))
                return el
            except TimeoutException:
                continue
        return None

    user_el = find_visible(user_locators)
    pass_el = find_visible(pass_locators)

    if not user_el or not pass_el:
        # もう一度トップに戻って iframe 総当たり
        driver.switch_to.default_content()
        if switch_into_login_iframe(driver):
            user_el = user_el or find_visible(user_locators)
            pass_el = pass_el or find_visible(pass_locators)

    if not user_el or not pass_el:
        save_debug(driver, "login_not_found")
        raise RuntimeError("ログイン入力欄が見つかりませんでした（login_not_found.* を確認）")

    # 入力（通常）
    try:
        user_el.clear(); user_el.send_keys(LOGIN_USER)
    except ElementNotInteractableException:
        set_value_via_js(driver, user_el, LOGIN_USER)

    try:
        pass_el.clear(); pass_el.send_keys(LOGIN_PASS)
    except ElementNotInteractableException:
        set_value_via_js(driver, pass_el, LOGIN_PASS)

    # ログインボタン
    login_btn = None
    for loc in [
        (By.ID, "loginButton"),
        (By.CSS_SELECTOR, "button[type='submit']"),
        (By.XPATH, "//button[contains(.,'ログイン') or contains(.,'Login')]"),
        (By.CSS_SELECTOR, "input[type='submit']"),
    ]:
        try:
            login_btn = wait.until(EC.element_to_be_clickable(loc))
            break
        except TimeoutException:
            continue

    if not login_btn:
        save_debug(driver, "login_button_not_found")
        raise RuntimeError("ログインボタンが見つかりません（login_button_not_found.* を確認）")

    driver.execute_script("arguments[0].scrollIntoView(true);", login_btn)
    try:
        login_btn.click()
    except ElementNotInteractableException:
        driver.execute_script("arguments[0].click();", login_btn)

    time.sleep(3)
    driver.switch_to.default_content()

    # ここから先は従来処理（一覧ページ遷移→CSVダウンロード→Sheets更新）
    # すでに実装済みの処理を続けて実行してください。
    # 例：
    driver.get('https://cloud.ielove.jp/rent/')
    time.sleep(2)
    # （以下、あなたの既存コードと同じ…）

except Exception as e:
    print("⚠️ ログイン処理でエラー:", e)
    save_debug(driver, "login_error")
    raise
