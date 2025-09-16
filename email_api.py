import os

from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


load_dotenv()

message = Mail(
    from_email="dabcrc@umsystem.edu",
    to_emails="khai1995pham@gmail.com",
    subject="Email-Day Test",
    plain_text_content="Never gonna give you up, never gonna let you down",
)

try:
    sg = SendGridAPIClient(os.environ["SENDGRID_API_KEY"])
    response = sg.send(message)
    print(response.status_code)
    print(response.body)
    print(response.headers)
except Exception as e:
    print(str(e))