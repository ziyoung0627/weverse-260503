import time
import email.utils
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from utils import get_mail_count, get_verification_code

# 테스트 계정 정보
EMAIL = ""           # 위버스 가입할 이메일
APP_PASSWORD = ""    # Gmail 앱 비밀번호
WEVERSE_PASSWORD = "" # 위버스 가입할 비밀번호

def get_wid():
    """
    위버스 사용자 정보 API로 WID 추출
    - Authorization 토큰은 로그인 후 브라우저에서 수동으로 가져와야 함
    - 토큰 자동 추출 불가하여 수동 입력 방식 사용ㅠ.ㅠ
    """
    token = input("브라우저에서 복사한 Authorization 토큰 입력 (Bearer 제외): ")

    response = requests.get(
        "https://global.apis.naver.com/weverse/wevweb/users/v1.0/users/me",
        params={
            "appId": "be4d79eb8fc7bd008ee82c8ec4ff6fd4",
            "language": "ko",
            "os": "WEB",
            "platform": "WEB",
            "wpf": "pc",
            "wmd": "oQVMOb9WztGy9yfSqXjecS1Y0l4=",
            "wmsgpad": str(int(time.time() * 1000))
        },
        headers={
            "Referer": "https://weverse.io/",
            "Authorization": f"Bearer {token}"
        }
    )

    data = response.json()
    return data.get("wid")

def signup_weverse():
    """위버스 회원가입 자동화"""
    options = webdriver.ChromeOptions()
    options.add_argument("--user-data-dir=/tmp/weverse_chrome")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 20)

    try:
        # 1. 회원가입 페이지 접속
        driver.get("https://account.weverse.io/ko/signup/credential?client_id=weverse&redirect_uri=https%3A%2F%2Fweverse.io%2F&redirect_method=COOKIE&v=4")
        time.sleep(2)

        # 2. 이메일 입력
        email_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']")))
        email_input.click()
        email_input.send_keys(EMAIL)

        # 3. 인증코드 받기 버튼 클릭 전 현재 메일 개수 저장
        send_code_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '인증코드')]/parent::button")))
        initial_count = get_mail_count(EMAIL, APP_PASSWORD)
        send_code_btn.click()

        # 4. 비밀번호 / 비밀번호 확인 입력
        pw_inputs = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "input[type='password']")))
        pw_inputs[0].send_keys(WEVERSE_PASSWORD)
        pw_inputs[1].send_keys(WEVERSE_PASSWORD)

        # 5. 새로 도착한 인증코드 자동 수신 후 입력
        code = get_verification_code(initial_count, EMAIL, APP_PASSWORD)
        code_input = driver.find_element(By.CSS_SELECTOR, "input[placeholder='인증코드 6자리']")
        code_input.send_keys(code)

        # 6. 인증코드 확인 버튼 클릭
        verify_btn = driver.find_element(By.XPATH, "//span[contains(text(), '인증코드 확인')]/parent::button")
        verify_btn.click()
        time.sleep(1)

        # 7. 다음 버튼 클릭
        next_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '다음')]/parent::button")))
        driver.execute_script("arguments[0].click();", next_btn)
        time.sleep(3)

        # 8. 모두 동의 클릭
        agree_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '모두 동의')]/parent::button")))
        agree_btn.click()
        time.sleep(1)

        # 9. 가입하기 클릭
        submit_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '가입하기')]/parent::button")))
        driver.execute_script("arguments[0].click();", submit_btn)
        time.sleep(3)

        # 10. 확인 클릭
        confirm_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '확인')]/parent::button")))
        confirm_btn.click()
        time.sleep(3)

        return driver

    except Exception as e:
        print(f"에러 발생: {e}")
        driver.quit()
        return None

def main():
    # 회원가입 자동화 실행
    driver = signup_weverse()
    if not driver:
        return

    driver.quit()

    # WID 추출 (브라우저에서 토큰 수동 입력)
    wid = get_wid()

    # 결과 출력
    print("\n===== 결과 =====")
    print(f"ID  : {EMAIL}")
    print(f"PW  : {WEVERSE_PASSWORD}")
    print(f"WID : {wid}")
    print("================")

if __name__ == "__main__":
    main()