import vk_api
from pprint import pprint
import time
import re
from pymongo import MongoClient
import pymongo
import pandas as pd
import json


log = (input("Введите логин: "))
pas = (input("Введите пароль: "))
age1 = (input("Укажите возраст от: "))
age1 = (input("Укажите возраст до: "))

named_tuple = time.localtime()
time_string = time.strftime("%Y", named_tuple)

client = MongoClient()
vkinder_bd = client['VKinder']
coll_in = vkinder_bd['Matches']

# print(client.drop_database('VKinder'))
# print(client.db.command("dropDatabase"))


class USER:

    def __init__(self):
        pass

# Формируем данные пользователя в словарь

    def main(self):
        login, password = log, pas
        self.vk_session = vk_api.VkApi(login, password)
        pattern = re.compile(r'\d+$')
        try:
            self.vk_session.auth(token_only=True)
        except vk_api.AuthError as error_msg:
            print(error_msg)
        vk = self.vk_session.get_api()
        response = vk.users.get(fields=['bdate', 'relation', 'sex', 'city'])

        for i in response:
            user_id = i['id']
            sex = i['sex']
            city = i['city']['id']
            relation = i['relation']
            bdate = str(i['bdate'])
            res = re.findall(pattern, bdate)
            for year in res:
                user_info = {'id': user_id, 'sex': sex, 'bdate': year,
                'city': city, 'relation': relation}
        return user_info

# Формируем данные для поиска жертвы

    def create_response(self):  # age_from, age_to
        search_parameters = {}
        user_info = self.main()
        if user_info['sex'] == 2:
            search_parameters['sex'] = 1
        else:
            search_parameters['sex'] = 2
        # if user_info['bdate']:
        #     get_year_from = int(time_string) - age_from
        #     get_year_to = int(time_string) - age_to
        #     search_parameters['age_from'] = get_year_from
        #     search_parameters['age_to'] = get_year_to
        if user_info['city']:
            search_parameters['city'] = user_info['city']
        # if user_info['relation']:
            search_parameters['relation'] = user_info['relation']

        return search_parameters

# Поиск жертвы c созданием JSON

    def user_search(self):
        s_p = self.create_response()
        vk = self.vk_session.get_api()
        user_list = []
        response = vk.users.search(sex=s_p['sex'], age_from=25, age_to=30,
        city=s_p['city'], status=s_p['relation'], has_photo=1,  fields=['common_count'])['items']
        for i in response:
            profile_photos = vk.photos.get(owner_id=i['id'], album_id='profile', extended=1,)['items']
            if profile_photos:
                df = pd.json_normalize(profile_photos).sort_values(by=['owner_id','comments.count'], ascending=False).head(3)
                df = df.take([3, 6, 12, 10], axis=1)
                result = df.to_json(orient="records")
                parsed = json.loads(result)
                for info in parsed:
                   if "sizes" in info:
                        sizes = info.get('sizes')[4]
                        for i in sizes:
                            url = sizes.get('url')
                        rec_info = {'owner_id':info ['owner_id'], 'url_photo':url, "likes":info['likes.count'], "comments":info['comments.count']}
                        user_list.append(rec_info)
        return user_list


    def get_json(self):
        with open('vkinder_users.json', 'w', encoding='utf-8') as fi:
            parsed = json.dump(self.user_search(), fi, indent=4)


    def send_to_the_db(self):
        result = coll_in.insert_many('vkinder_users.json')
        return result.inserted_ids


    def get_db(self):
        for  i in coll_in.find().sort("owner_id"):
            print(i)


person = USER()

# print(person.user_search())

# print(person.get_json())

# print(person.send_to_the_db())
# person.get_db()