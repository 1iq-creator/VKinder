from random import randrange
import datetime
import vk_api
import requests
from vk_api.longpoll import VkLongPoll, VkEventType
from database import *


class VKBot:
    def __init__(self):
        self.vk = vk_api.VkApi(token=comm_token)
        self.longpoll = VkLongPoll(self.vk)

    def write_msg(self, user_id, message):
        self.vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7)})

    def get_bdate(self, user_id):
        url = f'https://api.vk.com/method/users.get'
        params = {'access_token': user_token,
                  'user_ids': user_id,
                  'fields': 'bdate',
                  'v': '5.131'}
        res = requests.get(url, params=params)
        response = res.json()
        try:
            information = response['response']
            for i in information:
                date = i.get('bdate')
            date_split = date.split('.')
            if len(date_split) == 3:
                year = int(date_split[2])
                year_now = int(datetime.date.today().year)
                return year_now - year
            elif len(date_split) == 2 or 'date' not in i:
                self.write_msg(user_id, 'Введите сколько вам лет: ')
                for event in self.longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                        age = event.text
                        return age
        except KeyError:
            self.write_msg(user_id, 'Ошибка получения токена ')

    def get_sex(self, user_id):
        url = f'https://api.vk.com/method/users.get'
        params = {'access_token': user_token,
                  'user_ids': user_id,
                  'fields': 'sex',
                  'v': '5.131'}
        res = requests.get(url, params=params)
        response = res.json()
        try:
            information = response['response']
            for i in information:
                sex = i.get('sex')
            if sex == 0 or 'sex' not in i:
                self.write_msg(user_id, 'Введите ваш пол (1 — женский; 2 — мужской): ')
                for event in self.longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                        sex = event.text
                        return sex
            elif sex == 1:
                sex = 2
                return sex
            elif sex == 2:
                sex = 1
                return sex
        except KeyError:
            self.write_msg(user_id, 'Ошибка получения токена')

    def get_city(self, user_id):
        url = f'https://api.vk.com/method/users.get'
        params = {'access_token': user_token,
                  'user_ids': user_id,
                  'fields': 'city',
                  'v': '5.131'}
        res = requests.get(url, params=params)
        response = res.json()
        try:
            information = response['response']
            for i in information:
                city = i['city']['title']
            if 'city' in i:
                return city
            elif city == 0 or 'city' not in i:
                self.write_msg(user_id, 'Введите ваш город: ')
                for event in self.longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                        city = event.text
                        return city
        except KeyError:
            self.write_msg(user_id, 'Ошибка получения токена')

    def get_city_id(self, user_id, city_name):
        url = url = f'https://api.vk.com/method/database.getCities'
        params = {'access_token': user_token,
                  'q': city_name,
                  'v': '5.131'}
        res = requests.get(url, params=params)
        response = res.json()
        try:
            city_id = response['response']['items'][0]['id']
            return city_id
        except KeyError:
            self.write_msg(user_id, 'Ошибка получения токена')

    def find_user(self, user_id):
        url = f'https://api.vk.com/method/users.search'
        age = self.get_bdate(user_id)
        params = {'access_token': user_token,
                  'v': '5.131',
                  'sex': self.get_sex(user_id),
                  'age_from': age,
                  'age_to': age,
                  'city': self.get_city_id(user_id, self.get_city(user_id)),
                  'fields': 'is_closed, id, first_name, last_name, screen_name, city',
                  'status': '1' or '6',
                  'count': 500}
        res = requests.get(url, params=params)
        response = res.json()
        try:
            dict_1 = response['response']
            list_1 = dict_1['items']
            for person_dict in list_1:
                if not person_dict.get('is_closed'):
                    first_name = person_dict.get('first_name')
                    last_name = person_dict.get('last_name')
                    vk_id = str(person_dict.get('id'))
                    vk_link = 'vk.com/' + str(person_dict.get('screen_name'))
                    insert_data_users(first_name, last_name, vk_id, vk_link)
                else:
                    continue
            return f'Поиск завершён'
        except KeyError:
            self.write_msg(user_id, 'Ошибка получения токена')

    def person_info(self, offset):
        tuple_person = select(offset)
        list_person = []
        for i in tuple_person:
            list_person.append(i)
        return f'{list_person[0]} {list_person[1]}, ссылка - {list_person[3]}'

    def get_person_id(self, offset):
        tuple_person = select(offset)
        list_person = []
        for i in tuple_person:
            list_person.append(i)
        return str(list_person[2])

    def get_popular_photos(self, user_link):
        response = requests.get('https://api.vk.com/method/utils.resolveScreenName', params={
            'access_token': user_token,
            'v': '5.131',
            'screen_name': user_link.split('/')[-1]
        })
        data = response.json()
        user_id = data['response']['object_id']
        response = requests.get('https://api.vk.com/method/photos.get', params={
            'access_token': user_token,
            'v': '5.131',
            'owner_id': user_id,
            'album_id': 'profile',
            'extended': 1
        })
        data = response.json()
        photos = data['response']['items']
        if len(photos) < 1:
            return
        sorted_photos = sorted(photos, key=lambda x: (x['likes']['count'] if 'likes' in x else 0) + (
            x['comments']['count'] if 'comments' in x else 0), reverse=True)
        photo_attachments = []
        for photo in sorted_photos[:3]:
            photo_attachments.append(f"photo{photo['owner_id']}_{photo['id']}")
        photo_attachments = ','.join(photo_attachments)
        return photo_attachments

    def send_photos(self, user_id, attachments):
        if attachments is None:
            self.write_msg(user_id, 'Фотографий не найдено')
        else:
            self.vk.method('messages.send', {'user_id': user_id, 'attachment': attachments, 'random_id': randrange(10 ** 7)})

    def find_persons(self, user_id, offset):
        self.write_msg(user_id, self.person_info(offset))
        list_person = self.person_info(offset).split(' ')
        insert_data_seen_users(self.get_person_id(offset))
        self.send_photos(user_id, self.get_popular_photos(list_person[4]))


bot = VKBot()
