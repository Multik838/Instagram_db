from pymongo import MongoClient
from pprint import pprint

client = MongoClient('localhost', 27017)
db = client['instagram_SUPER']
users = db.instagram

name = input('Укажите имя пользователя: ')
cnt = users.count_documents({'$and': [{'name_followers': name_followers}]})
print(f'Подписчики {cnt}:')
for user in users.find({'$and': [{'source_name': name_followers}]}):
    pprint(user)
print('_____________________________________')
cnt = users.count_documents({'$and': [{'name_following': name_following}]})
print(f'Подписки {cnt}:')
for user in users.find({'$and': [{'name_following': name_following}]}):
    pprint(user)