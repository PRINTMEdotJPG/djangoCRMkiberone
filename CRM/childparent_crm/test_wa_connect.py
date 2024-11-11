# test_connection.py
from services import WhatsAppService

whatsapp = WhatsAppService()
test_phone = "221772724842"  # номер в формате 7XXXXXXXXXX
result = whatsapp.send_message(test_phone, "Тестовое сообщение")
print(f"Результат отправки: {result}")