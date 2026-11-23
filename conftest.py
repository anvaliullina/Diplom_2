from uuid import uuid4
import pytest
from clients.burger_api import BurgerApi

@pytest.fixture
def api():
    client = BurgerApi()
    yield client
    client.session.close()

@pytest.fixture
def user_data(api):
    data = {'email': f'anna.qa.{uuid4().hex}@example.com', 'password': 'QaTest!123456', 'name': 'Anna QA'}
    yield data
    # Cleanup also runs when registration/assertions fail after a user was created.
    response = api.login({'email': data['email'], 'password': data['password']})
    if response.status_code == 200:
        deleted = api.delete_user(response.json()['accessToken'])
        assert deleted.status_code == 202, f'Не удалось удалить тестового пользователя: {deleted.status_code}'
    else:
        assert response.status_code == 401, f'Не удалось проверить очистку пользователя: {response.status_code}'

@pytest.fixture
def registered_user(api, user_data):
    response = api.register(user_data)
    assert response.status_code == 200, response.text
    assert response.json()['success'] is True
    return {**user_data, 'token': response.json()['accessToken']}

@pytest.fixture
def ingredient_ids(api):
    response = api.ingredients()
    assert response.status_code == 200, response.text
    ingredients = response.json()['data']
    bun = next(item['_id'] for item in ingredients if item['type'] == 'bun')
    filling = next(item['_id'] for item in ingredients if item['type'] == 'main')
    return [bun, filling, bun]
