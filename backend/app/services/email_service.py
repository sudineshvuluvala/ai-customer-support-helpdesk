import html
import logging
import smtplib
import threading
from email.message import EmailMessage

from flask import current_app

log = logging.getLogger(__name__)


def _send(cfg, to, subject, body, html_body=None):
    try:
        msg = EmailMessage()
        msg["From"] = cfg["MAIL_FROM"]
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(body)
        if html_body:
            msg.add_alternative(html_body, subtype="html")

        port = int(cfg.get("MAIL_PORT") or 587)
        server = cfg.get("MAIL_SERVER")

        if port == 465:
            with smtplib.SMTP_SSL(server, port, timeout=12) as s:
                if cfg.get("MAIL_USERNAME"):
                    s.login(cfg["MAIL_USERNAME"], cfg["MAIL_PASSWORD"])
                s.send_message(msg)
        else:
            with smtplib.SMTP(server, port, timeout=12) as s:
                s.ehlo()
                s.starttls()
                s.ehlo()
                if cfg.get("MAIL_USERNAME"):
                    s.login(cfg["MAIL_USERNAME"], cfg["MAIL_PASSWORD"])
                s.send_message(msg)
        log.info("Email sent successfully to %s: %s", to, subject)
    except Exception as exc:  # email failure must never break ticket operations
        log.warning("Email to %s failed: %s", to, exc)


def send_email(to, subject, body, html_body=None):
    """Best-effort, non-blocking email. Returns True if dispatch was attempted."""
    try:
        cfg = current_app.config
    except Exception:
        return False
    if not cfg.get("MAIL_ENABLED") or not cfg.get("MAIL_SERVER") or not to:
        return False
    snapshot = {
        "MAIL_FROM": cfg.get("MAIL_FROM"),
        "MAIL_SERVER": cfg.get("MAIL_SERVER"),
        "MAIL_PORT": cfg.get("MAIL_PORT"),
        "MAIL_USERNAME": cfg.get("MAIL_USERNAME"),
        "MAIL_PASSWORD": cfg.get("MAIL_PASSWORD"),
    }
    threading.Thread(target=_send, args=(snapshot, to, subject, body, html_body), daemon=True).start()
    return True


def render_email_template(title, headline, paragraphs, cta_text=None, cta_url=None):
    """Generate a clean responsive HTML email template for Helpdesk notifications."""
    p_tags = "".join(f"<p style='color: #475569; font-size: 15px; line-height: 1.6; margin: 0 0 16px 0;'>{html.escape(p)}</p>" for p in paragraphs)
    cta_block = ""
    if cta_text and cta_url:
        cta_block = f"""
        <div style='text-align: center; margin: 32px 0;'>
          <a href='{html.escape(cta_url)}' style='background: #2563eb; color: #ffffff; text-decoration: none; padding: 12px 28px; font-weight: 600; border-radius: 6px; display: inline-block; font-size: 14px;'>
            {html.escape(cta_text)}
          </a>
        </div>
        """
    return f"""
    <!DOCTYPE html>
    <html>
      <body style='font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: #f8fafc; margin: 0; padding: 30px 10px;'>
        <div style='max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 10px; border: 1px solid #e2e8f0; overflow: hidden;'>
          <div style='background: #0f172a; padding: 24px; text-align: center;'>
            <h1 style='color: #ffffff; font-size: 20px; margin: 0; font-weight: 700;'>AI Support &amp; Helpdesk</h1>
          </div>
          <div style='padding: 32px 28px;'>
            <h2 style='color: #0f172a; font-size: 18px; margin-top: 0; margin-bottom: 20px; font-weight: 600;'>{html.escape(headline)}</h2>
            {p_tags}
            {cta_block}
            <hr style='border: 0; border-top: 1px solid #f1f5f9; margin: 30px 0;'/>
            <p style='color: #94a3b8; font-size: 12px; margin: 0; line-height: 1.5;'>
              You are receiving this automated email from the AI-Powered Customer Support &amp; Helpdesk Portal.<br/>
              Please do not reply directly to this message.
            </p>
          </div>
        </div>
      </body>
    </html>
    """
