import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import textwrap
from email.utils import parseaddr
import time
import logging
import configparser

# Config for password and username in config.ini
config = configparser.ConfigParser()
config.read('config.ini')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Gmail IMAP and SMTP settings
IMAP_SERVER = "imap.gmail.com"
SMTP_SERVER = "smtp.gmail.com"
IMAP_PORT = 993
SMTP_PORT = 587
USERNAME = config['DEFAULT']['USERNAME']  # Replace with your email in config.ini
PASSWORD = config['DEFAULT']['PASSWORD']  # Replace with your password in config.ini

print(USERNAME)
print(PASSWORD)

# Email subject to trigger auto-reply
TRIGGER_SUBJECT = 'Share request for "EV & ICE Novated Lease Calculators"' # Replace with your subject

# Auto-reply message content
def create_auto_reply(to_email):
    auto_reply_text = textwrap.dedent(f"""\
        Hi,

        Thank you very much for your request for access to the spreadsheet.

        Unfortunately, due to the way Google Sheets work, I can’t grant “edit request” as all your edits would directly change my original version.

        Therefore, you will have to “make a copy”. This is the method:

        Use a computer, make sure you are logged on to Google, then go to File > Make a copy.

        Thank you,
        Me
    """)
    return auto_reply_text

# Function to send auto-reply email
def send_auto_reply(to_email):
    # Prepare the email
    msg = MIMEMultipart()
    msg['From'] = USERNAME
    msg['To'] = to_email
    msg['Subject'] = 'Re: Share request for "EV & ICE Novated Lease Calculators"'

    # Attach the message content
    msg.attach(MIMEText(create_auto_reply(to_email), 'plain'))

    # Set up the SMTP server
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Start TLS encryption
        server.login(USERNAME, PASSWORD)  # Login to the email server
        server.sendmail(USERNAME, to_email, msg.as_string())  # Send email
        server.quit()  # Close the connection
        logging.info(f"Auto-reply sent to {to_email}")

    except Exception as e:
        logging.error(f"Error sending email to {to_email}: {e}")

# Function to check inbox for unread emails and send replies
def check_and_reply():
    try:
        # Connect to the Gmail IMAP server
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(USERNAME, PASSWORD)
        mail.select('inbox')

        # Search for all unread emails
        status, messages = mail.search(None, '(UNSEEN)')

        # If there are any unread emails
        if status == "OK":
            for num in messages[0].split():
                # Fetch the email by ID
                status, data = mail.fetch(num, '(RFC822)')

                for response_part in data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])

                        # Get the subject and sender
                        subject = msg["subject"]
                        from_email = parseaddr(msg["from"])[1]

                        # Check if subject matches the trigger subject
                        if TRIGGER_SUBJECT in subject and "Re:" not in subject:
                            logging.info(f"Found matching email from {from_email}")

                            # Extract the first word from the body as the reply-to email
                            body = get_email_body(msg)
                            reply_to_email = extract_first_word(body)
                            if reply_to_email:
                                logging.info(f"Replying to {reply_to_email}")
                                # Send the auto-reply to the extracted email address
                                send_auto_reply(reply_to_email)
                            else:
                                logging.warning(f"No valid email found in the body of the email from {from_email}")

                            # Mark email as read
                            mail.store(num, '+FLAGS', '\\Seen')

        # Close the connection and logout
        mail.close()
        mail.logout()

    except Exception as e:
        logging.error(f"Error checking inbox: {e}")

# Helper function to get the email body from the message
def get_email_body(msg):
    """Extracts the email body from the message."""
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            if "attachment" not in content_disposition:
                if content_type == "text/plain":
                    body = part.get_payload(decode=True).decode()
                    break
    else:
        body = msg.get_payload(decode=True).decode()
    return body

# Helper function to extract the first word from the email body
def extract_first_word(body):
    """Extracts the first word from the email body."""
    words = body.split()
    if words:
        return words[0]
    return None

# Run the check-and-reply every 5 minutes
if __name__ == "__main__":
    while True:
        check_and_reply()
        time.sleep(300)  # Sleep for 5 minutes before checking again