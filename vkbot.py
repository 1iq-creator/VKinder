from main import *
from database import *
from keyboard import sender, sender_without_search

for event in bot.longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        request = event.text.lower()
        user_id = str(event.user_id)
        if request == 'начать':
            sender(user_id, request)
            creating_database()
        elif request == 'начать поиск':
            sender_without_search(user_id, request)
            offset = 0
            step_offset = 30
            list_id = bot.find_user(user_id, offset)
            bot.write_msg(event.user_id, f'Нашёл для тебя пару, жми на кнопку "Вперед"')
        elif request == 'вперед':
            forms = bot.find_persons(user_id, offset, list_id)
            if forms == 'need_new_forms':
                list_id = bot.find_user(user_id, step_offset)
                step_offset += step_offset
                offset = 0
                sender_without_search(user_id, request)
            offset += 1
        else:
            bot.write_msg(event.user_id, 'Твоё сообщение непонятно')