import smtplib
from email.message import EmailMessage
from string import Template
from pathlib import Path
import os
import dotenv

dotenv.load_dotenv()


def send_email(message, reciever):
    # html = Template(Path('scripting/index.html').read_text())

    email = EmailMessage()
    email['from'] = 'Abyssara'
    email['to'] = reciever
    email['subject'] = message

    gmail_username = os.environ.get('MAIL_USERNAME')
    gmail_password = os.environ.get('MAIL_PASSWORD')
    print(gmail_username, gmail_password)
    # email.set_content(html.substitute({'name': 'TinTin'}), 'html')

    with smtplib.SMTP(host='smtp.gmail.com', port=587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(gmail_username, gmail_password)
        smtp.send_message(email)
        print('all done')
