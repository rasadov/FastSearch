"""
This module is responsible for sending emails to the users.
~~~~~~~~~~~~~~~~~~~~~

It uses the smtplib library to establish a connection with the SMTP server and send the email.
The email message is created using the EmailMessage class from the email.message module.
The email content is generated by substituting variables
in an HTML template using the string.Template class.
The template file is located in the 'templates' directory relative to the current file.
The SMTP server details and login credentials are retrieved
from environment variables using the dotenv library.

The send_email function takes the recipient's email address, message content,
subject, and title as parameters.
It creates an EmailMessage object and sets the sender, recipient, and subject fields.
The HTML content is generated by substituting the title and message variables in the template.
The email content is set to the generated HTML content.
Finally, the email is sent using the SMTP server.

Example usage:
send_email('example@example.com', 'Hello, this is a test email.', 'Test Email', 'My App')
"""

import os
import smtplib
from email.message import EmailMessage
from pathlib import Path
from string import Template

import dotenv

dotenv.load_dotenv()


def send_email(reciever, message, subject, title):
    """
    Sends an email to the specified receiver with the given message, subject, and title.

    Parameters:
    - receiver (str): The email address of the receiver.
    - message (str): The content of the email message.
    - subject (str): The subject of the email.
    - title (str): The title to be substituted in the email template.

    Returns:
    None
    """
    email = EmailMessage()
    email["from"] = "Abyssara"
    email["to"] = reciever
    email["subject"] = subject

    gmail_username = os.environ.get("MAIL_USERNAME")
    gmail_password = os.environ.get("MAIL_PASSWORD")

    # Load the HTML template
    html_template = Template(
        Path(
            os.path.join(os.path.dirname('src/app/'), "templates", "Base/email.html"),
        ).read_text(encoding="utf-8")
    )

    # Substitute the title in the template
    html_content = html_template.substitute({"title": title, "message": message})

    email.set_content(html_content, "html")

    with smtplib.SMTP(host="smtp.gmail.com", port=587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(gmail_username, gmail_password)
        smtp.send_message(email)
