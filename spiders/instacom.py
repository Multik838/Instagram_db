import scrapy
import json
import re
from copy import deepcopy
from scrapy.http import HtmlResponse
from instaparser.items import InstaparserItem
from urllib.parse import urlencode


class InstacomSpider(scrapy.Spider):
    name = 'instacom'
    allowed_domains = ['instagram.com']
    start_urls = ['https://instagram.com/']
    # Здесь ссылка
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    # Здесь ссылка graphql
    inst_graphql_link = 'https://www.instagram.com/graphql/query/?'

    # Проба
    inst_followers_link = 'https://i.instagram.com/api/v1/friendships/'
    # Здесь наш логин
    inst_login = ""
    # Здесь наш пароль
    inst_pass = ''
    # Здесь указываем пользователя, которого парсим
    # parse_user = 'liveindrive777'
    parse_user = ['berberi_fm', 'liveindrive777', 'jeremyclarkson1']
    # parse_user3 = 'sergeistillavin'
    # Здесь указываем query_hash
    posts_hash = '02e14f6a7812a876f7d133c9555b1151'

# Здесь авторизация
    def parse(self, response: HtmlResponse):
        csrf = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.inst_login_link,
            method='POST',
            callback=self.login,
            formdata={'username': self.inst_login,
                      'enc_password': self.inst_pass},
            headers={'X-CSRFToken': csrf}
        )
        # В formdata необязательно указывать весь словарь, но при первой работе с сайтом важно учитывать каждый чих

# Здесь пользователи с которых берём данные
# Для реализации ипользовал цикл while для списка
# Т.е. здесь мы считываем кол-во пользователей и поочерёдно их поставляем в user_parse
    def login(self, response: HtmlResponse):
        global i
        j_body = response.json()
        parse_user = ['berberi_fm', 'liveindrive777', 'jeremyclarkson1']
        if j_body['authenticated']:
            i = 0
        while i <= len(parse_user):
            if i <= len(parse_user):
                yield response.follow(
                    f'/{self.parse_user[i]}',                                 # НЕ ЗАБУДЬ [i]
                    callback=self.user_parse,
                    cb_kwargs={'username': self.parse_user[i]}             # НЕ ЗАБУДЬ [i]
                )
                i = i + 1
            else:
                print('В списке всего', len(parse_user), 'пользователя(лей)')
                yield i

        # username
        # 'ai_machine_learning'
        # response.url
        # 'https://www.instagram.com/ai_machine_learning/'
        # https://www.instagram.com/berberi_fm/

        # Ошибка в исходном коде
        # Нужно из user_parse передать user_id и variables

# Здесь обрабатываем followers
    def subscribers_parse(self, response: HtmlResponse, username, user_id, variables):
        print()
        user_id = self.fetch_user_id(response.text, username)
        variables = {
            'id': user_id,
            'count': 12}
        url_followers = f"https://i.instagram.com/api/v1/friendships/{user_id}/followers/?{urlencode(variables)}"
        yield response.follow(
                            url_followers,
                            callback=self.subscribers_parse_next,
                            headers={'User-Agent': 'Instagram 64.0.0.14.96'},
                            cb_kwargs={'username': username,
                                       'user_id': user_id,
                                       'variables': deepcopy(variables)})

# Далее играем с max_id. Для эксперимента взял пользователя с количеством followers более 3 млн
    def subscribers_parse_next(self, response: HtmlResponse, username, user_id, variables):
        global max_id, item
        j_data = json.loads(response.text)
        users = j_data.get('users')
        max_id = j_data.get('next_max_id')      # Здесь получаем 1-ый max_id
        variables = {
            'id': user_id,
            'count': 12,
            'max_id': max_id}
        url_followers = f"https://i.instagram.com/api/v1/friendships/{user_id}/followers/?{urlencode(variables)}" #Здесь без max_id
        if max_id == 12:
            max_id += 12
            url_followers = f"https://i.instagram.com/api/v1/friendships/{user_id}/followers/?{max_id}{urlencode(variables)}"  # Подставляем max_id вот сюда
            variables = {
                'id': user_id,
                'count': 12,
                'max_id': max_id}
        elif max_id == None:
            max_id = 'QVFCTWlESjNjWGR4TVhYZ0tTLVJ3N2Q5OWVTb2J5VmNiT2NqdU02d2xBTkF2cWhjUmktR0pwVUV3MUJkZ1VlekRMN3N6dEoza0Z6S1VaaTczRjE0REpPdQ==' # 'jeremyclarkson1'(followers более 3 млн)
        else:
            print('That`s ALL')
        for user in users:
            item = InstaparserItem(
                                    parent_name=username,
                                    parent_id=user_id,
                                    user_id=user.get('pk'),
                                    name_followers=user.get('full_name'),
                                    photo_followers=user.get('profile_pic_url'))
            # Собрали followers
            yield item

            yield response.follow(
                            url_followers,
                            callback=self.following_parse,
                            headers={'User-Agent': 'Instagram 64.0.0.14.96'},
                            cb_kwargs={'username': username,
                                       'user_id': user_id,
                                       'variables': deepcopy(variables)}
            )

# Тут аналогично, только вместо followers собираем following
    def following_parse(self, response: HtmlResponse, username, user_id, variables):
        global max_id, item
        j_data = json.loads(response.text)
        users = j_data.get('users')
        max_id = j_data.get('next_max_id')
        variables = {
            'id': user_id,
            'count': 12,
            'max_id': max_id}
        url_followers = f"https://i.instagram.com/api/v1/friendships/{user_id}/following/?{urlencode(variables)}"
        if max_id == 12:
            max_id += 12
            url_followers = f"https://i.instagram.com/api/v1/friendships/{user_id}/following/?{max_id}{urlencode(variables)}"
            variables = {
                'id': user_id,
                'count': 12,
                'max_id': max_id}
        elif max_id == None:
            max_id = 'QVFCTWlESjNjWGR4TVhYZ0tTLVJ3N2Q5OWVTb2J5VmNiT2NqdU02d2xBTkF2cWhjUmktR0pwVUV3MUJkZ1VlekRMN3N6dEoza0Z6S1VaaTczRjE0REpPdQ=='
        else:
            print('That`s ALL')
        for user in users:
            item = InstaparserItem(
                                    parent_name=username,
                                    parent_id=user_id,
                                    user_id=user.get('pk'),
                                    name_following=user.get('full_name'),
                                    photo_following=user.get('profile_pic_url'))
            yield item

            yield response.follow(
                            url_followers,
                            callback=self.subscribers_parse_next,
                            headers={'User-Agent': 'Instagram 64.0.0.14.96'},
                            cb_kwargs={'username': username,
                                       'user_id': user_id,
                                       'variables': deepcopy(variables)}
            )

    def user_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        variables = {
            'id': user_id,
            'first': 12
        }

        url_posts = f'{self.inst_graphql_link}query_hash={self.posts_hash}&{urlencode(variables)}'

        yield response.follow(
                                url_posts,
                                callback=self.user_posts_parse,
                                cb_kwargs={'username': username,
                                           'user_id': user_id,
                                           'variables': deepcopy(variables)}
                            )

    # Так как user_post_parse является завершающим (На данный момент), то он ссылается через callback сам на себя.

    def user_posts_parse(self, response: HtmlResponse, username, user_id, variables):
        j_data = response.json()
        page_info = j_data.get('data').get('user').get('edge_owner_to_timeline_media').get('page_info')
        if page_info.get('has_next_page'):
            variables['after'] = page_info.get('end_cursor')

            url_posts = f'{self.inst_graphql_link}query_hash={self.posts_hash}&{urlencode(variables)}'

            yield response.follow(
                url_posts,
                callback=self.subscribers_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables)}
            )

        posts = j_data.get('data').get('user').get('edge_owner_to_timeline_media').get('edges')
        for post in posts:
            item = InstaparserItem(
                user_id=user_id,
                username=username,
                photo=post.get('node').get('display_url'),
                like=post.get('node').get('edge_media_preview_like').get('count'),
                post_data=post.get('node'))
            yield item

    # Получаем токен для авторизации
    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    # Получаем id желаемого пользователя
    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')
# Далее все данные пишутся в items
