import json
from main import bot


def get_button(text, color):
    return {
        "action": {
            "type": "text",
            "payload": "{\"button\": \"" + "1" + "\"}",
            "label": f"{text}"
        },
        "color": f"{color}",
    }


keyboard = {
    "one_time": True,
    "buttons": [
        [get_button('Начать поиск', 'primary')],
    ]
}

keyboard_without_search = {
    "one_time": False,
    "buttons": [
        [get_button('Вперед', 'primary')]
    ]
}

keyboard_new_forms = {
    "one_time": True,
    "buttons": [
        [get_button('Поиск новых анкет', 'primary')],
    ]
}


def sender(user_id, text):
    bot.vk.method('messages.send', {'user_id': user_id,  'message': text, 'keyboard': keyboard, 'random_id': 0})


def sender_without_search(user_id, text):
    bot.vk.method('messages.send', {'user_id': user_id,  'message': text, 'keyboard': keyboard_without_search, 'random_id': 0})


def sender_new_forms(user_id, text):
    bot.vk.method('messages.send', {'user_id': user_id,  'message': text, 'keyboard': keyboard_new_forms, 'random_id': 0})


keyboard = json.dumps(keyboard, ensure_ascii=False).encode('utf-8')
keyboard = str(keyboard.decode('utf-8'))
keyboard_without_search = json.dumps(keyboard_without_search, ensure_ascii=False).encode('utf-8')
keyboard_without_search = str(keyboard_without_search.decode('utf-8'))
keyboard_new_forms = json.dumps(keyboard_new_forms, ensure_ascii=False).encode('utf-8')
keyboard_new_forms = str(keyboard_new_forms.decode('utf-8'))