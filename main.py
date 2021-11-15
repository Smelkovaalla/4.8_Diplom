from pprint import pprint
import requests
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import json
from random import randint


# Работа с ВК
class VkUser:
  url = 'https://api.vk.com/method/'

  def __init__(self, token):
    self.params = {
      'access_token': token,
      'v': '5.131'
    }

# Метод для поиска необходимой информации о клиенте
  def UsersInfo(self, id_client):
    self.UsersInfo_url = self.url + 'users.get'
    self.UsersInfo_params = {
      'user_ids': id_client,
      'fields': 'sex, city, status, relation, bdate, country'
      }
    req = requests.get(self.UsersInfo_url, params={**self.params, **self.UsersInfo_params}).json()
    req = req['response'][0]
    # pprint(req)
    client_info = {}
    if 'sex' in req:
      client_info['sex'] = req['sex']
  #   пол. Возможные значения:
  # 1 — женский;
  # 2 — мужской;
  # 0 — пол не указан.
    if 'city' in req.keys():
      client_info['city'] = req['city']['title']
    if 'bdate' in req:
      client_bdate = req['bdate']
      client_bdate = str(client_bdate)
      bdate = client_bdate[-4:]
      client_info['bdate'] = int(bdate)
    if 'relation' in req:
      client_info['status'] = req['relation']
  #   семейное положение. Возможные значения:
  # 1 — не женат/не замужем;
  # 2 — есть друг/есть подруга;
  # 3 — помолвлен/помолвлена;
  # 4 — женат/замужем;
  # 5 — всё сложно;
  # 6 — в активном поиске;
  # 7 — влюблён/влюблена;
  # 8 — в гражданском браке;
  # 0 — не указано.
    return client_info

  def search_city(self):
    self.search_city_url = self.url + 'database.getCities'
    city_list = []
    v = [1, 7]
    for c in v:
      self.search_city_params = {
        'count':1000,
        'country_id': c,
        'need_all':0
      }  
      req = requests.get(self.search_city_url, params={**self.params, **self.search_city_params}).json() 
      for i in req['response']['items']:
        a = i['title'].lower()
        city_list.append(a)

    # pprint(city_list)
    return city_list

# Подбираем параметры для пары клиента и ищем 3 подходящих кандидатов 
  def search_pare(self, client_info):
    pare_info = {}
    pare_info['status'] = '6'
    pare_info['city'] = client_info['city']
    if client_info['sex'] == 1:
      pare_info['sex'] = '2'
    elif client_info['sex'] == 2:
      pare_info['sex'] = '1'
    if client_info['sex'] == 1:
      pare_info['age_from'] = 2021 - int(client_info['bdate'])
      pare_info['age_to'] = 2021 - int(client_info['bdate']) + 5
    elif client_info['sex'] == 2:
      pare_info['age_from'] = 2021 - int(client_info['bdate']) - 5
      pare_info['age_to'] = 2021 - int(client_info['bdate'])
    # print(pare_info)

    self.search_id_url = self.url + 'users.search'
    self.search_id_params = {
      'count': 100,
      'sex': pare_info['sex'],
      'hometown': pare_info['city'],
      'status': pare_info['status'],
      'age_from' : pare_info['age_from'],
      'age_to' : pare_info['age_to']
    }
    req = requests.get(self.search_id_url, params={**self.params, **self.search_id_params}).json()
    pprint(req)
    if req['response']['count'] == 0:
      pare_id = 1
      return pare_id
    else:
      num = len(req['response']['items']) 
      m = randint(0, num - 1)
      pare_id = req['response']['items'][m]['id']
      return pare_id

# Поиск фото по id аккаунта, сортировка фото по популярности
  def search_photos(self, pare_id, sorting=0):
    self.photos_search_url = self.url + 'photos.get'
    self.photos_search_params = {
      'count': 50,
      'owner_id': pare_id,
      'extended': 1,
      'album_id': 'profile'
    }
    req = requests.get(self.photos_search_url, params={**self.params, **self.photos_search_params}).json()
    req = req['response']['items']
    photos_count = len(req)

    photos_dict = {}
    i = 0
    while i < photos_count:   
      likes = req[i]['likes']['count']
      comments = req[i]['comments']['count']
      photos_dict[req[i]['sizes'][-1]['url']] = int(likes) + int(comments)
      i += 1
    photos_dict = sorted(photos_dict.items(), key=lambda t: t[1])
    if len(photos_dict) > 3:
      photos_dict = photos_dict[-3:]
    return photos_dict

if __name__ == "__main__":
   
  # Получение ТОКЕНА. Если нет прикрепленного файла, используем ручной ввод.
  with open('token_VK_group.txt', 'r') as file_object:
    token_VK_group = file_object.read().strip()
  with open('token_VK.txt', 'r') as file_object:
    token_VK = file_object.read().strip()


  vk_group = vk_api.VkApi(token=token_VK_group)
  vk_session = vk_group.get_api()
  longpoll = VkLongPoll(vk_group) 
  vk_client = VkUser(token_VK)


  def search_pare_photos(client_info_all):
    pare_id = vk_client.search_pare(client_info_all)
    if pare_id == 1:
      sms = ['Простите, для вас в ВК пары нет, сходите в театр']
      return sms
    else:
      url_pare = 'https://vk.com/id' + str(pare_id)
      photos_dict = vk_client.search_photos(pare_id)
      sms = []
      sms.append(url_pare)
      for i in photos_dict:
        sms.append(i[0])
      return sms


    # Создадим функцию для ответа на сообщения в лс группы
  def blasthack(id, text):
      vk_group.method('messages.send', {'user_id' : id, 'message' : text, 'random_id': 0})

  def chat_bot():
    client_info_all = {}
    # Слушаем longpoll(Сообщения)
    for event in longpoll.listen():
      if event.type == VkEventType.MESSAGE_NEW:
        # Чтобы наш бот не слышал и не отвечал на самого себя
        if event.to_me:
          # Для того чтобы бот читал все с маленьких букв 
          message = event.text.lower()
          # Получаем id пользователя
          user_id = event.user_id
          client_info = vk_client.UsersInfo(user_id)
          city_list = vk_client.search_city()
          pprint(client_info_all)
          # Структура переписки
          if message == 'привет':
            client_info_all = client_info
            if len(client_info) == 4 and client_info_all['status'] != 0:
              blasthack(user_id, 'Ваши данные полные, введите "найди пару"')
            elif len(client_info) == 4 and client_info_all['status'] == 0:
              client_info_all['status'] = 6
              blasthack(user_id, 'Ваш статус неопределен, ищем для вас партнера в активном поиске, введите "найди пару"') 
            elif len(client_info) == 3:
              if 'sex' not in client_info:
                blasthack(user_id, 'Ваш пол не установлен, введите ж или м')
              elif 'city' not in client_info:
                blasthack(user_id, 'Введите название вашего города')
              elif 'bdate' not in client_info:
                blasthack(user_id, 'Введите год вашего рождения')  

          elif message == 'ж':
            client_info_all['sex'] = 1        
            blasthack(user_id, 'Ваши данные полные, введите "найди пару"')  
          elif message == 'м':
            client_info_all['sex'] = 2        
            blasthack(user_id, 'Ваши данные полные, введите "найди пару"')  
          elif message in city_list:
            client_info_all['city'] = message
            blasthack(user_id, 'Ваши данные полные, введите "найди пару"')    
          elif len(str(message)) == 4 and 19 <= int(message)/100 <=20:
            client_info_all['bdate'] = message
            blasthack(user_id, 'Дата рождения принята, Ваши данные полные, введите "найди пару"')
          elif message == 'найди пару':    
            text = search_pare_photos(client_info_all)
            for i in text:
              sms = str(i)
              blasthack(user_id, sms)
          else:
            blasthack(user_id, 'Я вас не понимаю, для начала поиска пары введите "привет"') 


chat_bot()

