import allure
import pytest

@allure.feature('Создание пользователя')
class TestRegistration:
    @allure.title('Регистрация пользователя с уникальным email')
    def test_unique_user(self, api, user_data):
        response = api.register(user_data)
        assert response.status_code == 200
        body = response.json()
        assert body['success'] is True
        assert body['user'] == {'email': user_data['email'], 'name': user_data['name']}
        assert body['accessToken'].startswith('Bearer ')
        assert body['refreshToken']

    @allure.title('Повторная регистрация с email существующего пользователя')
    def test_duplicate_user(self, api, registered_user):
        data = {key: registered_user[key] for key in ('email', 'password', 'name')}
        response = api.register(data)
        assert response.status_code == 403
        assert response.json() == {'success': False, 'message': 'User already exists'}

    @pytest.mark.parametrize('field', ['email', 'password', 'name'])
    @pytest.mark.parametrize('mode', ['missing', 'empty'])
    @allure.title('Регистрация: обязательное поле {field}, вариант {mode}')
    def test_required_field(self, api, user_data, field, mode):
        payload = user_data.copy()
        if mode == 'missing':
            payload.pop(field)
        else:
            payload[field] = ''
        response = api.register(payload)
        assert response.status_code == 403
        assert response.json() == {
            'success': False, 'message': 'Email, password and name are required fields'
        }
