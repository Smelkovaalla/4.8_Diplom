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

  def ProfileInfo(self):

    self.ProfileInfo_url = self.url + 'account.getProfileInfo'
    # self.ProfileInfo.params = {
    #   'user_id': id_client
    #   }
    req = requests.get(self.ProfileInfo_url, params={**self.params}).json()
    return req


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
      bdate = client_bdate[5:]
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


  def search_pare(self, client_info_all):
    pare_info = {}
    pare_info['status'] = '1'
    pare_info['city'] = client_info_all['city']
    if client_info_all['sex'] == 1:
      pare_info['sex'] = '2'
    elif client_info_all['sex'] == 2:
      pare_info['sex'] = '1'
    if client_info_all['sex'] == 1:
      pare_info['bdate'] = int(client_info_all['bdate']) - 2
    elif client_info_all['sex'] == 2:
      pare_info['bdate'] = int(client_info_all['bdate']) + 2

    print(pare_info)

    self.search_id_url = self.url + 'users.search'
    self.search_id_params = {
      'count': 3,
      'sex': pare_info['sex'],
      'hometown': pare_info['city'],
      'status': pare_info['status'],
      'birth_year': pare_info['bdate']
    }
    req = requests.get(self.search_id_url, params={**self.params, **self.search_id_params}).json() 

    return req



if __name__ == "__main__":
   
  # Получение ТОКЕНА. Если нет прикрепленного файла, используем ручной ввод.
  with open('token_VK_group.txt', 'r') as file_object:
    token_VK_group = file_object.read().strip()

  # VK = VKinder_Bot()
  vk_group = vk_api.VkApi(token=token_VK_group)
  vk_session = vk_group.get_api()
  longpoll = VkLongPoll(vk_group)
  
  vk_client = VkUser(token_VK_group)
  
  id_client = 12415666

  client_info = vk_client.UsersInfo(id_client)
  pprint(client_info)

  client_info_all = vk_client.UsersInfo_all(client_info)
  pprint(client_info_all)

  pare_info = vk_client.search_pare(client_info_all)
  pprint(pare_info)




    # Создадим функцию для ответа на сообщения в лс группы
  def blasthack(id, text):
      vk_group.method('messages.send', {'user_id' : id, 'message' : text, 'random_id': 0})


#  # Слушаем longpoll(Сообщения)
#   for event in longpoll.listen():
#     if event.type == VkEventType.MESSAGE_NEW:

#       # Чтобы наш бот не слышал и не отвечал на самого себя
#       if event.to_me:

#         # Для того чтобы бот читал все с маленьких букв 
#         message = event.text.lower()

#         # Получаем id пользователя
#         id_client = event.user_id
#         ProfileInfo = vk_client.ProfileInfo(id_client)
#         # Структура переписки
#         if message == 'привет':
#           blasthack(id_client, 'Для подбора пары введите 1')

#         elif message == 'как дела?':
#           blasthack(id_client, 'Хорошо, а твои как?')

#         elif message == '1':
#           blasthack(id_client, id_client)

#         else:
#           blasthack(id_client, 'Я вас не понимаю! :(')









