import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

# Email Configuration
SMTP_SERVER = "smtp.mail.yahoo.com"
SMTP_PORT = 465
EMAIL_SENDER = "weatherclaim@yahoo.com"
EMAIL_PASSWORD = "leaanjmxrigfhcrc"
EMAIL_RECEIVER = os.environ.get("TARGET_TEST_EMAIL", "").split(",")
EMAIL_RECEIVER = [email.strip() for email in EMAIL_RECEIVER if email.strip()]


def send_email(weather_type, date_time, location, tweet_link):
    """Sends a weather alert email notification."""
    try:
        # Print the converted email list for debugging
        print("📧 Converted Email List:", EMAIL_RECEIVER)

        msg = MIMEMultipart()
        msg["From"] = EMAIL_SENDER
        msg["To"] = ", ".join(EMAIL_RECEIVER)  # Convert list to a comma-separated string
        msg["Subject"] = f"🚨 Weather Alert: {weather_type} Detected"

        body = f"""
        <h3>🚨 Urgent Weather Alert</h3>
        <p><strong>Weather Type:</strong> {weather_type}</p>
        <p><strong>Date & Time:</strong> {date_time}</p>
        <p><strong>Location:</strong> {location}</p>
        <p><strong>Source:</strong> <a href='{tweet_link}' target='_blank'>View Map</a></p>
        <p>Please take necessary preventive measures.</p>
        """
        msg.attach(MIMEText(body, "html"))

        # Connect and Send Email
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        server.quit()

        print("✅ Email sent successfully!")
        return True
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False