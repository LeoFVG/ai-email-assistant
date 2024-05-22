import imaplib
from getpass import getpass
from email import message_from_bytes
from email import message_from_bytes
from email.message import Message
from email.header import decode_header
from bs4 import BeautifulSoup
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging

class Email:
    """
    A class to represent an email.
    """

    def __init__(self, raw_email: bytes, uid: str) -> None:
        """
        Constructs all the necessary attributes for the Email object.

        :param raw_email: raw email content in bytes
        """
        self.raw_email = raw_email
        self.uid = uid
        self.msg = self._get_message_from_bytes(raw_email)
        self.subject = self._decode_header(self.msg["subject"])
        self.sender = self._decode_header(self.msg["from"])
        self.reciever = self._decode_header(self.msg["to"])
        self.body = self.get_html_body()
        self.attachments = None
        self.processed_data = self.process_html_body() # {sender, text}
        self.links = None
        self.images = None

    @staticmethod
    def _get_message_from_bytes(raw_email: bytes) -> Message:
        """
        Convert raw email bytes into a Message object.

        :param raw_email: raw email content in bytes
        :return: a Message object
        """
        try:
            return message_from_bytes(raw_email)
        except Exception as e:
            logging.error(f"Failed to convert raw email into a Message object: {e}", exc_info=True)
            return None

    def get_html_body(self) -> str:
        """
        Extracts the HTML body of the email.

        :return: the HTML body of the email
        """
        if self.msg is None:
            return ""

        try:
            if self.msg.is_multipart():
                for part in self.msg.walk():
                    if part.get_content_type() == 'text/html':
                        payload = part.get_payload(decode=True)
                        return payload.decode('utf-8', errors='replace')
            else:
                if self.msg.get_content_type() == 'text/html':
                    payload = self.msg.get_payload(decode=True)
                    return payload.decode('utf-8', errors='replace')
        except Exception as e:
            logging.error(f"Failed to get HTML body: {e}", exc_info=True)
            return ""

    def _decode_header(self, header):
        """
        Decodes the header.

        :param header: the header to decode
        :return: the decoded header
        """
        if header is None:
            return None

        decoded_header = decode_header(header)
        header_parts = []
        for part, encoding in decoded_header:
            if encoding is not None:
                part = part.decode(encoding, errors='replace')
            else:
                part = part if isinstance(part, str) else part.decode('utf-8', errors='replace')
            header_parts.append(part)
        return ' '.join(header_parts)

    def process_html_body(self) -> dict:
        """
        Processes the HTML body of the email and extracts important data.

        :return: a dictionary containing the processed data
        """
        processed_data = {}

        processed_data['sender'] = self.sender # Maybe remove <sender address>
        processed_data['subject'] = self.subject

        if self.body:
            soup = BeautifulSoup(self.body, 'html.parser')

            text = soup.get_text()
            # Removing as many unecessary characters as possible to save tokens.
            replacements = ['\n', '\r', '�', " ", "\t"]
            for r in replacements:
                text = text.replace(r, '')
            text = text.encode("ascii", errors="ignore").decode() # remove unicode characters.
            processed_data['text'] = text

            self.links = [a['href'] for a in soup.find_all('a', href=True)]
            self.images = [img['src'] for img in soup.find_all('img', src=True)]

        return processed_data




class EmailClient:
    def __init__(self):
        self.imap = None
        self.password = None
        self.username = None
        self.imap_server = None
        self.smtp = None
        self.smtp_server = None

    
    def _get_server(self, server_type: str, email_address: str):
        if server_type == "imap":
                self.imap = 'imap.' + email_address.split('@')[1]
                if self.imap == "imap.hotmail.com":
                    self.imap = "imap.outlook.com"

        elif server_type == "smtp":
                self.smtp = 'smtp.' + email_address.split('@')[1]
                if self.smtp == "smtp.hotmail.com":
                    self.smtp = "smtp.outlook.com"
        else:
            print("_get_server() failed")
            return 1

    def connect(self, username=None, password=None):
        if username is not None and password is not None:
            self.username = username
            self.password =  password
        else:
            print(f"\n{'='*50}\nPlease login to your email.\n{'='*50}")
            self.username = input('Username: ')
            self.password = getpass('Password: ')

        #self.imap = 'imap.' + self.username.split('@')[1]
        #if self.imap == "imap.hotmail.com":
        #    self.imap = "imap.outlook.com"
        self._get_server("imap", self.username)

        try:
            self.imap_server = imaplib.IMAP4_SSL(self.imap)
            logging.info(f"Username: [{self.username}] logging in to IMAP: [{self.imap}]...")
            self.imap_server.login(self.username, self.password)
            logging.info(f"Successfully connected to IMAP!")
        except Exception as e:
            logging.error(f"Error: {e}", exc_info=True)
            print(f"Could it be your login details are incorrect?\nUsername: {self.username}\nServer: {self.imap}")

    def disconnect(self):
        try:
            self.imap_server.close()
            self.imap_server.logout()
            logging.info("Disconnected from IMAP.")
        except Exception as e:
            logging.error(f"Error: {e}", exc_info=True)
            print("Failed to disconnect from IMAP.")

    def get_mail(self, increment=1, mailbox="inbox", criteria="ALL") -> 'Email':
        if increment == 0:
            increment = 1
        try:
            self.imap_server.select(mailbox)
            _, data = self.imap_server.uid('search', None, criteria)
            latest_email_uid = data[0].split()[-1*increment]
            uid_str = latest_email_uid.decode('utf-8')
            _, data = self.imap_server.uid('fetch', latest_email_uid, '(RFC822)')
            raw_email = data[0][1]
            return Email(raw_email, uid_str)
        except Exception as e:
            logging.error(f"Error: {e}", exc_info=True)
            print("Failed to fetch recent mail.")
            return None

    def send_mail(self, to_address: str, subject: str, message: str):
        """
        Sends an email to a specified receiver.
        """
        port = 587
        self._get_server("smtp", to_address)
        try:
            self.smtp_server = smtplib.SMTP(f"{self.smtp}:{port}")
            self.smtp_server.starttls()
            self.smtp_server.login(self.username, self.password)
            msg = MIMEMultipart()
            msg["From"] = self.username
            msg["To"] = to_address
            msg["Subject"] = subject
            msg.attach(MIMEText(message, "plain"))
            self.smtp_server.send_message(msg)
        except Exception as e:
            print(f"Error occurred: {e}")
        finally:
            self.smtp_server.quit()
