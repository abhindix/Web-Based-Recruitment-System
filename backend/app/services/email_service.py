from aiosmtplib import SMTP
from email.message import EmailMessage
from app.core.config import settings

async def send_email(to_email: str, subject: str, body: str) -> None:
    if not settings.SMTP_HOST:
        # allow running locally without SMTP
        return

    msg = EmailMessage()
    msg["From"] = settings.SMTP_FROM
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    smtp = SMTP(hostname=settings.SMTP_HOST, port=settings.SMTP_PORT, start_tls=True)
    await smtp.connect()
    await smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
    await smtp.send_message(msg)
    await smtp.quit()
