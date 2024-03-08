"""
This module is responsible for sending emails to the users.
"""

import smtplib
from email.message import EmailMessage
from string import Template
from pathlib import Path
import os
import dotenv

dotenv.load_dotenv()


def send_email(reciever, message, subject, title):
    # html = Template(Path('scripting/index.html').read_text())

    email = EmailMessage()
    email['from'] = 'Abyssara'
    email['to'] = reciever
    email['subject'] = subject

    gmail_username = os.environ.get('MAIL_USERNAME')
    gmail_password = os.environ.get('MAIL_PASSWORD')
    print(gmail_username, gmail_password)
    # email.set_content(html.substitute({'name': 'TinTin'}), 'html')

    # Load the HTML template
    html_template = Template(Path(os.path.join(os.path.dirname(__file__), 'templates', 'email.html')).read_text())
    
    # Substitute the title in the template
    html_content = html_template.substitute({'title': title, 'message': message})
    
    email.set_content(html_content, 'html')

    with smtplib.SMTP(host='smtp.gmail.com', port=587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(gmail_username, gmail_password)
        smtp.send_message(email)
        print('all done')
