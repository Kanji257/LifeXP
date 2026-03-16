"""
email_service.py — LifeXP Email Service
Sends verification codes via Gmail SMTP.
Designed to be swappable with SendGrid later by replacing send_email().
"""

import smtplib
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta


def _get_credentials():
    """Load Gmail credentials from Streamlit secrets or environment."""
    try:
        import streamlit as st
        return st.secrets["GMAIL_ADDRESS"], st.secrets["GMAIL_APP_PASSWORD"]
    except Exception:
        import os
        return os.environ.get("GMAIL_ADDRESS",""), os.environ.get("GMAIL_APP_PASSWORD","")


def send_email(to_address: str, subject: str, html_body: str) -> tuple[bool, str]:
    """
    Send an email via Gmail SMTP.
    Returns (success, error_message).
    To switch to SendGrid later, replace only this function.
    """
    gmail_address, app_password = _get_credentials()
    if not gmail_address or not app_password:
        return False, "Email service not configured. Add GMAIL_ADDRESS and GMAIL_APP_PASSWORD to Streamlit Secrets."

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"LifeXP <{gmail_address}>"
        msg["To"] = to_address
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_address, app_password)
            server.sendmail(gmail_address, to_address, msg.as_string())
        return True, ""
    except smtplib.SMTPAuthenticationError:
        return False, "Email authentication failed. Check your Gmail App Password in Streamlit Secrets."
    except smtplib.SMTPException as e:
        return False, f"Email sending failed: {str(e)[:100]}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)[:100]}"


def generate_code(length: int = 6) -> str:
    """Generate a random numeric verification code."""
    return "".join(random.choices(string.digits, k=length))


def _email_template(title: str, body_html: str) -> str:
    """Wrap content in a styled HTML email template."""
    return f"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#0F0F1A;font-family:'Helvetica Neue',Arial,sans-serif;">
  <div style="max-width:520px;margin:40px auto;background:linear-gradient(135deg,#1A1A2E,#16213E);
    border:1px solid #2A2A4A;border-radius:16px;overflow:hidden;">
    <!-- Header -->
    <div style="background:linear-gradient(135deg,#7C3AED,#2563EB);padding:28px 32px;text-align:center;">
      <div style="font-size:28px;font-weight:900;color:white;letter-spacing:2px;">🎮 LifeXP</div>
      <div style="color:rgba(255,255,255,0.8);font-size:12px;letter-spacing:3px;margin-top:4px;">
        AI · GAMIFIED · SELF-IMPROVEMENT
      </div>
    </div>
    <!-- Body -->
    <div style="padding:32px;">
      <h2 style="color:#A78BFA;font-size:20px;margin:0 0 16px;font-weight:700;">{title}</h2>
      {body_html}
    </div>
    <!-- Footer -->
    <div style="padding:20px 32px;border-top:1px solid #2A2A4A;text-align:center;">
      <p style="color:#4B5563;font-size:12px;margin:0;">
        This email was sent by LifeXP. If you didn't request this, ignore it safely.
      </p>
    </div>
  </div>
</body>
</html>"""


def send_verification_code(to_email: str, code: str, purpose: str = "verify") -> tuple[bool, str]:
    """
    Send a 6-digit verification code email.
    purpose: 'verify' (add email) or 'reset' (password reset)
    """
    if purpose == "reset":
        title = "Reset Your Password"
        body = f"""
<p style="color:#D1D5DB;font-size:15px;line-height:1.6;margin:0 0 24px;">
  You requested a password reset for your LifeXP account. Use the code below to continue.
</p>
<div style="background:#0F0F1A;border:2px solid #7C3AED;border-radius:12px;
  padding:24px;text-align:center;margin:0 0 24px;">
  <div style="font-size:42px;font-weight:900;letter-spacing:12px;color:#A78BFA;
    font-family:'Courier New',monospace;">{code}</div>
  <div style="color:#6B7280;font-size:13px;margin-top:8px;">This code expires in 10 minutes</div>
</div>
<p style="color:#6B7280;font-size:13px;margin:0;">
  If you didn't request a password reset, your account is safe — just ignore this email.
</p>"""
    else:
        title = "Verify Your Email"
        body = f"""
<p style="color:#D1D5DB;font-size:15px;line-height:1.6;margin:0 0 24px;">
  Enter the code below in LifeXP to verify your email address.
</p>
<div style="background:#0F0F1A;border:2px solid #7C3AED;border-radius:12px;
  padding:24px;text-align:center;margin:0 0 24px;">
  <div style="font-size:42px;font-weight:900;letter-spacing:12px;color:#A78BFA;
    font-family:'Courier New',monospace;">{code}</div>
  <div style="color:#6B7280;font-size:13px;margin-top:8px;">This code expires in 10 minutes</div>
</div>
<p style="color:#6B7280;font-size:13px;margin:0;">
  If you didn't request this, ignore it safely.
</p>"""

    html = _email_template(title, body)
    return send_email(to_email, f"LifeXP — Your verification code: {code}", html)
