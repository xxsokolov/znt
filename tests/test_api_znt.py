####################################
#          Sokolov Dmitry          #
#       xx.sokolov@gmail.com       #
#        https://t.me/ZbxNTg       #
####################################
# https://github.com/xxsokolov/znt #
####################################
import sys
import pytest
import requests

url = 'http://192.168.1.118/api/znt/{route}'
headers = {'Content-Type': 'application/json'}


def test_znt_healthcheck():
    """
    Тестирование API: znt.healthcheck: GET: Показать статус api
    """
    responce = requests.get(url=url.format(route='healthcheck'), headers=headers)
    assert responce.status_code == 200, 'Не валидный код ответа'
    responce_dict = responce.json()
    assert responce_dict['status'] == 'ok', 'Значение ключа status в ответе не соответствует "ok"'


def test_znt_bot_get_all():
    """
    Тестирование API: znt.bot: GET: Поиск бота без параметров
    """
    responce = requests.get(url=url.format(route='bot'), headers=headers)
    assert responce.status_code == 200, 'Не валидный код ответа'
    responce_dict = responce.json()
    assert responce_dict == [
        {'name': '@znt_test_bot', 'group': 'infra', 'description': 'test bot 1', 'priority': 0, 'id': 1, 'proxy_use': False, 'proxy': None},
        {'name': '@znt_test_test_bot', 'group': 'dba', 'description': 'test bot 2', 'priority': 1, 'id': 2, 'proxy_use': False, 'proxy': None},
        {'name': '@znt_test_test_bot', 'group': 'hr', 'description': 'test bot 2', 'priority': 1, 'id': 4, 'proxy_use': False, 'proxy': None},
        {'name': '@znt_test_bot', 'group': 'hd', 'description': 'test bot 1', 'priority': 0, 'id': 5, 'proxy_use': False, 'proxy': None}
    ]


@pytest.mark.add_get_del
def test_znt_bot_post():
    """
    Тестирование API: znt.bot: POST: Добавление/Чтение/Удаление бота
    """
    import secrets
    token = secrets.token_hex(16)
    data = {"name": "@pytest_bot", "description": "Бот создан для тестирования API", "bot_group": "test", "priority": 0, "token": f"{token}"}
    responce_add = requests.post(url=url.format(route='bot'), json=data, headers=headers)
    assert responce_add.status_code == 200, 'Не валидный код ответа'
    assert responce_add.json() == dict(status="Бот @pytest_bot добавлен",
                                 detail=dict(
                                     name='@pytest_bot', group=None, description='Бот создан для тестирования API',
                                     priority=0, token=f"{token}")
                                 ), 'Не ожидаемый ответ'

    responce_search_name = requests.get(url=url.format(route='bot?name=@pytest_bot'), headers=headers)
    assert responce_search_name.status_code == 200, 'Не валидный код ответа'
    responce_search_name_json = responce_search_name.json()
    assert responce_search_name.json() == [{'name': '@pytest_bot', 'group': None, 'description': 'Бот создан для тестирования API',
                             'priority': 0, 'id': responce_search_name_json[0]['id'], 'proxy_use': False, 'proxy': None
                             }]

    responce_search_id = requests.get(url=url.format(route="bot?id={id}".format(id=responce_search_name_json[0]['id'])), headers=headers)
    assert responce_search_id.status_code == 200, 'Не валидный код ответа'
    assert responce_search_id.json() == [{'name': '@pytest_bot', 'group': None, 'description': 'Бот создан для тестирования API',
                             'priority': 0, 'id': responce_search_name_json[0]['id'], 'proxy_use': False, 'proxy': None
                             }]

    responce = requests.delete(url=url.format(route=f"bot/{responce_search_name_json[0]['id']}"), headers=headers)
    assert responce.status_code == 200, 'Не валидный код ответа'
    responce_dict = responce.json()
    assert responce_dict == {'status': 'Бот @pytest_bot ({id}) удален'.format(id=responce_search_name_json[0]['id'])}
