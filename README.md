## 실행 방법

### 1. 패키지 설치
```bash
pip install selenium webdriver-manager requests
```

### 2. 계정 정보 설정
각 파일 상단의 계정 정보를 입력해주세요.
```python
weverse_email = ""       # 위버스 가입할 이메일
app_password = ""        # Gmail 앱 비밀번호
weverse_password = ""    # 위버스 비밀번호
```

### 3. 회원가입 실행
```bash
python3 weverse_signup.py
```

### 4. 로그인 및 포스트 자동화 실행
```bash
python3 weverse_login.py
```

## 자동화 흐름

### weverse_signup.py
1. 위버스 회원가입 페이지 접속
2. 이메일 입력 및 인증코드 자동 수신
3. 비밀번호 입력 및 가입 완료
4. WID 추출 (수동 토큰 입력)

### weverse_login.py
1. 위버스 로그인 (이메일 인증코드 자동 수신)
2. 커뮤니티 가입
3. 포스트 생성 (텍스트 + 이미지)
4. 포스트 수정 (텍스트 변경 + 이미지 삭제 + 동영상 교체)
5. 포스트 삭제

## 한계점
- **WID 자동 추출 불가**: 테스트용 계정 생성에 제약이 있어 로그인 후 토큰 추출까지 완전한 자동화 구현에 한계가 있었습니다. 현재는 브라우저에서 Authorization 토큰을 수동으로 입력하는 방식으로 구현하였으며, 추후 개선이 필요한 부분으로 인지하고 있습니다.
- **Gmail 인증코드**: Gmail IMAP을 활용하여 인증코드를 자동 수신하도록 구현했습니다.
