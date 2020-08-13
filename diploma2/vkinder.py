import vk_api
from pprint import pprint
import time
import re
from pymongo import MongoClient
import pandas as pd
import json
import random


client = MongoClient()
vkinder_bd = client['VKinder']
coll_in = vkinder_bd['Matches']

# print(client.drop_database('VKinder'))  # удаление базы


class USER:

    def __init__(self):
        pass

# Формируем данные пользователя в словарь

    def main(self):
        log = (input("Введите логин: "))
        pas = (input("Введите пароль: "))
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

    def create_response(self):
        search_parameters = {}
        user_info = self.main()
        if user_info['sex'] == 2:
            search_parameters['sex'] = 1
        else:
            search_parameters['sex'] = 2
        if user_info['city']:
            search_parameters['city'] = user_info['city']
            search_parameters['relation'] = user_info['relation']

        return search_parameters

# Поиск жертвы c созданием JSON

    def user_search(self):
        age1 = (input("Укажите возраст от: "))
        age2 = (input("Укажите возраст до: "))
        s_p = self.create_response()
        vk = self.vk_session.get_api()
        user_list = []
        response = vk.users.search(sex=s_p['sex'], age_from=age1, age_to=age2,
            city=s_p['city'], status=s_p['relation'], has_photo=1,
            fields=['common_count'], count=100)['items']

        for i in response:
            if i['is_closed'] is False:
                profile_info = {
                    "user_id": i['id'],
                    "first_name": i['first_name'],
                    "last_name": i['last_name'],
                    "link": "https://vk.com/id{}".format(i['id']),
                    "photo": ''
                        }
                profile_photos = vk.photos.get(owner_id=i['id'], album_id='profile', extended=1,)['items']
                if profile_photos:
                    df = pd.json_normalize(profile_photos).sort_values(by=['likes.count', 'comments.count'], ascending=False).head(3)
                    result = df.to_json(orient="records")
                    parsed = json.loads(result)
                    df = pd.DataFrame(parsed)
                    df1 = df[['owner_id', 'sizes']].to_json(orient="records")
                    parsed1 = json.loads(df1)
                    photo_links_list = []
                    for info in parsed1:
                        if "sizes" in info:
                            sizes = info.get('sizes')
                            if len(sizes):
                                need_size = sizes[len(sizes)-1]['url']
                        photo_links_list.append(need_size)
                profile_info["photo"] = photo_links_list
                user_list.append(profile_info)

        return user_list

    def get_json(self):
        user_frame = pd.DataFrame(self.user_search()).to_json(orient="records")
        parsed = json.loads(user_frame)
        with open('vkinder_users.json', 'w',  encoding="utf-8") as fi:
            for chunk in json.JSONEncoder(ensure_ascii=False, indent=4).iterencode(parsed):
                fi.write(chunk)

    def send_to_the_db(self):
        with open('vkinder_users.json', encoding="utf-8") as fo:
            data = json.load(fo)
            result = coll_in.insert_many(data)
            return result.inserted_ids

    def get_10th_users_list(self):
        top_list = []
        while len(top_list) < 10:
            for document in coll_in.find().skip(random.randint(0, 90)).limit(10):
                document['_id'] = str(document['_id'])
                top_list.append(document)
            with open('vkinder_users.json') as fo:
                data = json.load(fo)
            for chunk in top_list:
                if chunk in data:
                    top_list.remove(chunk)
        with open('vkinder_users.json', 'w+',  encoding="utf-8") as fi:
            for chunk in json.JSONEncoder(ensure_ascii=False, indent=4).iterencode(top_list[:10]):
                fi.write(chunk)

        return top_list


if __name__ == "__main__":

    person = USER()

    pprint(person.get_10th_users_list())
