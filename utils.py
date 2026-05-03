import imaplib
import email
import re
import time
from datetime import datetime

def get_mail_count(weverse_email, app_password):
    """인증코드 전송 전 현재 메일 개수 확인"""
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(weverse_email, app_password)
    mail.select("inbox")
    today = datetime.now().strftime("%d-%b-%Y")
    _, messages = mail.search(None, f'FROM "noreply@weverse.io" SINCE {today}')
    count = len(messages[0].split()) if messages[0] else 0
    mail.logout()
    return count

def get_verification_code(initial_count, weverse_email, app_password):
    """Gmail IMAP으로 새로 도착한 인증코드 자동 읽기"""
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(weverse_email, app_password)
    mail.select("inbox")
    today = datetime.now().strftime("%d-%b-%Y")

    for _ in range(20):
        time.sleep(5)
        mail.check()
        _, messages = mail.search(None, f'FROM "noreply@weverse.io" SINCE {today}')
        current_count = len(messages[0].split()) if messages[0] else 0

        if current_count > initial_count:
            latest = messages[0].split()[-1]
            _, msg_data = mail.fetch(latest, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])

            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode()
                        code = re.search(r'\b\d{6}\b', body)
                        if code:
                            mail.logout()
                            return code.group()
            else:
                body = msg.get_payload(decode=True).decode()
                code = re.search(r'\b\d{6}\b', body)
                if code:
                    mail.logout()
                    return code.group()

    mail.logout()
    return None