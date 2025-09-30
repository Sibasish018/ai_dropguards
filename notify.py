import smtplib
from email.mime.text import MIMEText
from config import MAIL_SERVER, MAIL_PORT, MAIL_USE_TLS, MAIL_USERNAME, MAIL_PASSWORD

def setup_smtp_server():
    """
    Connects to the SMTP server and logs in.
    Returns the server object.
    """
    server = smtplib.SMTP(MAIL_SERVER, MAIL_PORT)
    if MAIL_USE_TLS:
        server.starttls()
    server.login(MAIL_USERNAME, MAIL_PASSWORD)
    return server

def send_email(server, to_email, subject, message):
    """
    Sends an email using an existing server connection.
    """
    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = MAIL_USERNAME
    msg["To"] = to_email
    server.sendmail(MAIL_USERNAME, [to_email], msg.as_string())