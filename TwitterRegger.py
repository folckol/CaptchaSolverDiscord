import os
import shutil
import threading
import time
import traceback
import urllib
from io import BytesIO

import requests
import json
import random
import string
import re
import imaplib
import email
import datetime

import tls_client
import ua_generator
from PIL import Image
from faker import Faker
from playwright.sync_api import sync_playwright

def MakeIMG():
    image_files = ['image1.png', 'image2.png', 'image3.png', 'image4.png', 'image5.png', 'image6.png']

    images = [Image.open(x) for x in image_files]

    # Проверка размеров картинок
    for img in images:
        if img.size != (200, 200):
            raise ValueError("All images must be of size 200x200")

    # Создание нового изображения с размером 1200x200
    result = Image.new('RGB', (1200, 400))

    # Вставка каждого изображения в результирующее изображение
    for index, img in enumerate(images):
        result.paste(img, (index * 200, 0))

    result.paste(Image.open('MainIMG.png'), (0, 200))
    # Сохранение результирующего изображения
    result.save('result.png')


def random_user_agent():
    browser_list = [
        'Mozilla/10.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{0}.{1}.{2} Edge/{3}.{4}.{5}'
    ]

    chrome_version = random.randint(90, 108)
    firefox_version = random.randint(90, 108)
    safari_version = random.randint(605, 610)
    edge_version = random.randint(15, 99)

    chrome_build = random.randint(1000, 9999)
    firefox_build = random.randint(1, 100)
    safari_build = random.randint(1, 50)
    edge_build = random.randint(1000, 9999)

    browser_choice = random.choice(browser_list)
    user_agent = browser_choice.format(chrome_version, firefox_version, edge_version, chrome_build, firefox_build, edge_build)

    return user_agent

def img(url):

    print('oo', url)


    time.sleep(10)

    playwright = sync_playwright().start()

    browser = playwright.chromium.launch(proxy={
        "server": "",
        "username": '',
        "password": '',
    }, headless=True, devtools=False)

    UA = random.choice(['Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 OPR/68.0.3618.125 (Edition Rambler)',
                        'Mozilla/5.0 (Windows NT 5.01) AppleWebKit/535.0 (KHTML, like Gecko) Chrome/90.0.4347.19 Safari/535.0 Edg/90.01032.88',
                        'Mozilla/5.0 (Windows; U; Windows NT 4.0) AppleWebKit/532.38.5 (KHTML, like Gecko) Version/4.0.1 Safari/532.38.5'])

    # print(random.uniform(-180, 180))
    context = browser.new_context(user_agent=UA,
                                            viewport={"width": random.randint(1000, 1920),
                                                      "height": random.randint(600, 900)},
                                            locale=random.choice(["en-US"]),
                                            timezone_id='Europe/Berlin'
                                            )

    context.set_extra_http_headers(headers={
        'Accept-Language': 'en-US;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'User-Agent': UA,
        'Sec-Ch-Ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Site': 'same-origin'
    })

    # self.context.set_offline(True)#кеширование
    page = context.new_page()

    page.goto(url)
    page.wait_for_selector('img').screenshot(path='Image.jpg')


    context.close()



class RegerModel:

    def __init__(self):
        playwright = sync_playwright().start()

        self.browser = playwright.chromium.launch(proxy={
            "server": "",
            "username": '',
            "password": '',
        },headless=False,devtools=True)

        UA = ua_generator.generate(device='desktop', browser='chrome').text
        # print(random.uniform(-180, 180))
        self.context = self.browser.new_context(user_agent=UA,
                                                viewport={"width": random.randint(1000, 1920), "height": random.randint(600, 900)},
                                                locale=random.choice(["en-US"]),
                                                timezone_id='Europe/Berlin'
                                                )

        self.context.set_extra_http_headers(headers={
            'Accept-Language': 'en-US;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'User-Agent': UA,
            'Sec-Ch-Ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Site': 'same-origin'
        })

        #self.context.set_offline(True)#кеширование
        self.page = self.context.new_page()

        self.page.set_default_timeout(45000)#базовое время ожидания выполнения
        self.url_public_key = "NO"

        #Перехват запросов со страницы для получения public_key
        def route_handler(route, request):
            # Сохраняем URL запроса
            self.url_public_key = request.url
            # Продолжаем выполнение запроса
            route.continue_()
        self.page.route(re.compile(r'.*public_key.*'), route_handler)

        self.link = ''
        login = ""
        password = ""
        # Открытие страницы Twitter
        #self.page.goto("https://twitter.com/i/flow/signup")
        self.page.goto("https://twitter.com/i/flow/signup?lang=en", timeout=25000, wait_until='domcontentloaded')
        self.page.wait_for_selector('xpath=//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[5]').click()
        self.page.get_by_label("Name0 / 50").click()
        fake = Faker()
        Name = fake.first_name_nonbinary()
        self.page.get_by_label("Name0 / 50").fill(str(Name))#указать имя
        self.page.get_by_label("Email").click()
        self.page.get_by_label("Email").fill(login)#указать почту
        Month = random.randint(1, 12)
        self.page.get_by_role("combobox", name="Month").select_option(str(Month))#выбрать месяц
        Day = random.randint(1, 28)
        self.page.get_by_role("combobox", name="Day").select_option(str(Day))#выбрать день
        Year = random.randint(1980, 2000)
        self.page.get_by_role("combobox", name="Year").select_option(str(Year))#выбрать год
        self.page.get_by_test_id("ocfSignupNextLink").click()
        self.page.get_by_test_id("ocfSettingsListNextButton").click()
        self.page.get_by_test_id("ocfSignupReviewNextLink").click()#после этого действия должна загрузиться капча
        self.page.wait_for_timeout(25000)#ожидание 25 сек

        # print(self.page.frames)
        self.frame = self.page.frames[-1]

        def handler(route, request):
            # получаем данные запроса
            print(f"intercepted request: {request.method} {request.url}")

            self.link = '3'

            route.continue_()

        self.frame.wait_for_selector('[data-theme="home.verifyButton"]').click()
        # self.frame.wait_for_timeout(10000)

        self.frame.page.route(re.compile(r'.*/rtig/image.*'), handler)

        while self.link == '':
            self.frame.wait_for_timeout(2)

        time.sleep(5)

        for i in range(6):

            print(i)

            self.box = self.frame.wait_for_selector('[aria-label*="Image"]')
            self.box.screenshot(path=f'image{i+1}.png')
            img = Image.open(f"image{i+1}.png")
            cropped_img = img.crop((0, 0, 200, 200))
            cropped_img.save(f"image{i+1}.png")

            self.frame.wait_for_selector('[aria-label="Navigate to next image"]').click()
            self.frame.wait_for_timeout(0.5)

        self.frame.wait_for_selector('[aria-labelledby="key-frame-text"]').screenshot(path='MainIMG.png')
        img = Image.open(f"MainIMG.png")
        cropped_img = img.crop((0, 0, 200, 200))
        cropped_img.save(f"MainIMG.png")

        MakeIMG()




        while not os.path.isfile('Image.jpg'):
            time.sleep(1)



        self.box = self.frame.wait_for_selector('[aria-label*="Image"]').bounding_box()
        time.sleep(3)




        moveMouse(40,40)






        # self.page.frames[-1].page.mouse.move(100, 100)

        # self.frame.query_selector('[data-theme="home.verifyButton"]').click()

        input('Стоп')


        ####################Капча####################
        self.public_key = self.url_public_key[52:88]
        headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
        }
        post_data_createTask = {
        "clientKey":"",
        "task":
            {
                "type":"FunCaptchaTaskProxyless",
                "websiteURL":"https://twitter.com/i/flow/signup",
                "websitePublicKey":self.public_key
            },
        "softId":0,
        "languagePool":"en"
        }


        print('Начали решать капчу')

        self.responseCREATE = requests.post("https://api.anti-captcha.com/createTask", json=post_data_createTask, headers=headers)
        self.responseCREATE_json = self.responseCREATE.text
        self.responseCREATE_dict = json.loads(self.responseCREATE_json)
        self.task_id = self.responseCREATE_dict['taskId']

        #создание запроса для получения токена
        post_data_getTaskResult = {
            "clientKey": "",
            "taskId": self.task_id
        }
        def getTaskResult():
            self.responseResult = requests.post("https://api.anti-captcha.com/getTaskResult", json=post_data_getTaskResult, headers=headers)
            self.responseResult_json = self.responseResult.text
            self.responseResult_dict = json.loads(self.responseResult_json)
            return self.responseResult_dict['status']

        while True:
            self.status = getTaskResult()
            if self.status == "processing":
                self.page.wait_for_timeout(10000)
            else:
                self.responseResult = requests.post("https://api.anti-captcha.com/getTaskResult", json=post_data_getTaskResult, headers=headers)
                self.responseResult_json = self.responseResult.text
                self.responseResult_dict = json.loads(self.responseResult_json)
                self.solution = self.responseResult_dict['solution']
                self.token = self.solution['token']
                break

        print('Капча решена')

        #self.page.evaluate(
        #    "() => { parent.postMessage(JSON.stringify({eventId:'challenge-complete',payload:{sessionToken:'" + self.token + "'}}),'*') }")
        #self.page.wait_for_timeout(10000)

        #captcha_token = str(self.token)
        #payload = {'eventId': 'challenge-complete', 'payload': {'sessionToken': captcha_token}}
        #script = "window.parent.postMessage(JSON.stringify(arguments[0]),'*')"
        #self.page.evaluate(script, payload)

        captcha_token = str(self.token)
        payload = {'eventId': 'challenge-complete', 'payload': {'sessionToken': captcha_token}}
        script = f"window.parent.postMessage(JSON.stringify({json.dumps(payload)}),'*')"
        self.page.evaluate(script)

        ## Получаем переменную captchaToken в Python
        #captcha_token = self.token
        ## Выполняем JavaScript-код в контексте страницы
        #self.page.evaluate(f"""() => {{
        #    parent.postMessage(JSON.stringify({{
        #        eventId: 'challenge-complete',
        #        payload: {{sessionToken: '{captcha_token}'}}
        #    }}), '*');
        #}}""")
        ####################Капча####################


        ####################Модуль получения сообщения###################
        def chech_message_twitter_rambler(login_imap, password_imap):
            imap_server = 'imap.rambler.ru'
            imap_port = 993
            # Параметры поиска сообщения
            search_from = 'info@twitter.com'
            today = datetime.date.today().strftime('%d-%b-%Y')

            # Подключение к почтовому ящику
            mail = imaplib.IMAP4_SSL(imap_server, imap_port)
            mail.login(login_imap, password_imap)
            mail.select('inbox')

            # Проверка наличия сообщения от указанного отправителя и даты
            def check_email():
                typ, messages = mail.search(None, f'(FROM "{search_from}")', f'(SENTON "{today}")')
                if messages[0]:
                    # Получение текста первого найденного письма
                    num = messages[0].split()[-1]
                    typ, data = mail.fetch(num, '(RFC822)')
                    message = email.message_from_bytes(data[0][1])
                    if message.is_multipart():
                        for part in message.walk():
                            content_type = part.get_content_type()
                            if content_type == 'text/plain':
                                text = part.get_payload(decode=True).decode()
                                # print('Найдено сообщение от', search_from, ':', text)
                                # print("!!!!!")
                                # print(text)
                                res = True
                                return res, text
                    else:
                        text = message.get_payload(decode=True).decode()
                        # print('Найдено сообщение от', search_from, ':', text)
                        # print("@@@@")
                        # print(text)
                        res = True
                        return res, text
                res = False
                text = "No"
                return res, text

            # Бесконечный цикл проверки новых сообщений
            count = 0
            while True and count < 5:
                res, text = check_email()
                if res == True:
                    break
                # Ожидание 20 сек перед следующей проверкой
                mail.noop()
                self.page.wait_for_timeout(20000)  #######
                print(count)
                count += 1

            if count >= 5:
                mail.close()
                mail.logout()
                return "NO"

            # Закрытие соединения с почтовым ящиком
            mail.close()
            mail.logout()
            return text
        ####################Модуль получения сообщения###################

        #получение текста с сообщением
        self.text_imap = chech_message_twitter_rambler(login, password)
        #парсинг кода из сообщения
        pattern = r"\b\d{6}\b"
        self.code_twitter_message_list = re.findall(pattern, self.text_imap)
        self.code_twitter_message = self.code_twitter_message_list[0]#код из сообщения
        #self.page.wait_for_timeout(220000)

        #использование кода
        self.page.get_by_label("Verification code").click()
        self.page.get_by_label("Verification code").fill(str(self.code_twitter_message))
        self.page.get_by_role("button", name="Next").click()
        # генерируем случайную строку из букв и цифр длиной 14 символов
        letters_and_digits = string.ascii_letters + string.digits
        Password = ''.join(random.choice(letters_and_digits) for i in range(14))
        self.page.get_by_label("Password", exact=True).fill(str(Password))
        self.page.get_by_test_id("LoginForm_Login_Button").click()
        #аккаунт зарегистрирован, скорее всего заблочен, требуется анлок
        self.page.wait_for_timeout(5000)
        self.state = self.context.storage_state()  # получение состояния хранилища
        with open('cookies.json', 'w') as f:  # сохраняем состояние хранилища в файл
            f.write(json.dumps(self.state))
        #####По заказу Квекса - всё#####





    def close(self):
        self.context.close()
        self.browser.close()

if __name__ == '__main__':
    try:
        RegerModel()
    except:
        traceback.print_exc()
        input('STOP')

