from main import *
from database import *
from keyboard import sender

for event in bot.longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        request = event.text.lower()
        user_id = str(event.user_id)
        if request == 'начать':
            sender(user_id, request)
        elif request == 'начать поиск':
            creating_database()
            bot.find_user(user_id)
            bot.write_msg(event.user_id, f'Нашёл для тебя пару, жми на кнопку "Вперед"')
        elif request == 'вперед':
            for i in line:
                offset += 1
                bot.find_persons(user_id, offset)
                break

        else:
            bot.write_msg(event.user_id, 'Твоё сообщение непонятно')
