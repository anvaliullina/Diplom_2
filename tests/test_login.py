from uuid import uuid4
import allure
import pytest

UNREGISTERED_EMAIL = f'unregistered.{uuid4().hex}@example.com'


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

    @pytest.mark.parametrize(
        'incorrect_fields',
        [
            pytest.param({'email': UNREGISTERED_EMAIL}, id='email'),
            pytest.param({'password': 'WrongPassword!654321'}, id='password'),
            pytest.param({
                'email': UNREGISTERED_EMAIL,
                'password': 'WrongPassword!654321',
            }, id='both'),
        ],
    )
    @allure.title('Вход: неверные учётные данные')
    def test_wrong_credentials(self, api, registered_user, incorrect_fields):
        payload = {key: registered_user[key] for key in ('email', 'password')}
        payload.update(incorrect_fields)
        response = api.login(payload)
        assert response.status_code == 401
        assert response.json() == {'success': False, 'message': 'email or password are incorrect'}
