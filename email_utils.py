from email.message import EmailMessage

import aiosmtplib
from fastapi.templating import Jinja2Templates

from config import settings


templates = Jinja2Templates(directory= "templates")

# "Give me the recipient, subject, and content."
# " I'll turn it into an EmailMessage and send"
# " it through SMTP."
async def send_email(
    to_email: str,
    subject: str,
    plain_text: str,
    html_content: str | None = None,
) -> None:
    message = EmailMessage()
    message["From"] = settings.mail_from
    message["To"] = to_email
    message["Subject"] = subject

    message.set_content(plain_text)

    if html_content:
        message.add_alternative(html_content, subtype="html")

    print("ABOUT TO SEND EMAIL TO MAILTRAP")
    
    await aiosmtplib.send(
        message,
        hostname=settings.mail_server,
        port=settings.mail_port,
        username=settings.mail_username if settings.mail_username else None,
        password=settings.mail_password.get_secret_value() or None,
        start_tls=settings.mail_use_tls,
        )

    print("EMAIL SENT TO MAILTRAP")
# "We're sending a password reset. Here's the username, here's the reset token,"
# " here's the reset link, and here's what the email should say."
async def send_password_reset_email(to_email: str, username: str, token: str) -> None:

    print("EMAIL FUNCTION STARTED")
    reset_url = f"{settings.frontend_url}/reset-password?token={token}"

    template = templates.env.get_template("email/password_reset.html")
    html_content = template.render(reset_url=reset_url, username=username)

    plain_text = f"""Hi {username},

You requested to reset your password. Click the link below to set a new password:

{reset_url}

This link will expire in 1 hour.

If you didn't request this, you can safely ignore this email.

Best regards,
The FastAPI Blog Team
"""

    await send_email(
        to_email=to_email,
        subject="Reset Your Password - FastAPI Blog",
        plain_text=plain_text,
        html_content=html_content,
    )

    print("EMAIL FUNCTION FINISHED")