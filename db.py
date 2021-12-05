import sqlalchemy
import psycopg2

# создаем engine
# db = f'postgresql://{user}:{password}@{host}:5432/{db_name}'

engine = sqlalchemy.create_engine(db)
connection = engine.connect()

try:
  connection = engine.connect()
  print('Подключились к PostgreSQL')
except Exception as error:
  print('Ошибка при работе с PostgreSQL', {error})

def insert_client(client_info):
  info = f"""INSERT INTO Client (ID_VK_Client, First_name, Last_name, Sex, City, Bdate, Status) VALUES(
    '{client_info.get('id_client')}', 
    '{client_info.get('first_name')}', 
    '{client_info.get('last_name')}', 
    '{client_info.get('sex')}',
    '{client_info.get('city')}',    
    '{client_info.get('bdate')}',
    '{client_info.get('status')}'
  );"""
  return connection.execute(info)

def insert_partner(partner_info):
  info = f"""INSERT INTO Client (ID_VK_Partner, Sex, City, Bday, Status) VALUES(
    '{partner_info.get('pare_id')}',
    '{partner_info.get('sex')}',
    '{partner_info.get('city')}',    
    '{partner_info.get('bdate')}',
    '{partner_info.get('status')}'
  );"""
  return connection.execute(info)

def insert_photo(Photo):
  info = f"""INSERT INTO Photo (id_Partner, url_photo) VALUES(
    '{Photo.get('pare_id')}',
    '{Photo.get('url_photo')}'
  );"""
  return connection.execute(info)

def insert_client_partner(dic):
  info = f"""INSERT INTO Client_Partner (id_Client, id_Partner) VALUES(
    '{dic['client_info']['id_client']}',
    '{dic['partner_info']['pare_id']}'
  );"""
  return connection.execute(info)
