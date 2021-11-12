from pprint import pprint
import requests
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import json


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
      'fields': 'sex, city, status, relation, bdate'
      }
    req = requests.get(self.UsersInfo_url, params={**self.params, **self.UsersInfo_params}).json()
    pprint(req)

    if 'sex' in req['response'][0]:
      client_sex = req['response'][0]['sex']
    else:
      client_sex = ''
  #   пол. Возможные значения:
  # 1 — женский;
  # 2 — мужской;
  # 0 — пол не указан.

    if 'title' in req['response'][0]['city']:
      client_city = req['response'][0]['city']['title']
    else:
      client_city = ''

    if 'bdate' in req['response'][0]:
      client_bdate = req['response'][0]['bdate']
      client_info = {}
      client_bdate = str(client_bdate)
      bdate = client_bdate[-4:]
      bdate = int(bdate)
    else:
      bdate = ''

    if 'relation' in req['response'][0]:
      client_relation = req['response'][0]['relation']
    else:
      client_relation = ''
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
    # print(client_sex, client_city, client_bdate, client_relation)
    client_info = {}  
    client_info['sex'] = client_sex
    client_info['city'] = client_city
    client_info['bdate'] = bdate
    client_info['status'] = client_relation
    return client_info

# Если информации недостаточно, запрашиваем необходимую.
  def UsersInfo_all(self, client_info):
      
    client_info_all = client_info

    if client_info['bdate'] == '':
      bdate = input('Введите год рождения')
      client_info_all['bdate'] = bdate

    if client_info['sex'] == '':
      sex = input('Выберите и впишите индекс вашего пола. (1-женщина, 2-мужчина)')
      client_info_all['sex'] = sex

    if client_info['status'] == '':
      print('Введите статус вашего семейного положения? 1-не женат/не замужем; 2 — есть друг/есть подруга; 3 — помолвлен/помолвлена; 4 — женат/замужем; 5 — всё сложно; 6 — в активном поиске; 7 — влюблён/влюблена; 8 — в гражданском браке;')
      status = input()
      if status == '1' or status == '5' or status == '6':
        client_info_all['status'] = status
      elif status == '2' or status == '3' or status == '4' or status == '7' or status == '8':
        print('Иди к своей половинке')
      else:
        print('Вы ввели неверное значение')


    if client_info['city'] == '':
      city = input('Введите название вашего города')
      client_info_all['city'] = city

    return client_info_all

# Подбираем параметры для пары клиента и ищем 3 подходящих кандидатов 
  def search_pare(self, client_info_all):
    pare_info = {}
    pare_info['status'] = '1'
    pare_info['city'] = client_info_all['city']
    if client_info_all['sex'] == 1:
      pare_info['sex'] = '2'
    elif client_info_all['sex'] == 2:
      pare_info['sex'] = '1'
    if client_info_all['sex'] == 1:
      pare_info['age_from'] = 2021 - int(client_info_all['bdate'])
      pare_info['age_to'] = 2021 - int(client_info_all['bdate']) + 5
    elif client_info_all['sex'] == 2:
      pare_info['age_from'] = 2021 - int(client_info_all['bdate']) - 5
      pare_info['age_to'] = 2021 - int(client_info_all['bdate'])
    print(pare_info)

    self.search_id_url = self.url + 'users.search'
    self.search_id_params = {
      'count': 3,
      'sex': pare_info['sex'],
      'hometown': pare_info['city'],
      'status': pare_info['status'],
      'age_from' : pare_info['age_from'],
      'age_to' : pare_info['age_to']
    }
    req = requests.get(self.search_id_url, params={**self.params, **self.search_id_params}).json() 
    pare1 = req['response']['items'][0]['id']
    pare2 = req['response']['items'][1]['id']
    pare3 = req['response']['items'][2]['id']
    pare = [pare1, pare2, pare3]
    return pare

# Поиск фото по id аккаунта, сортировка фото по популярности
  def search_photos(self, owner_id, sorting=0):
    self.photos_search_url = self.url + 'photos.get'
    self.photos_search_params = {
      'count': 50,
      'owner_id': owner_id,
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
    url_pare = 'https://vk.com/id' + str(owner_id)

    return photos_dict

if __name__ == "__main__":
   
  # Получение ТОКЕНА. Если нет прикрепленного файла, используем ручной ввод.
  with open('token_VK_group.txt', 'r') as file_object:
    token_VK_group = file_object.read().strip()
  with open('token_VK.txt', 'r') as file_object:
    token_VK = file_object.read().strip()



  # VK = VKinder_Bot()
  vk_group = vk_api.VkApi(token=token_VK_group)
  vk_session = vk_group.get_api()
  longpoll = VkLongPoll(vk_group)
  vk_client = VkUser(token_VK)



  id_client = 135378796

  def search_pare_photos(id_client, vk_client):
    client_info = vk_client.UsersInfo(id_client)
    # pprint(client_info)

    client_info_all = vk_client.UsersInfo_all(client_info)
    # pprint(client_info_all)

    pare_info = vk_client.search_pare(client_info_all)
    pprint(pare_info)

    url_pare = 'https://vk.com/id' + str(pare_info[0])

    photo1 = vk_client.search_photos(pare_info[0])
    photo2 = vk_client.search_photos(pare_info[1])
    photo3 = vk_client.search_photos(pare_info[2])
    sms = str(url_pare) + ' ' + str(photo1[0][0]) + ' ' + str(photo2[0][0]) + ' ' + str(photo3[0][0])
    return(sms)

  # pprint(search_pare_photos(id_client, vk_client))


    # Создадим функцию для ответа на сообщения в лс группы
  def blasthack(id, text):
      vk_group.method('messages.send', {'user_id' : id, 'message' : text, 'random_id': 0})


 # Слушаем longpoll(Сообщения)
  for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:

      # Чтобы наш бот не слышал и не отвечал на самого себя
      if event.to_me:

        # Для того чтобы бот читал все с маленьких букв 
        message = event.text.lower()

        # Получаем id пользователя
        id_client = event.user_id

        # Структура переписки
        if message == 'привет':
          blasthack(id_client, 'Для подбора пары введите 1')
          
        elif message == '1':
          sms = search_pare_photos(id_client, vk_client)
          blasthack(id_client, sms)
          

        elif message == 'как дела?':
          blasthack(id_client, 'Хорошо, а твои как?')


        else:
          blasthack(id_client, 'Я вас не понимаю! :(')









