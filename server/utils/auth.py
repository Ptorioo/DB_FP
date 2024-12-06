import os
from dotenv import load_dotenv
from email.message import EmailMessage
import smtplib
import hashlib

load_dotenv()

MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
SENDER_MAIL = os.getenv("SENDER_MAIL")

def send_email(receiver, subject, body):
    sender = SENDER_MAIL
    em = EmailMessage()
    em["From"] = sender
    em["To"] = receiver
    em["Subject"] = subject
    em.set_content(body)

    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls()
        smtp.login(sender, MAIL_PASSWORD)
        smtp.sendmail(sender, receiver, em.as_string())

def hash_password(password: str) -> str:
    sha1_hash = hashlib.sha1()

    sha1_hash.update(password.encode('utf-8'))
    return sha1_hash.hexdigest()[:20]
