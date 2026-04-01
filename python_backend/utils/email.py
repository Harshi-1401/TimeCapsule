import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", SMTP_USER)


def send_unlock_email(to_email: str, capsule_title: str) -> bool:
    """
    Send an unlock notification email to the user.
    Returns True on success, False on failure.
    """
    if not SMTP_USER or not SMTP_PASSWORD:
        print("⚠️  Email not configured — skipping email send.")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "🎉 Your Time Capsule is Unlocked!"
        msg["From"] = EMAIL_FROM
        msg["To"] = to_email

        # Plain text version
        text = f"""
Hi there!

Your time capsule "{capsule_title}" has just been unlocked!

Go to your dashboard to read your message and view any media you saved.

http://localhost:5173/dashboard

— The Time Capsule Team
        """.strip()

        # HTML version
        html = f"""
<html>
  <body style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px;">
    <div style="background: linear-gradient(135deg, #667eea, #764ba2); padding: 30px; border-radius: 12px; text-align: center;">
      <h1 style="color: white; margin: 0;">🎉 Your Capsule is Unlocked!</h1>
    </div>
    <div style="padding: 30px; background: #f9f9f9; border-radius: 0 0 12px 12px;">
      <p style="font-size: 16px; color: #333;">
        Your time capsule <strong>"{capsule_title}"</strong> has just been unlocked!
      </p>
      <p style="font-size: 15px; color: #555;">
        Head over to your dashboard to read your message and view any media you saved.
      </p>
      <a href="http://localhost:5173/dashboard"
         style="display: inline-block; margin-top: 16px; padding: 12px 28px;
                background: #764ba2; color: white; text-decoration: none;
                border-radius: 8px; font-weight: bold;">
        Open Dashboard →
      </a>
      <p style="margin-top: 30px; font-size: 12px; color: #aaa;">
        — The Time Capsule Team
      </p>
    </div>
  </body>
</html>
        """.strip()

        msg.attach(MIMEText(text, "plain"))
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(EMAIL_FROM, to_email, msg.as_string())

        print(f"✅ Unlock email sent to {to_email} for capsule '{capsule_title}'")
        return True

    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {e}")
        return False
