import json
import allure
import requests
from config import BASE_URL, TIMEOUT, ORDER_TIMEOUT

SENSITIVE = {'password', 'accessToken', 'refreshToken', 'token'}

def redact(value):
    if isinstance(value, dict):
        return {key: '***' if key in SENSITIVE else redact(item) for key, item in value.items()}
    if isinstance(value, list):
        return [redact(item) for item in value]
    return value

class BurgerApi:
    def __init__(self):
        self.session = requests.Session()

    def request(self, method, path, payload=None, token=None):
        with allure.step(f'{method} {path}'):
            if payload is not None:
                allure.attach(json.dumps(redact(payload), ensure_ascii=False), 'Тело запроса', allure.attachment_type.JSON)
            response = self.session.request(
                method, BASE_URL + path, json=payload,
                headers={'Authorization': token} if token else {},
                timeout=ORDER_TIMEOUT if path == '/api/orders' else TIMEOUT,
            )
            allure.attach(str(response.status_code), 'HTTP статус', allure.attachment_type.TEXT)
            try:
                body = json.dumps(redact(response.json()), ensure_ascii=False)
            except ValueError:
                body = response.text
            allure.attach(body, 'Ответ', allure.attachment_type.TEXT)
            return response

    def register(self, payload):
        return self.request('POST', '/api/auth/register', payload)

    def login(self, payload):
        return self.request('POST', '/api/auth/login', payload)

    def delete_user(self, token):
        return self.request('DELETE', '/api/auth/user', token=token)

    def ingredients(self):
        return self.request('GET', '/api/ingredients')

    def create_order(self, payload, token=None):
        return self.request('POST', '/api/orders', payload, token)
