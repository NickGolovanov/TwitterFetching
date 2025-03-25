import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Email Configuration
SMTP_SERVER = "smtp.mail.yahoo.com"
SMTP_PORT = 465
EMAIL_SENDER = "aerika04@yahoo.com"
EMAIL_PASSWORD = "pkamoyfembtcddhi"  # Replace with your Yahoo App Password
EMAIL_RECEIVER = "erika.nicolau@student.nhlstenden.com"


def send_email(weather_type, date_time, location, tweet_link):
    """Sends a weather alert email notification."""
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECEIVER
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
