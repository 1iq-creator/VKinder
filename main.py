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

    def get_user_info(self, user_id):
        url = 'https://api.vk.com/method/users.get'
        params = {
            'access_token': user_token,
            'user_ids': user_id,
            'fields': 'city, sex, bdate',
            'v': '5.131'
        }
        res = requests.get(url, params=params)
        response = res.json()

        try:
            information = response['response']
        except KeyError:
            self.write_msg(user_id, 'Ошибка получения токена')
            return None

        city = None
        sex = None
        bdate = None

        for i in information:
            city = i.get('city', {}).get('title')
            sex = i.get('sex')
            bdate = i.get('bdate')
            date_split = bdate.split('.')
            if len(date_split) == 3:
                year = int(date_split[2])
                year_now = int(datetime.date.today().year)
                bdate = year_now - year
            else:
                bdate = None

            if city and sex and bdate:
                break

        if not city:
            self.write_msg(user_id, 'Введите ваш город: ')
            for event in self.longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    city = event.text
                    break

        if sex == 0 or not sex:
            self.write_msg(user_id, 'Введите ваш пол (1 — женский; 2 — мужской): ')
            for event in self.longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    sex = event.text
                    break

        if not bdate:
            self.write_msg(user_id, 'Введите сколько вам лет ')
            for event in self.longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    bdate = event.text
                    break
        if sex == 1:
            sex = 2
        elif sex == 2:
            sex = 1
        return city, sex, bdate

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

    def find_user(self, user_id, offset):
        url = f'https://api.vk.com/method/users.search'
        age = self.get_user_info(user_id)[2]
        params = {'access_token': user_token,
                  'v': '5.131',
                  'sex': self.get_user_info(user_id)[1],
                  'age_from': age,
                  'age_to': age,
                  'city': self.get_city_id(user_id, self.get_user_info(user_id)[0]),
                  'fields': 'is_closed, id',
                  'status': '1' or '6',
                  'offset': offset,
                  'count': 30}
        res = requests.get(url, params=params)
        response = res.json()
        try:
            dict_1 = response['response']
        except KeyError:
            self.write_msg(user_id, 'Ошибка получения токена')
        list_1 = dict_1['items']
        forms = []
        for person_dict in list_1:
            if not person_dict.get('is_closed'):
                vk_id = str(person_dict.get('id'))
                forms.append(vk_id)
            else:
                continue
        return forms

    def get_popular_photos(self, user_id):
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
            self.vk.method('messages.send',
                           {'user_id': user_id, 'attachment': attachments, 'random_id': randrange(10 ** 7)})

    def find_persons(self, user_id, offset, list_id):
        try:
            insert_data_users(list_id[offset])
            self.write_msg(user_id, 'vk.com/id' + str(list_id[offset]))
            self.send_photos(user_id, self.get_popular_photos(list_id[offset]))
        except IndexError:
            self.write_msg(user_id, 'Анкеты закончились')
            return 'need_new_forms'


bot = VKBot()