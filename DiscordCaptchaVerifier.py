
import ast
import base64
import json
import os
import pickle
import random
import re
import ssl
import string
import time
import traceback

import instaloader

import capmonster_python
import cloudscraper
import requests
from python_rucaptcha.image_captcha import ImageCaptcha
from requests_html import HTMLSession
from playwright.sync_api import sync_playwright
from capmonster_python import ImageToTextTask

def random_user_agent():
    browser_list = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{0}.{1}.{2} Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_{2}_{3}) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{1}.{2}) Gecko/20100101 Firefox/{1}.{2}',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{0}.{1}.{2} Edge/{3}.{4}.{5}'
    ]

    chrome_version = random.randint(70, 108)
    firefox_version = random.randint(70, 108)
    safari_version = random.randint(605, 610)
    edge_version = random.randint(15, 99)

    chrome_build = random.randint(1000, 9999)
    firefox_build = random.randint(1, 100)
    safari_build = random.randint(1, 50)
    edge_build = random.randint(1000, 9999)

    browser_choice = random.choice(browser_list)
    user_agent = browser_choice.format(chrome_version, firefox_version, safari_version, edge_version, chrome_build, firefox_build, safari_build, edge_build)

    return user_agent

def generate_random_session_id(length=32):
    characters = string.ascii_letters + string.digits
    random_value = ''.join(random.choice(characters) for _ in range(length))
    return random_value

class Browser:
    def __init__(self, token, cap_key):

        self.cap_key = cap_key
        self.token = token

        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False)

        # Создание нового контекста
        self.context = self.browser.new_context()

        # Создание новой страницы
        self.page = self.context.new_page()

        # Переход на нужную страницу
        self.page.set_default_timeout(0)


    def goDiscordServer(self, link, waiting='🤖'):

        # time.sleep(10)
        self.page.goto(link)
        self.page.evaluate(f'''() => {{
                function login(token) {{
                    setInterval(() => {{
                        document.body.appendChild(document.createElement `iframe`).contentWindow.localStorage.token = `"${{token}}"`
                    }}, 50);
                    setTimeout(() => {{
                        location.reload();
                    }}, 2500);
                }}
                    login('{self.token}');
            }}''')
        self.page.goto(link)

        self.page.wait_for_timeout(5000)

        for i in range(3):
            # print(i, i)
            try:
                self.page.query_selector('button[class*="closeContainer"]').click()

            except:
                pass

            self.page.wait_for_timeout(2000)

        try:
            self.page.query_selector('button[class*="colorGreen"]').click()
        except:
            pass

        self.page.wait_for_timeout(2000)

        if waiting != None:

            if waiting == 'Verify':

                self.page.wait_for_selector('xpath=//div[contains(text(),"Verify")]')
                # print('Нажал')

            elif waiting == 'Green':
                pass

            else:
                self.page.wait_for_selector(f'[data-name="{waiting}"]')
        else:
            pass

    def AlongsideCaptcha(self, rucaptchaKey):

        # Ожидание определенного элемента

        element = self.page.wait_for_selector('[data-role="img"]')
        href = element.get_attribute('href')


        result = ImageCaptcha(rucaptcha_key=rucaptchaKey).captcha_handler(captcha_link=href)['captchaSolve']



        # self.page.wait_for_timeout(100000)

        # print(text)

        buttons = self.page.query_selector_all('[type="button"]')
        buttons[-1].click()

        self.page.wait_for_selector('[name="Answer"]')
        time.sleep(1)

        self.page.fill('input[name="Answer"]', result)
        time.sleep(1)
        self.page.query_selector('[type="submit"]').click()

        try:
            self.page.wait_for_selector('xpath=//strong[contains(text(),"Attempt")]', timeout=5000)
            self.page.reload()
            time.sleep(10)
            # self.page.wait_for_selector('[data-name="🤖"]')
            return 0

        except:

            self.browser.close()
            self.playwright.stop()
            return 1

    def VulcanCaptcha(self, rucaptchaKey):

        # Ожидание определенного элемента


        self.page.wait_for_selector('[class*="lookFilled"][aria-haspopup="listbox"]')

        element = self.page.query_selector_all('article [data-role="img"]')[-1]

        href = element.get_attribute('href')
        result = ImageCaptcha(rucaptcha_key=rucaptchaKey).captcha_handler(captcha_link=href)['captchaSolve']
        # print(result)

        button = self.page.query_selector('[class*="lookFilled"][aria-haspopup="listbox"]')
        button.click()

        self.page.wait_for_selector('div[id*="popout"] div[role="option"]')
        time.sleep(1)
        elements = self.page.query_selector_all('div[id*="popout"] div[role="option"]')

        for element in elements:

            try:
                if element.text_content().lower() == result.lower():
                    element.click()
                    self.browser.close()
                    self.playwright.stop()
                    return 1
                else:
                    pass
            except:

                pass

        self.browser.close()
        self.playwright.stop()
        return 0

    def Verifier(self, rucaptchaKey, attempts):

        # Ожидание определенного элемента
        
        button = self.page.wait_for_selector('xpath=//div[contains(text(),"Click here to answer")]')
        self.page.wait_for_timeout(3000)

        element = self.page.wait_for_selector('div[class*="ephemeral"] a[data-role="img"]')
        href = element.get_attribute('href')

        count = 0
        while count != attempts:

            result = ImageCaptcha(rucaptcha_key=rucaptchaKey).captcha_handler(captcha_link=href)['captchaSolve']

            button.click()

            self.page.wait_for_selector('input[class*="inputDefault"]').fill(result.upper())
            self.page.wait_for_selector('button[type="submit"]').click()

            self.page.wait_for_timeout(4000)

            try:
                self.page.wait_for_selector('xpath=//div[contains(text(),"Click here to answer")]', 3000)
                count+=1

            except:
                self.browser.close()
                self.playwright.stop()
                return 1

        return 0


    def PandezCaptcha(self, rucaptchaKey):

        # Ожидание определенного элемента

        self.page.wait_for_selector('xpath=//div[contains(text(),"Verify")]').click()
        self.page.wait_for_timeout(3000)

        element = self.page.wait_for_selector('xpath=//div[contains(text(),"Continue")]')
        element.click()
        self.page.wait_for_timeout(3000)

        element = self.page.wait_for_selector('xpath=//div[contains(text(),"Continue")]')
        element.click()

        self.page.wait_for_timeout(3000)

        try:
            element = self.page.wait_for_selector('div[class*="ephemeral"] button[class*="colorBrand"]', timeout=7000)
            # print(element.text_content())
            if element.text_content() == 'Enter Captcha':
                # print('Картинка')

                self.page.wait_for_timeout(3000)
                element = self.page.wait_for_selector('div[class*="ephemeral"] a[data-role="img"]')

                href = element.get_attribute('href')

                result = ImageCaptcha(rucaptcha_key=rucaptchaKey).captcha_handler(captcha_link=href)['captchaSolve']

                self.page.wait_for_selector('div[class*="ephemeral"] button[class*="colorBrand"]', timeout=7000).click()
                self.page.wait_for_timeout(1000)

                self.page.wait_for_selector('input[class*="inputDefault"]').fill(result)
                self.page.wait_for_selector('button[type="submit"]').click()

                try:
                    self.page.wait_for_selector('xpath=//div[text()="Try again"]', timeout=7000)
                    self.browser.close()
                    self.playwright.stop()
                    return 0
                except:
                    self.browser.close()
                    self.playwright.stop()
                    return 1

        except:

            # traceback.print_exc()
            #
            # print('калькулятор Картинка')

            try:
                self.page.query_selector('button[class*="colorRed"]')
                self.page.query_selector('button[class*="colorGreen"]')

                element = self.page.wait_for_selector('div[class*="ephemeral"] a[data-role="img"]')
                href = element.get_attribute('href')

                result = ImageCaptcha(rucaptcha_key=rucaptchaKey).captcha_handler(captcha_link=href)['captchaSolve']
                for letter in result:
                    for button in self.page.query_selector_all('div[class*="ephemeral"] > div[class*="container"] > div[class*="container"] > div[class*="container"] button'):
                        if button.text_content().rstrip() == letter:
                            button.click()
                            self.page.wait_for_timeout(2000)

                # self.page.query_selector('button[class*="colorGreen"]').click()

                self.page.wait_for_timeout(4000)

                try:
                    self.page.query_selector('button[class*="colorRed"]')
                    self.page.query_selector('button[class*="colorGreen"]')

                    self.browser.close()
                    self.playwright.stop()
                    return 0
                except:
                    self.browser.close()
                    self.playwright.stop()
                    return 1

            except:
                traceback.print_exc()
                ...

    def Sledgehammer(self):

        # Ожидание определенного элемента

        self.page.wait_for_selector('[class*="lookFilled"][aria-haspopup="listbox"]')

        keyWord = self.page.query_selector('div > em > u > strong').text_content().lower()


        button = self.page.query_selector('[class*="lookFilled"][aria-haspopup="listbox"]')
        button.click()

        self.page.wait_for_selector('div[id*="popout"] div[role="option"]')
        time.sleep(1)
        elements = self.page.query_selector_all('div[id*="popout"] div[role="option"]')

        for element in elements:

            try:

                if keyWord in element.get_attribute('data-list-item-id'):
                    element.click()
                    self.browser.close()
                    self.playwright.stop()
                    return 1
                else:
                    pass
            except:

                pass

        self.browser.close()
        self.playwright.stop()
        return 0

    def ChooseEmoji(self, message_id, emoji):

        # Ожидание определенного элемента

        self.page.wait_for_selector(f'[aria-describedby*="message-reactions-{message_id}"]')

        elements = self.page.query_selector_all(f'[aria-describedby*="message-reactions-{message_id}"] [data-type="emoji"]')

        for element in elements:

            try:
                # print(emoji, element.get_attribute('alt'))
                if emoji in element.get_attribute('alt'):
                    element.click()
                    self.browser.close()
                    self.playwright.stop()
                    return 1
                else:
                    pass
            except:

                pass

        self.browser.close()
        self.playwright.stop()
        return 0



class Discord:

    def __init__(self, token, proxy, cap_key):

        self.cap = capmonster_python.HCaptchaTask(cap_key)
        self.token = token
        self.proxy = proxy

        # print(token)
        # print(proxy)
        # print(cap_key)

        self.session = self._make_scraper()

        self.htmlSession = HTMLSession()
        self.htmlSession.mount('http://', self.session)
        self.htmlSession.mount('https://', self.session)

        self.ua = random_user_agent()
        self.session.user_agent = self.ua
        self.super_properties = self.build_xsp(self.ua)

        self.cfruid, self.dcfduid, self.sdcfduid = self.fetch_cookies(self.ua)
        self.fingerprint = self.get_fingerprint()
        self.sessionId = generate_random_session_id()

    def AcceptTerms(self, serverId, invite_code):

        self.session.headers = {'Host': 'discord.com', 'Connection': 'keep-alive',
                                'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
                                'X-Super-Properties': self.super_properties,
                                'Accept-Language': 'en-US', 'sec-ch-ua-mobile': '?0',
                                "User-Agent": self.ua,
                                'Content-Type': 'application/json', 'Authorization': self.token, 'Accept': '*/*',
                                'Origin': 'https://discord.com', 'Sec-Fetch-Site': 'same-origin',
                                'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Dest': 'empty',
                                'Referer': f'https://discord.com/channels/{guild_id}/{channel_id}',
                                'X-Debug-Options': 'bugReporterEnabled',
                                'Accept-Encoding': 'gzip, deflate, br',
                                'dnt': '1',
                                'x-fingerprint': self.fingerprint,
                                'x-discord-timezone': 'America/Maceio',
                                'Cookie': f'__dcfduid={self.dcfduid}; __sdcfduid={self.sdcfduid}; __cfruid={self.cfruid}; __cf_bm=DFyh.5fqTsl1JGyPo1ZFMdVTupwgqC18groNZfskp4Y-1672630835-0-Aci0Zz919JihARnJlA6o9q4m5rYoulDy/8BGsdwEUE843qD8gAm4OJsbBD5KKKLTRHhpV0QZybU0MrBBtEx369QIGGjwAEOHg0cLguk2EBkWM0YSTOqE63UXBiP0xqHGmRQ5uJ7hs8TO1Ylj2QlGscA='}

        with self.session.get(f'https://discord.com/api/v9/guilds/{serverId}/member-verification?with_guild=false&invite_code={invite_code}', timeout=10) as response:
            # print(response.json())
            data = response.json()

        payload = {'form_fields': data['form_fields'],
                   'version': data['version']}
        with self.session.put(f'https://discord.com/api/v9/guilds/{serverId}/requests/@me', json=payload, timeout=10) as response:
            # print(response.text)
            pass

    def SolveAlongsideCaptcha(self, guild_id, channel_id, message_id, rucaptchaKey, attempts):

        count = 0
        while count != attempts:

            self.browser = Browser(self.token, self.cap)
            self.browser.goDiscordServer(f'https://discord.com/channels/{guild_id}/{channel_id}')

            # self.fingerprint = self.get_fingerprint()
            self.session.headers = {'Host': 'discord.com', 'Connection': 'keep-alive',
                                    'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
                                    'X-Super-Properties': self.super_properties,
                                    'Accept-Language': 'en-US', 'sec-ch-ua-mobile': '?0',
                                    "User-Agent": self.ua,
                                    'Content-Type': 'application/json', 'Authorization': self.token, 'Accept': '*/*',
                                    'Origin': 'https://discord.com', 'Sec-Fetch-Site': 'same-origin',
                                    'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Dest': 'empty',
                                    'Referer': f'https://discord.com/channels/{guild_id}/{channel_id}',
                                    'X-Debug-Options': 'bugReporterEnabled',
                                    'Accept-Encoding': 'gzip, deflate, br',
                                    'dnt': '1',
                                    'x-fingerprint': self.fingerprint,
                                    'x-discord-timezone': 'America/Maceio',
                                    'Cookie': f'__dcfduid={self.dcfduid}; __sdcfduid={self.sdcfduid}; __cfruid={self.cfruid}; __cf_bm=DFyh.5fqTsl1JGyPo1ZFMdVTupwgqC18groNZfskp4Y-1672630835-0-Aci0Zz919JihARnJlA6o9q4m5rYoulDy/8BGsdwEUE843qD8gAm4OJsbBD5KKKLTRHhpV0QZybU0MrBBtEx369QIGGjwAEOHg0cLguk2EBkWM0YSTOqE63UXBiP0xqHGmRQ5uJ7hs8TO1Ylj2QlGscA='}

            while True:

                payload = {"type": 3,
                           "nonce": self.fingerprint.split(".")[0],
                           "guild_id": guild_id,
                           "channel_id": channel_id,
                           "message_flags": 0,
                           "message_id": message_id,
                           "application_id": "512333785338216465",
                           "session_id": self.sessionId,
                           "data": {"component_type": 2, "custom_id": "panel_verify"}}


                with self.session.post('https://discord.com/api/v9/interactions', json=payload, timeout=15) as response:
                    # print(response.text)
                    pass

                res = self.browser.AlongsideCaptcha(rucaptchaKey)

                if res:
                    return 'Alongside Done'
                else:
                    print('Ошибка')
                    break

            count+=1





    def VulcanCaptcha(self, guild_id, channel_id, message_id, rucaptchaKey, attempts):

        count = 0
        while count!=attempts:

            self.browser = Browser(self.token, self.cap)
            self.browser.goDiscordServer(f'https://discord.com/channels/{guild_id}/{channel_id}')

            # self.fingerprint = self.get_fingerprint()
            self.session.headers = {'Host': 'discord.com', 'Connection': 'keep-alive',
                                    'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
                                    'X-Super-Properties': self.super_properties,
                                    'Accept-Language': 'en-US', 'sec-ch-ua-mobile': '?0',
                                    "User-Agent": self.ua,
                                    'Content-Type': 'application/json', 'Authorization': self.token, 'Accept': '*/*',
                                    'Origin': 'https://discord.com', 'Sec-Fetch-Site': 'same-origin',
                                    'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Dest': 'empty',
                                    'Referer': f'https://discord.com/channels/{guild_id}/{channel_id}',
                                    'X-Debug-Options': 'bugReporterEnabled',
                                    'Accept-Encoding': 'gzip, deflate, br',
                                    'dnt': '1',
                                    'x-fingerprint': self.fingerprint,
                                    'x-discord-timezone': 'America/Maceio',
                                    'Cookie': f'__dcfduid={self.dcfduid}; __sdcfduid={self.sdcfduid}; __cfruid={self.cfruid}; __cf_bm=DFyh.5fqTsl1JGyPo1ZFMdVTupwgqC18groNZfskp4Y-1672630835-0-Aci0Zz919JihARnJlA6o9q4m5rYoulDy/8BGsdwEUE843qD8gAm4OJsbBD5KKKLTRHhpV0QZybU0MrBBtEx369QIGGjwAEOHg0cLguk2EBkWM0YSTOqE63UXBiP0xqHGmRQ5uJ7hs8TO1Ylj2QlGscA='}

            payload = {"type": 3,
                       "nonce": self.fingerprint.split(".")[0],
                       "guild_id": guild_id,
                       "channel_id": channel_id,
                       "message_flags": 0,
                       "message_id": message_id,
                       "application_id": "904575721429663785",
                       "session_id": self.sessionId,
                       "data": {"component_type": 2, "custom_id": "captcha-"}}

            with self.session.post('https://discord.com/api/v9/interactions', json=payload, timeout=15) as response:
                # print(response.text)
                pass

            res = self.browser.VulcanCaptcha(rucaptchaKey)

            if res:
                return 'Vulcan Done'
            else:
                # print('Неудача')
                count+=1

    def VerifierCaptcha(self, guild_id, channel_id, message_id, rucaptchaKey, attempts):



        self.browser = Browser(self.token, self.cap)
        self.browser.goDiscordServer(f'https://discord.com/channels/{guild_id}/{channel_id}', 'Green')

        # self.fingerprint = self.get_fingerprint()
        self.session.headers = {'Host': 'discord.com', 'Connection': 'keep-alive',
                                'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
                                'X-Super-Properties': self.super_properties,
                                'Accept-Language': 'en-US', 'sec-ch-ua-mobile': '?0',
                                "User-Agent": self.ua,
                                'Content-Type': 'application/json', 'Authorization': self.token, 'Accept': '*/*',
                                'Origin': 'https://discord.com', 'Sec-Fetch-Site': 'same-origin',
                                'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Dest': 'empty',
                                'Referer': f'https://discord.com/channels/{guild_id}/{channel_id}',
                                'X-Debug-Options': 'bugReporterEnabled',
                                'Accept-Encoding': 'gzip, deflate, br',
                                'dnt': '1',
                                'x-fingerprint': self.fingerprint,
                                'x-discord-timezone': 'America/Maceio',
                                'Cookie': f'__dcfduid={self.dcfduid}; __sdcfduid={self.sdcfduid}; __cfruid={self.cfruid}; __cf_bm=DFyh.5fqTsl1JGyPo1ZFMdVTupwgqC18groNZfskp4Y-1672630835-0-Aci0Zz919JihARnJlA6o9q4m5rYoulDy/8BGsdwEUE843qD8gAm4OJsbBD5KKKLTRHhpV0QZybU0MrBBtEx369QIGGjwAEOHg0cLguk2EBkWM0YSTOqE63UXBiP0xqHGmRQ5uJ7hs8TO1Ylj2QlGscA='}

        payload = {"type": 3,
                   "nonce": self.fingerprint.split(".")[0],
                   "guild_id": guild_id,
                   "channel_id": channel_id,
                   "message_flags": 0,
                   "message_id": message_id,
                   "application_id": "967155551211491438",
                   "session_id": self.sessionId,
                   "data": {"component_type": 2, "custom_id": "captcha-"}}

        with self.session.post('https://discord.com/api/v9/interactions', json=payload, timeout=15) as response:
            # print(response.text)
            pass

        res = self.browser.Verifier(rucaptchaKey, attempts)

        if res:
            return 'Verifier Done'
        else:
            return 'Капчу решить не удалось'

    def PandezCaptcha(self, guild_id, channel_id, message_id, rucaptchaKey, attempts):

        count = 0
        while count != attempts:

            self.browser = Browser(self.token, self.cap)
            self.browser.goDiscordServer(f'https://discord.com/channels/{guild_id}/{channel_id}', 'Verify')

            # self.fingerprint = self.get_fingerprint()
            self.session.headers = {'Host': 'discord.com', 'Connection': 'keep-alive',
                                    'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
                                    'X-Super-Properties': self.super_properties,
                                    'Accept-Language': 'en-US', 'sec-ch-ua-mobile': '?0',
                                    "User-Agent": self.ua,
                                    'Content-Type': 'application/json', 'Authorization': self.token, 'Accept': '*/*',
                                    'Origin': 'https://discord.com', 'Sec-Fetch-Site': 'same-origin',
                                    'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Dest': 'empty',
                                    'Referer': f'https://discord.com/channels/{guild_id}/{channel_id}',
                                    'X-Debug-Options': 'bugReporterEnabled',
                                    'Accept-Encoding': 'gzip, deflate, br',
                                    'dnt': '1',
                                    'x-fingerprint': self.fingerprint,
                                    'x-discord-timezone': 'America/Maceio',
                                    'Cookie': f'__dcfduid={self.dcfduid}; __sdcfduid={self.sdcfduid}; __cfruid={self.cfruid}; __cf_bm=DFyh.5fqTsl1JGyPo1ZFMdVTupwgqC18groNZfskp4Y-1672630835-0-Aci0Zz919JihARnJlA6o9q4m5rYoulDy/8BGsdwEUE843qD8gAm4OJsbBD5KKKLTRHhpV0QZybU0MrBBtEx369QIGGjwAEOHg0cLguk2EBkWM0YSTOqE63UXBiP0xqHGmRQ5uJ7hs8TO1Ylj2QlGscA='}

            payload = {"type": 3,
                       "nonce": self.fingerprint.split(".")[0],
                       "guild_id": guild_id,
                       "channel_id": channel_id,
                       "message_flags": 0,
                       "message_id": message_id,
                       "application_id": "967155551211491438",
                       "session_id": self.sessionId,
                       "data": {"component_type": 2, "custom_id": "captcha-"}}

            with self.session.post('https://discord.com/api/v9/interactions', json=payload, timeout=15) as response:
                # print(response.text)
                pass

            res = self.browser.PandezCaptcha(rucaptchaKey)

            if res:
                return 'Pandez Done'
            else:
                count += 1

    def Sledgehammer(self, guild_id, channel_id, message_id):

        self.browser = Browser(self.token, self.cap)
        self.browser.goDiscordServer(f'https://discord.com/channels/{guild_id}/{channel_id}')

        # self.fingerprint = self.get_fingerprint()
        self.session.headers = {'Host': 'discord.com', 'Connection': 'keep-alive',
                                'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
                                'X-Super-Properties': self.super_properties,
                                'Accept-Language': 'en-US', 'sec-ch-ua-mobile': '?0',
                                "User-Agent": self.ua,
                                'Content-Type': 'application/json', 'Authorization': self.token, 'Accept': '*/*',
                                'Origin': 'https://discord.com', 'Sec-Fetch-Site': 'same-origin',
                                'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Dest': 'empty',
                                'Referer': f'https://discord.com/channels/{guild_id}/{channel_id}',
                                'X-Debug-Options': 'bugReporterEnabled',
                                'Accept-Encoding': 'gzip, deflate, br',
                                'dnt': '1',
                                'x-fingerprint': self.fingerprint,
                                'x-discord-timezone': 'America/Maceio',
                                'Cookie': f'__dcfduid={self.dcfduid}; __sdcfduid={self.sdcfduid}; __cfruid={self.cfruid}; __cf_bm=DFyh.5fqTsl1JGyPo1ZFMdVTupwgqC18groNZfskp4Y-1672630835-0-Aci0Zz919JihARnJlA6o9q4m5rYoulDy/8BGsdwEUE843qD8gAm4OJsbBD5KKKLTRHhpV0QZybU0MrBBtEx369QIGGjwAEOHg0cLguk2EBkWM0YSTOqE63UXBiP0xqHGmRQ5uJ7hs8TO1Ylj2QlGscA='}

        payload = {"type": 3,
                   "nonce": self.fingerprint.split(".")[0],
                   "guild_id": guild_id,
                   "channel_id": channel_id,
                   "message_flags": 0,
                   "message_id": message_id,
                   "application_id": "863168632941969438",
                   "session_id": self.sessionId,
                   "data": {"component_type": 2, "custom_id": "startVerification.en"}}

        with self.session.post('https://discord.com/api/v9/interactions', json=payload, timeout=15) as response:
            # print(response.text)
            pass

        res = self.browser.Sledgehammer()

        if res:
            return 'Done'
        else:
            return 'Fail'

    def ChooseEmoji(self, guild_id, channel_id, message_id, emoji):

        self.browser = Browser(self.token, self.cap)
        self.browser.goDiscordServer(f'https://discord.com/channels/{guild_id}/{channel_id}', None)

        res = self.browser.ChooseEmoji(message_id, emoji)

        if res:
            return 'Done'
        else:
            return 'Fail'

    def ButtonClick(self, guild_id, channel_id, message_id, application_id, custom_id):

        # self.browser = Browser(self.token, self.cap)
        # self.browser.goDiscordServer(f'https://discord.com/channels/{guild_id}/{channel_id}')

        # self.fingerprint = self.get_fingerprint()
        self.session.headers = {'Host': 'discord.com', 'Connection': 'keep-alive',
                                'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
                                'X-Super-Properties': self.super_properties,
                                'Accept-Language': 'en-US', 'sec-ch-ua-mobile': '?0',
                                "User-Agent": self.ua,
                                'Content-Type': 'application/json', 'Authorization': self.token, 'Accept': '*/*',
                                'Origin': 'https://discord.com', 'Sec-Fetch-Site': 'same-origin',
                                'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Dest': 'empty',
                                'Referer': f'https://discord.com/channels/{guild_id}/{channel_id}',
                                'X-Debug-Options': 'bugReporterEnabled',
                                'Accept-Encoding': 'gzip, deflate, br',
                                'dnt': '1',
                                'x-fingerprint': self.fingerprint,
                                'x-discord-timezone': 'America/Maceio',
                                'Cookie': f'__dcfduid={self.dcfduid}; __sdcfduid={self.sdcfduid}; __cfruid={self.cfruid}; __cf_bm=DFyh.5fqTsl1JGyPo1ZFMdVTupwgqC18groNZfskp4Y-1672630835-0-Aci0Zz919JihARnJlA6o9q4m5rYoulDy/8BGsdwEUE843qD8gAm4OJsbBD5KKKLTRHhpV0QZybU0MrBBtEx369QIGGjwAEOHg0cLguk2EBkWM0YSTOqE63UXBiP0xqHGmRQ5uJ7hs8TO1Ylj2QlGscA='}

        payload = {"type": 3,
                   "nonce": self.fingerprint.split(".")[0],
                   "guild_id": guild_id,
                   "channel_id": channel_id,
                   "message_flags": 0,
                   "message_id": message_id,
                   "application_id": application_id,
                   "session_id": self.sessionId,
                   "data": {"component_type": 2, "custom_id": custom_id}}

        with self.session.post('https://discord.com/api/v9/interactions', json=payload, timeout=15) as response:
            # print(response.text)
            pass

        # res = self.browser.Sledgehammer()


        return 'Done'




    def JoinServer(self, invite):

        rer = self.session.post("https://discord.com/api/v9/invites/" + invite, headers={"authorization": self.token})

        # print(rer.text, rer.status_code)
        # print(rer.text)
        # print(rer.status_code)

        if "200" not in str(rer):
            site = "a9b5fb07-92ff-493f-86fe-352a2803b3df"
            tt = self.cap.create_task("https://discord.com/api/v9/invites/" + invite, site)
            # print(f"Created Captcha Task {tt}")
            captcha = self.cap.join_task_result(tt)
            captcha = captcha["gRecaptchaResponse"]
            # print(captcha)
            # print(f"[+] Solved Captcha ")
            # print(rer.text)

            self.session.headers = {'Host': 'discord.com', 'Connection': 'keep-alive',
                               'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
                               'X-Super-Properties': self.super_properties,
                               'Accept-Language': 'en-US', 'sec-ch-ua-mobile': '?0',
                               "User-Agent": self.ua,
                               'Content-Type': 'application/json', 'Authorization': 'undefined', 'Accept': '*/*',
                               'Origin': 'https://discord.com', 'Sec-Fetch-Site': 'same-origin',
                               'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Dest': 'empty',
                               'Referer': 'https://discord.com/@me', 'X-Debug-Options': 'bugReporterEnabled',
                               'Accept-Encoding': 'gzip, deflate, br',
                               'x-fingerprint': self.fingerprint,
                               'Cookie': f'__dcfduid={self.dcfduid}; __sdcfduid={self.sdcfduid}; __cfruid={self.cfruid}; __cf_bm=DFyh.5fqTsl1JGyPo1ZFMdVTupwgqC18groNZfskp4Y-1672630835-0-Aci0Zz919JihARnJlA6o9q4m5rYoulDy/8BGsdwEUE843qD8gAm4OJsbBD5KKKLTRHhpV0QZybU0MrBBtEx369QIGGjwAEOHg0cLguk2EBkWM0YSTOqE63UXBiP0xqHGmRQ5uJ7hs8TO1Ylj2QlGscA='}
            rej = self.session.post("https://discord.com/api/v9/invites/" + invite, headers={"authorization": self.token}, json={
                "captcha_key": captcha,
                "captcha_rqtoken": str(rer.json()["captcha_rqtoken"])
            })
            # print(rej.text())
            # print(rej.status_code)
            if "200" in str(rej):
                return 'Successfully Join 0'
            if "200" not in str(rej):
                return 'Failed Join'

        else:
            with self.session.post("https://discord.com/api/v9/invites/" + invite, headers={"authorization": self.token}) as response:
                # print(response.text)
                pass
            return 'Successfully Join 1'


    def _make_scraper(self):
        ssl_context = ssl.create_default_context()
        ssl_context.set_ciphers(
            "ECDH-RSA-NULL-SHA:ECDH-RSA-RC4-SHA:ECDH-RSA-DES-CBC3-SHA:ECDH-RSA-AES128-SHA:ECDH-RSA-AES256-SHA:"
            "ECDH-ECDSA-NULL-SHA:ECDH-ECDSA-RC4-SHA:ECDH-ECDSA-DES-CBC3-SHA:ECDH-ECDSA-AES128-SHA:"
            "ECDH-ECDSA-AES256-SHA:ECDHE-RSA-NULL-SHA:ECDHE-RSA-RC4-SHA:ECDHE-RSA-DES-CBC3-SHA:ECDHE-RSA-AES128-SHA:"
            "ECDHE-RSA-AES256-SHA:ECDHE-ECDSA-NULL-SHA:ECDHE-ECDSA-RC4-SHA:ECDHE-ECDSA-DES-CBC3-SHA:"
            "ECDHE-ECDSA-AES128-SHA:ECDHE-ECDSA-AES256-SHA:AECDH-NULL-SHA:AECDH-RC4-SHA:AECDH-DES-CBC3-SHA:"
            "AECDH-AES128-SHA:AECDH-AES256-SHA"
        )
        ssl_context.set_ecdh_curve("prime256v1")
        ssl_context.options |= (ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3 | ssl.OP_NO_TLSv1_3 | ssl.OP_NO_TLSv1)
        ssl_context.check_hostname = False

        return cloudscraper.create_scraper(
            debug=False,
            ssl_context=ssl_context
        )

    def build_xsp(self, ua):
        # ua = get_useragent()
        _,fv = self.get_version(ua)
        data = json.dumps({
            "os": "Windows",
            "browser": "Chrome",
            "device": "",
            "system_locale": "en-US",
            "browser_user_agent": ua,
            "browser_version": fv,
            "os_version": "10",
            "referrer": "",
            "referring_domain": "",
            "referrer_current": "",
            "referring_domain_current": "",
            "release_channel": "stable",
            "client_build_number": self.get_buildnumber(),
            "client_event_source": None
        }, separators=(",",":"))
        return base64.b64encode(data.encode()).decode()

    def get_version(self, user_agent):  # Just splits user agent
        chrome_version = user_agent.split("/")[3].split(".")[0]
        full_chrome_version = user_agent.split("/")[3].split(" ")[0]
        return chrome_version, full_chrome_version

    def get_buildnumber(self):  # Todo: make it permanently work
        r = requests.get('https://discord.com/app', headers={'User-Agent': 'Mozilla/5.0'})
        asset = re.findall(r'([a-zA-z0-9]+)\.js', r.text)[-2]
        assetFileRequest = requests.get(f'https://discord.com/assets/{asset}.js',
                                        headers={'User-Agent': 'Mozilla/5.0'}).text
        try:
            build_info_regex = re.compile('buildNumber:"[0-9]+"')
            build_info_strings = build_info_regex.findall(assetFileRequest)[0].replace(' ', '').split(',')
        except:
            # print("[-]: Failed to get build number")
            pass
        dbm = build_info_strings[0].split(':')[-1]
        return int(dbm.replace('"', ""))

    def fetch_cookies(self, ua):
        try:
            url = 'https://discord.com/'
            headers = {'user-agent': ua}
            response = self.session.get(url, headers=headers, proxies=self.proxy)
            cookies = response.cookies.get_dict()
            cfruid = cookies.get("__cfruid")
            dcfduid = cookies.get("__dcfduid")
            sdcfduid = cookies.get("__sdcfduid")
            return cfruid, dcfduid, sdcfduid
        except:
            # print(response.text)
            return 1

    def get_fingerprint(self):
        try:
            fingerprint = self.session.get('https://discord.com/api/v9/experiments', proxies=self.proxy).json()['fingerprint']
            # print(f"[=]: Fetched Fingerprint ({fingerprint[:15]}...)")
            return fingerprint
        except Exception as err:
            # print(err)
            return 1

if __name__ == '__main__':

    capKey = ''
    discordTokens = []
    proxies = []

    with open('FILEs/CaptchaKey.txt', 'r') as file:
        for i in file:
            capKey = i.rstrip()

    with open('FILEs/Discords.txt', 'r') as file:
        for i in file:
            discordTokens.append(i.rstrip())

    with open('FILEs/Proxies.txt', 'r') as file:
        for i in file:
            proxies.append(i.rstrip())


    invite_code = ''
    format = ''
    delay = 1
    attempts = 1

    with open('config', 'r') as file:
        for i in file:
            if 'InviteLink=' in i:
                invite_code = i.rstrip().split('=')[-1].split('/')[-1]
            elif 'CaptchaType=' in i:
                format = i.rstrip().split('=')[-1]
            elif 'Delay=' in i:
                delay = float(i.rstrip().split('=')[-1])
            elif 'Attempts=' in i:
                attempts = int(i.rstrip().split('=')[-1])



    if format == 'Alongside':
        rucaptchaKey = input('Вы выбрали решение Alongside капчи, для успешного решение требуется ключ от RuCaptcha, введите его: ').rstrip()
        data = input('Введите ID сервера, канала и сообщения от Alongside в следующем формате:\n'
                                                 '999999999999999999 8888888888888888888 777777777777777\n').rstrip().split(' ')
        guild_id, channel_id, message_id = data[0],data[1],data[2]

        for i in range(len(discordTokens)):
            try:
                acc = Discord(token=discordTokens[i],
                        proxy={
                            'http': f'http://{proxies[i].split(":")[2]}:{proxies[i].split(":")[3]}@{proxies[i].split(":")[0]}:{proxies[i].split(":")[1]}',
                            'https': f'http://{proxies[i].split(":")[2]}:{proxies[i].split(":")[3]}@{proxies[i].split(":")[0]}:{proxies[i].split(":")[1]}'},
                        cap_key=capKey)

                # print(1)
                print(f'{i+1} - Пытаюсь зайти на сервер')
                next = acc.JoinServer(invite_code)
                time.sleep(1)
                # print(2)

                try:
                    acc.AcceptTerms(guild_id, invite_code)
                    print(f'{i+1} - Соглашаюсь с условиями сервера')
                except:
                    traceback.print_exc()
                    pass

                # print(3)

                if 'Successfully' in next:
                    print(f'{i+1} - Успешно присоединился к серверу')
                    result = acc.SolveAlongsideCaptcha(guild_id,channel_id,message_id,rucaptchaKey,attempts)
                else:
                    result = 'Зайти на сервер не получиолсь'

                print(i + 1, f'- {result}\n')

            except Exception as e:
                # traceback.print_exc()
                print(i + 1, f'- {e}\n')

            time.sleep(delay)

    elif format == 'Vulcan':

        rucaptchaKey = input(
            'Вы выбрали решение Vulcan капчи, для успешного решение требуется ключ от RuCaptcha, введите его: ').rstrip()
        data = input('Введите ID сервера, канала и сообщения от Vulcan в следующем формате:\n'
                     '999999999999999999 8888888888888888888 777777777777777\n').rstrip().split(' ')
        guild_id, channel_id, message_id = data[0], data[1], data[2]

        for i in range(len(discordTokens)):
            try:
                acc = Discord(token=discordTokens[i],
                        proxy={
                            'http': f'http://{proxies[i].split(":")[2]}:{proxies[i].split(":")[3]}@{proxies[i].split(":")[0]}:{proxies[i].split(":")[1]}',
                            'https': f'http://{proxies[i].split(":")[2]}:{proxies[i].split(":")[3]}@{proxies[i].split(":")[0]}:{proxies[i].split(":")[1]}'},
                        cap_key=capKey)

                print(f'{i+1} - Пытаюсь зайти на сервер')
                next = acc.JoinServer(invite_code)
                time.sleep(1)

                try:
                    acc.AcceptTerms(guild_id, invite_code)
                    print(f'{i+1} - Соглашаюсь с условиями сервера')
                except:
                    pass

                if 'Successfully' in next:
                    print(f'{i+1} - Успешно присоединился к серверу')
                    result = acc.VulcanCaptcha(guild_id, channel_id, message_id, rucaptchaKey, attempts)
                else:
                    result = 'Зайти на сервер не получиолсь'

                print(i + 1, f'- {result}\n')

            except Exception as e:
                # traceback.print_exc()
                print(i + 1, f'- {e}\n')

            time.sleep(delay)

    elif format == 'Pandez':

        rucaptchaKey = input(
            'Вы выбрали решение Pandez капчи, для успешного решение требуется ключ от RuCaptcha, введите его: ').rstrip()
        data = input('Введите ID сервера, канала и сообщения от Pandez в следующем формате:\n'
                     '999999999999999999 8888888888888888888 777777777777777\n').rstrip().split(' ')
        guild_id, channel_id, message_id = data[0], data[1], data[2]

        for i in range(len(discordTokens)):
            try:
                acc = Discord(token=discordTokens[i],
                        proxy={
                            'http': f'http://{proxies[i].split(":")[2]}:{proxies[i].split(":")[3]}@{proxies[i].split(":")[0]}:{proxies[i].split(":")[1]}',
                            'https': f'http://{proxies[i].split(":")[2]}:{proxies[i].split(":")[3]}@{proxies[i].split(":")[0]}:{proxies[i].split(":")[1]}'},
                        cap_key=capKey)

                print(f'{i+1} - Пытаюсь зайти на сервер')
                next = acc.JoinServer(invite_code)
                time.sleep(1)

                try:
                    acc.AcceptTerms(guild_id, invite_code)
                    print(f'{i+1} - Соглашаюсь с условиями сервера')
                except:
                    pass

                if 'Successfully' in next:
                    print(f'{i+1} - Успешно присоединился к серверу')
                    result = acc.PandezCaptcha(guild_id, channel_id, message_id, rucaptchaKey, attempts)
                else:
                    result = 'Зайти на сервер не получиолсь'

                print(i + 1, f'- {result}\n')

            except Exception as e:
                # traceback.print_exc()
                print(i + 1, f'- {e}\n')

            time.sleep(delay)

    elif format == 'Verifier':

        rucaptchaKey = input(
            'Вы выбрали решение Verifier капчи, для успешного решение требуется ключ от RuCaptcha, введите его: ').rstrip()
        data = input('Введите ID сервера, канала и сообщения от Verifier в следующем формате:\n'
                     '999999999999999999 8888888888888888888 777777777777777\n').rstrip().split(' ')
        guild_id, channel_id, message_id = data[0], data[1], data[2]

        for i in range(len(discordTokens)):
            try:
                acc = Discord(token=discordTokens[i],
                        proxy={
                            'http': f'http://{proxies[i].split(":")[2]}:{proxies[i].split(":")[3]}@{proxies[i].split(":")[0]}:{proxies[i].split(":")[1]}',
                            'https': f'http://{proxies[i].split(":")[2]}:{proxies[i].split(":")[3]}@{proxies[i].split(":")[0]}:{proxies[i].split(":")[1]}'},
                        cap_key=capKey)

                print(f'{i+1} - Пытаюсь зайти на сервер')
                next = acc.JoinServer(invite_code)
                time.sleep(1)

                try:
                    acc.AcceptTerms(guild_id, invite_code)
                    print(f'{i+1} - Соглашаюсь с условиями сервера')
                except:
                    pass

                if 'Successfully' in next:
                    print(f'{i+1} - Успешно присоединился к серверу')
                    result = acc.VerifierCaptcha(guild_id, channel_id, message_id, rucaptchaKey, attempts)
                else:
                    result = 'Зайти на сервер не получиолсь'

                print(i + 1, f'- {result}\n')

            except Exception as e:
                # traceback.print_exc()
                print(i + 1, f'- {e}\n')

            time.sleep(delay)

    elif format == 'SledgeHammer':

        data = input('Введите ID сервера, канала и сообщения от SledgeHammer в следующем формате:\n'
                     '999999999999999999 8888888888888888888 777777777777777\n').rstrip().split(' ')
        guild_id, channel_id, message_id = data[0], data[1], data[2]

        for i in range(len(discordTokens)):
            try:
                acc = Discord(token=discordTokens[i],
                        proxy={
                            'http': f'http://{proxies[i].split(":")[2]}:{proxies[i].split(":")[3]}@{proxies[i].split(":")[0]}:{proxies[i].split(":")[1]}',
                            'https': f'http://{proxies[i].split(":")[2]}:{proxies[i].split(":")[3]}@{proxies[i].split(":")[0]}:{proxies[i].split(":")[1]}'},
                        cap_key=capKey)

                print(f'{i+1} - Пытаюсь зайти на сервер')
                next = acc.JoinServer(invite_code)
                time.sleep(1)

                try:
                    acc.AcceptTerms(guild_id, invite_code)
                    print(f'{i+1} - Соглашаюсь с условиями сервера')
                except:
                    pass

                if 'Successfully' in next:
                    print(f'{i+1} - Успешно присоединился к серверу')
                    result = acc.Sledgehammer(guild_id, channel_id, message_id)
                else:
                    result = 'Зайти на сервер не получиолсь'

                print(i + 1, f'- {result}\n')

            except Exception as e:
                # traceback.print_exc()
                print(i + 1, f'- {e}\n')

            time.sleep(delay)

    elif format == 'Choose Emoji':

        data = input('Введите ID сервера, канала, сообщения на котором нужно кликнуть на Emoji и требуемое Emoji в следующем формате:\n'
                     '999999999999999999 8888888888888888888 777777777777777 emoji\n').rstrip().split(' ')
        guild_id, channel_id, message_id, emoji = data[0], data[1], data[2], data[3]

        for i in range(len(discordTokens)):
            try:
                acc = Discord(token=discordTokens[i],
                        proxy={
                            'http': f'http://{proxies[i].split(":")[2]}:{proxies[i].split(":")[3]}@{proxies[i].split(":")[0]}:{proxies[i].split(":")[1]}',
                            'https': f'http://{proxies[i].split(":")[2]}:{proxies[i].split(":")[3]}@{proxies[i].split(":")[0]}:{proxies[i].split(":")[1]}'},
                        cap_key=capKey)

                print(f'{i+1} - Пытаюсь зайти на сервер')
                next = acc.JoinServer(invite_code)
                time.sleep(1)

                try:
                    acc.AcceptTerms(guild_id, invite_code)
                    print(f'{i+1} - Соглашаюсь с условиями сервера')
                except:
                    pass

                if 'Successfully' in next:
                    print(f'{i+1} - Успешно присоединился к серверу')
                    result = acc.ChooseEmoji(guild_id, channel_id, message_id, emoji)
                else:
                    result = 'Зайти на сервер не получиолсь'

                print(i + 1, f'- {result}\n')

            except Exception as e:
                # traceback.print_exc()
                print(i + 1, f'- {e}\n')

            time.sleep(delay)

    elif format == 'Click Button Classic':

        data = input('Введите ID сервера, канала, сообщения на кнопку которого нужно кликнуть, ID бота, который напечатал кнопку и custom_id из запроса при нажатии в следующем формате:\n'
                     '999999999999999999 8888888888888888888 777777777777777 66666666666666666 55555555555555\n').rstrip().split(' ')
        guild_id, channel_id, message_id, application_id, custom_id = data[0], data[1], data[2], data[3], data[4]

        for i in range(len(discordTokens)):
            try:
                acc = Discord(token=discordTokens[i],
                        proxy={
                            'http': f'http://{proxies[i].split(":")[2]}:{proxies[i].split(":")[3]}@{proxies[i].split(":")[0]}:{proxies[i].split(":")[1]}',
                            'https': f'http://{proxies[i].split(":")[2]}:{proxies[i].split(":")[3]}@{proxies[i].split(":")[0]}:{proxies[i].split(":")[1]}'},
                        cap_key=capKey)

                print(f'{i+1} - Пытаюсь зайти на сервер')
                next = acc.JoinServer(invite_code)
                time.sleep(1)

                try:
                    acc.AcceptTerms(guild_id, invite_code)
                    print(f'{i+1} - Соглашаюсь с условиями сервера')
                except:
                    pass

                if 'Successfully' in next:
                    print(f'{i+1} - Успешно присоединился к серверу')
                    result = acc.ButtonClick(guild_id, channel_id, message_id, application_id, custom_id)
                else:
                    result = 'Зайти на сервер не получиолсь'

                print(i + 1, f'- {result}\n')

            except Exception as e:

                # traceback.print_exc()
                print(i + 1, f'- {e}\n')

            time.sleep(delay)

    input('\n\nРабота скрипта окончена')
