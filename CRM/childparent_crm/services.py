# services.py
import requests

# мне не нравится то что это хранится здесь, надо перенести куда-то, чтобы я не забыл случайно оставить тут токен
# WHATSAPP CONNECT TOKEN
GREENAPI_INSTANCE_ID = '1103146764'
GREENAPI_TOKEN = 'a2aa3f5b916c43e8abfe250440d910cc242ef66b415a4152a2'

class WhatsAppService:
    def __init__(self):
        self.instance_id = GREENAPI_INSTANCE_ID
        self.token = GREENAPI_TOKEN
        self.base_url = f"https://api.green-api.com/waInstance{self.instance_id}"

    def send_message(self, phone, message):
        endpoint = f"{self.base_url}/sendMessage/{self.token}"
        payload = {
            "chatId": f"{phone}@c.us",
            "message": message
        }
        try:
            response = requests.post(endpoint, json=payload)
            return response.ok
        except Exception as e:
            print(f"Error sending message: {str(e)}")
            return False
