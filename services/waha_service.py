import os
import requests

WAHA_API_URL= os.getenv("WAHA_API_URL", "")
WAHA_SESSION_NAME = os.getenv("WAHA_SESSION_NAME", "")
WAHA_API_KEY = os.getenv("WAHA_API_KEY", "")



def send_message(chat_id: str, message: str):

    headers = {
        'Content-Type': 'application/json',
        'X-Api-Key': WAHA_API_KEY,
    }

    send_url = f"{WAHA_API_URL}/sendText"

    payload = {
        "session": WAHA_SESSION_NAME,
        "chatId": chat_id,
        "text": message
    }   

    return requests.post(url=send_url, headers=headers, json=payload)