import json
from datetime import datetime
import logging
from .email_utils import Email

def cache(msg: Email, data_path: str = "data/data.json") -> None:
    try:
        with open(data_path, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []
    for mail in data:
        if mail["uid"] == msg.uid:
            logging.info(f"Email with uid {msg.uid} already exists in data.json")
            return None
    data.append(
        {
            "uid": msg.uid,
            "processing date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "content": {"from": msg.sender, "to": msg.reciever, "subject": msg.subject, "body": msg.body},
            "ai": { "processed email": msg.processed_data}
        }
        )
    
    with open(data_path, "w") as f:
        json.dump(data, f, indent=4)
        logging.info("saved data to /data.json!")


def log_config() -> None:
    dt = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    logging.basicConfig(level=logging.INFO, filename=f"logs/log.log", filemode="w",
                        format="%(asctime)s - %(levelname)s - %(message)s")