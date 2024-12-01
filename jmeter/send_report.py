import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def send_email(subject, body, to_addr, file_path):
    from_addr = "sanica789@gmail.com"
    password = "dptg pvrx hfmr komj"  # Ensure this is your new, correctly copied app password

    print("Creating email message...")
    msg = MIMEMultipart()
    msg['From'] = "sanica789@gmail.com"
    msg['To'] = "stungare@corcentric.com"
    msg['Subject'] = "html"

    msg.attach(MIMEText(body, 'plain'))

    with open(file_path, "rb") as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(file_path)}")
        msg.attach(part)

    print("Connecting to SMTP server...")
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.set_debuglevel(1)  # Enable SMTP debugging output
    server.starttls()
    print("Logging in to SMTP server...")
    server.login(from_addr, password)
    text = msg.as_string()
    print("Sending email...")
    server.sendmail(from_addr, to_addr, text)
    server.quit()
    print("Email sent successfully.")

if __name__ == "__main__":
    subject = "JMeter Test Report"
    body = "Please find the attached HTML report for the JMeter test run."
    to_addr = "stungare@corcentric.com"  # Change to your Gmail address for testing
    file_path = "C:\\Users\\stungare\\git-local\\jmeter\\html_report\\index.html"

    send_email(subject, body, to_addr, file_path)
