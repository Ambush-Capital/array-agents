# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from datetime import datetime
import requests
from pydantic import BaseModel, Field

class SendEmail(BaseModel):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def send_full_analysis(output, recipient_email, current_time):
        message = Mail(
            from_email='carly@ambush.capital',
            to_emails=recipient_email,
        subject=f'Array Rebalancing Analysis - {current_time}',
        html_content=f"<p>{output}</p>"
        )
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(f"Email sent successfully with status code {response.status_code}")
    except Exception as e:
        print(f"Error sending email: {e}")

if __name__ == "__main__":
    SendEmail().send_full_analysis("test", "carly@ambush.capital")  