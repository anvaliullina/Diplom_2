from uuid import uuid4
import allure
import pytest

@allure.feature('Логин пользователя')
class TestLogin:
    @allure.title('Вход с email и паролем зарегистрированного пользователя')
    def test_existing_user(self, api, registered_user):
        response = api.login({key: registered_user[key] for key in ('email', 'password')})
        assert response.status_code == 200
        body = response.json()
        assert body['success'] is True
        assert body['user']['email'] == registered_user['email']
        assert body['user']['name'] == registered_user['name']
        assert body['accessToken'].startswith('Bearer ')
        assert body['refreshToken']

    @pytest.mark.parametrize('wrong_field', ['email', 'password', 'both'])
    @allure.title('Вход: неверные учётные данные — {wrong_field}')
    def test_wrong_credentials(self, api, registered_user, wrong_field):
        payload = {key: registered_user[key] for key in ('email', 'password')}
        if wrong_field in ('email', 'both'):
            payload['email'] = f'absent.{uuid4().hex}@example.com'
        if wrong_field in ('password', 'both'):
            payload['password'] = 'WrongPassword!654321'
        response = api.login(payload)
        assert response.status_code == 401
        assert response.json() == {'success': False, 'message': 'email or password are incorrect'}
