from src.assistant import EmailAssistant
from src.email_utils import EmailClient, Email
from src.save_file import log_config
import logging
from datetime import datetime

log_config()

MODEL_NAME = "claude-3-haiku-20240307"
API_KEY = ""
EMAIL_USERNAME = ""
EMAIL_PASSWORD = ""
assistant = EmailAssistant(api_key=API_KEY, model=MODEL_NAME)

def main():
    assistant.assistant()

if __name__ == "__main__":
    main()