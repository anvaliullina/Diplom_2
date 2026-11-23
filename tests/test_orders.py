
import allure
import pytest


@allure.feature('Создание заказа')
class TestOrders:

    @allure.title('Создание заказа с авторизацией и ингредиентами')
    def test_authorized_order_with_ingredients(self, api, registered_user, ingredient_ids):
        response = api.create_order({'ingredients': ingredient_ids}, registered_user['token'])
        assert response.status_code == 200
        body = response.json()
        assert body['success'] is True
        assert isinstance(body['order']['number'], int)
        assert body['order']['number'] > 0
        assert body['name']

    @pytest.mark.xfail(
        reason='Известный дефект API: заказ без авторизации создаётся, сервер отвечает 200 вместо 401',
        strict=True
    )
    @allure.title('Создание заказа без авторизации отклоняется')
    def test_order_without_authorization(self, api, ingredient_ids):
        response = api.create_order({'ingredients': ingredient_ids})
        assert response.status_code == 401, response.text
        assert response.json()['success'] is False

    @pytest.mark.parametrize(
        'payload',
        [{'ingredients': []}, {}],
        ids=['empty_list', 'missing_field']
    )
    @allure.title('Создание заказа без ингредиентов: {payload}')
    def test_order_without_ingredients(self, api, registered_user, payload):
        response = api.create_order(payload, registered_user['token'])
        assert response.status_code == 400
        assert response.json() == {
            'success': False,
            'message': 'Ingredient ids must be provided'
        }

    @allure.title('Создание заказа с неверным хешем ингредиента')
    def test_order_with_invalid_hash(self, api, registered_user):
        response = api.create_order(
            {'ingredients': ['invalid-ingredient-hash']},
            registered_user['token']
        )
        assert response.status_code == 500
