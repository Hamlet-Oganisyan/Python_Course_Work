import requests     # Импортируем библиотеку для работы с запросами Vk
from pprint import pprint # Импортируем библиотеку для более красивовго вывода на печать
import time         # Импортируем библиотеку для установления задержки времени
from tqdm import tqdm   # Импортируем библиотеку для отображения прогресс-бара
import json         # Импортируем библиотеку для работы с json-файлами 
from progress.bar import PixelBar # Импортируем библиотеку для отображения прогресса загрузки

vk_token = 'a67f00c673c3d4b12800dd0ba29579ec56d804f3c5f3bbcef5328d4b3981fa5987b951cf2c8d8b24b9abd' # Токен VK
version = '5.131' 

with open('D:/Netology/YaDisk_token.txt', 'r') as file: # Получим токен яндекса из файла
    yandex_token = file.read().strip()

class VkDownloader: # Создаем класс для работы с VK API
  
    url = 'https://api.vk.com/method/'
    
    def __init__(self, token, version):
        self.params = {
            'access_token': token,
            'v': version     
        }

    def get_photos(self, vk_id): # Пишем медот получения фото из Вк
        photos_get_url = self.url + 'photos.get'
        
        # Укажем параметры для получения         
        params = { 
            'owner_id': vk_id,     # идентификатор владельца альбома
            'album_id': 'profile', # устанавливаем параметр вывода фото , как фотографии профиля
            'extended': 1,         # получаем дополнительные поля likes и др. для их дальнейшего спользования 
            'photo_sizes': 0,      # получаем доступные размеры фотографии для дальнейшего выбора из них Мах значения
            'count': 5             # устанвливаем лимит получаемых записей
        }
        req = requests.get(photos_get_url, params={**self.params, **params}).json()
        res = req['response']['items'] 
        
        new_res = [] # создаем новый список с отфильтрованными данными
        for x in res:
            for k, v in x.items():
                if k == 'sizes':
                    x['sizes'] = v[-1] # из всех предоставляемых размеров фото выбираем самое большое расширение
            new_res.append(x) 
        self.json_to_save = []# Создаем список с информацией по фото 
        names = []  # Создадим список имен файлов
        file_information = [] # создаем список информации по файлам
        for x in new_res: #
            file_name = x['likes']['count']# создаем переменную имени файла равной количеству лайков фото
            if file_name not in names:
                names.append(file_name) # помещаем в список имя файла
            else:
                file_name = '_'.join([str(x['likes']['count']), str(x['date'])])
                names.append(file_name)
            # Заполняем список с инфой по файлам
            file_information.append({'file_name': f'{file_name}.jpg', "size": x['sizes']['type']})
            # Создаем файл-json с инфой по файлам в требуемом формате "file_name":  "size":
            with open('D:/Netology/Course_work/file_information.txt', 'w') as outfile:
                json.dump(file_information, outfile)
            
            self.json_to_save.append(({'file_name': f'{file_name}.jpg', "size": x['sizes']['type'], "url": x['sizes']['url']} ))
        
        # Создаем файл-json с фото для их дальнейшей загрузки на ЯндексДиск        
        for file in self.json_to_save:
            file_name = file.get('file_name')
            url = file.get('url')
            images = requests.get(url)
        with open('D:/Netology/Course_work/data.json', 'w') as write_file:
            json.dump(self.json_to_save, write_file, indent=4)
        
class YaUploader(VkDownloader): # Создаем класс для работы с Yandex Disk API
    host = r'https://cloud-api.yandex.net'
    
    def __init__(self, token: str):
        self.token = yandex_token

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': f'OAuth {self.token}'
        }

    def create_folder(self): # Создаем метод создания папки в ЯндексДиск, куда будут сохраняться фото
        host = self.host
        self.path = f'/Course_work'
        url = f"{host}/v1/disk/resources"
        headers = self.get_headers()
        params = {'path': self.path}
        response = requests.put(url, headers=headers, params=params)
        response.raise_for_status()
        print()
        if response.status_code == 201:
            print('Папка "Course_work" успешно создана на Яндекс Диск')
        else:
            return {'code': response.status_code, 'text': response.text} 
        
    def upload_file(self): 
        host = self.host
        self.create_folder()
        with open('D:/Netology/Course_work/data.json') as f:
            data = json.load(f)
            print()
            print('Идет загрузка фото на ЯндексДиск: ')
            print()
            for i in data:
                file_name = i.get('file_name')
                link = i.get('url')
                path = f'{host}/v1/disk/resources/upload'
                disc_path = f'/Course_work/{file_name}'
                headers = self.get_headers()
                params = {'path': disc_path, 'url': link}
                response = requests.post(url=path, headers=headers, params=params)
                bar = PixelBar(max=100)
                for i in range(100):
                    time.sleep(0.01)# Ставим задержку по времени
                    bar.next()
                if response.status_code == 202:
                    print(f'  Фото {file_name} успешно загружено')

                else:
                    return {'code': response.status_code, 'text': response.text} 
                
if __name__ == '__main__':
    downloader = VkDownloader(vk_token, version)
    downloader.get_photos(552934290)
    uploader = YaUploader(yandex_token)  
    result = uploader.upload_file()