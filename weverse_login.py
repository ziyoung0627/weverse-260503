import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from utils import get_mail_count, get_verification_code

# 계정 정보
weverse_email = ""           # 위버스 가입한 이메일
app_password = ""            # Gmail 앱 비밀번호
weverse_password = ""        # 위버스 비밀번호

# 테스트 설정
artist = "yutoadachi"
post_text = "안녕하세요옹"
edit_text = "수정했습니다"
image_path = "/Users/ziyoung/Downloads/detail.jpg"
video_path = "/Users/ziyoung/Downloads/video.mp4"


def login_weverse():
    """위버스 로그인 자동화"""
    options = webdriver.ChromeOptions()
    options.add_argument("--user-data-dir=/tmp/weverse_chrome_2")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    wait = WebDriverWait(driver, 20)

    try:
        # 1. 로그인 페이지 접속
        driver.get("https://account.weverse.io/ko/login/credential?client_id=weverse&redirect_uri=https%3A%2F%2Fweverse.io%2F&redirect_method=COOKIE&v=4")
        time.sleep(2)

        # 2. 이메일 입력
        email_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']")))
        email_input.send_keys(weverse_email)

        # 3. 비밀번호 입력
        pw_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']")))
        pw_input.send_keys(weverse_password)

        # 4. 로그인 버튼 클릭 전 메일 개수 저장
        login_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '로그인')]/parent::button")))
        initial_count = get_mail_count(weverse_email, app_password)
        driver.execute_script("arguments[0].click();", login_btn)

        # 5. 인증코드 자동 수신 후 입력
        code = get_verification_code(initial_count, weverse_email, app_password)
        code_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='인증코드 6자리']")))
        code_input.send_keys(code)

        # 6. 인증코드 확인 버튼 클릭
        verify_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '인증코드 확인')]/parent::button")))
        driver.execute_script("arguments[0].click();", verify_btn)
        time.sleep(5)

        # 7. 확인 클릭
        confirm_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '확인')]/parent::button")))
        confirm_btn.click()
        time.sleep(3)

        return driver

    except Exception as e:
        print(f"로그인 에러: {e}")
        driver.quit()
        return None


def join_community(driver, wait):
    """커뮤니티 가입"""
    driver.get(f"https://weverse.io/{artist}/highlight")
    time.sleep(3)

    # 첫 번째 가입하기 버튼 클릭
    join_btn = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//span[contains(text(), '가입하기')]/parent::button")))
    driver.execute_script("arguments[0].click();", join_btn[0])

    # 팝업 가입하기 버튼 클릭
    popup_join_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.custom-popup-_-button_area button")))
    driver.execute_script("arguments[0].click();", popup_join_btn)
    time.sleep(3)

    try:
        wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), '가입 완료')]")))
        print("커뮤니티 가입 완료")
    except:
        print("가입 정상적으로 안됨, 테스트 종료")
        driver.quit()
        return False

    return True


def create_post(driver, wait, actions):
    """포스트 생성 (텍스트 + 이미지)"""
    driver.get(f"https://weverse.io/{artist}/feed")
    time.sleep(3)

    # 포스트 입력창 클릭
    post_input = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), '이야기를 나눠보세요')]")))
    post_input.click()
    time.sleep(1)

    # 텍스트 입력
    actions.click(post_input).send_keys(post_text).perform()
    time.sleep(1)

    # 이미지 첨부
    file_input = driver.find_element(By.CSS_SELECTOR, "input#weuii")
    driver.execute_script("arguments[0].style.display = 'block';", file_input)
    file_input.send_keys(image_path)
    file_confirm = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '확인')]")))
    file_confirm.click()
    time.sleep(1)

    # 등록 클릭
    register_post = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '등록')]/parent::button")))
    register_post.click()
    time.sleep(1)

    # 피드에서 등록한 포스트 확인
    driver.get(f"https://weverse.io/{artist}/feed")
    time.sleep(3)

    try:
        wait.until(EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{post_text}')]")))
        print("포스트 등록 확인 완료")
    except:
        print("포스트 등록 확인 실패, 테스트 종료")
        driver.quit()
        return False

    return True


def edit_post(driver, wait, actions):
    """포스트 수정 (텍스트 변경 + 이미지 삭제 + 동영상 교체)"""
    driver.get(f"https://weverse.io/{artist}/feed")
    time.sleep(3)

    # 더보기 버튼 클릭
    post_element = wait.until(EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{post_text}')]")))
    more_btn = post_element.find_element(By.XPATH, "ancestor::div[@class='post-module-_-wrapper']//div[@class='toolbar-_-more']/button")
    driver.execute_script("arguments[0].click();", more_btn)
    time.sleep(1)

    # 수정하기 클릭
    edit_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '수정')]")))
    driver.execute_script("arguments[0].click();", edit_btn)
    time.sleep(1)

    # 이미지 삭제
    del_btn = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.btn.-del._deleteWidget")))
    driver.execute_script("arguments[0].click();", del_btn)
    time.sleep(1)

    # 텍스트 수정
    post_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.wev-editor-input-v3-_-text")))
    driver.execute_script("arguments[0].innerText = '';", post_input)
    time.sleep(1)
    actions.click(post_input).send_keys(edit_text).perform()
    time.sleep(1)

    # 동영상 첨부
    video_input = driver.find_element(By.CSS_SELECTOR, "input#weuvi")
    driver.execute_script("arguments[0].style.display = 'block';", video_input)
    video_input.send_keys(video_path)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "img.thumbnail")))
    print("동영상 업로드 완료!")
    file_confirm = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.dialog-button-area-_-button_area button")))
    driver.execute_script("arguments[0].click();", file_confirm)
    time.sleep(1)

    # 등록 클릭
    register_post = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '등록')]/parent::button")))
    register_post.click()
    time.sleep(1)

    # 피드에서 수정된 포스트 확인
    driver.get(f"https://weverse.io/{artist}/feed")
    time.sleep(3)

    try:
        wait.until(EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{edit_text}')]")))
        print("포스트 수정 확인 완료")
    except:
        print("포스트 수정 확인 실패, 테스트 종료")
        driver.quit()
        return False

    return True


def delete_post(driver, wait):
    """포스트 삭제"""
    driver.get(f"https://weverse.io/{artist}/feed")
    time.sleep(3)

    # 더보기 버튼 클릭
    post_element = wait.until(EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{edit_text}')]")))
    more_btn = post_element.find_element(By.XPATH, "ancestor::div[@class='post-module-_-wrapper']//div[@class='toolbar-_-more']/button")
    driver.execute_script("arguments[0].click();", more_btn)
    time.sleep(1)

    # 삭제하기 클릭
    delete_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '삭제')]")))
    driver.execute_script("arguments[0].click();", delete_btn)
    time.sleep(1)

    # 삭제 확인 버튼 클릭
    delete_confirm_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.dialog-button-area-_-button_area button")))
    driver.execute_script("arguments[0].click();", delete_confirm_btn)
    time.sleep(3)

    print("포스트 삭제 완료")
    return True


def main():
    driver = login_weverse()
    if not driver:
        return

    wait = WebDriverWait(driver, 60)
    actions = ActionChains(driver)

    if not join_community(driver, wait):
        return
    if not create_post(driver, wait, actions):
        return
    if not edit_post(driver, wait, actions):
        return
    if not delete_post(driver, wait):
        return

    driver.quit()


if __name__ == "__main__":
    main()