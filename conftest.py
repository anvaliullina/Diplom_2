from uuid import uuid4
import logging
import pytest
from clients.burger_api import BurgerApi

logger = logging.getLogger(__name__)


@pytest.fixture
def api():
    client = BurgerApi()
    yield client
    client.session.close()


@pytest.fixture
def user_data(api):
    data = {
        'email': f'anna.qa.{uuid4().hex}@example.com',
        'password': 'QaTest!123456',
        'name': 'Anna QA',
    }
    yield data
    # Очистка — техническое действие, а не проверка тестового сценария.
    response = api.login({'email': data['email'], 'password': data['password']})
    if response.status_code == 200:
        deletion = api.delete_user(response.json()['accessToken'])
        if deletion.status_code != 202:
            logger.warning('Не удалось удалить тестового пользователя: HTTP %s', deletion.status_code)
    elif response.status_code != 401:
        logger.warning('Не удалось проверить очистку пользователя: HTTP %s', response.status_code)


@pytest.fixture
def registered_user(api, user_data):
    response = api.register(user_data)
    response.raise_for_status()
    body = response.json()
    if not body.get('success') or 'accessToken' not in body:
        raise RuntimeError('API не создал тестового пользователя: некорректный ответ регистрации')
    return {**user_data, 'token': body['accessToken']}


@pytest.fixture
def ingredient_ids(api):
    response = api.ingredients()
    response.raise_for_status()
    ingredients = response.json()['data']
    bun = next(item['_id'] for item in ingredients if item['type'] == 'bun')
    filling = next(item['_id'] for item in ingredients if item['type'] == 'main')
    return [bun, filling, bun]
