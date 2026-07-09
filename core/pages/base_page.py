"""Базовый класс страницы для паттерна Page Object.

WebPage — обёртка над Selenium WebDriver, предоставляющая методы
навигации, скроллинга, работы с iframe/cookie/окнами и ожидания
полной загрузки страницы.
"""

import time
import requests

from termcolor import colored
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class WebPage(object):
    """Базовая страница с WebDriver и методами навигации.

    Атрибуты WebElement/ManyWebElements автоматически привязываются
    к драйверу при обращении через __getattribute__.
    """

    _web_driver = None

    def __init__(self, web_driver, url=''):
        self._web_driver = web_driver
        self.get(url)

    def __setattr__(self, name, value):
        if not name.startswith('_'):
            self.__getattribute__(name)._set_value(self._web_driver, value)
        else:
            super(WebPage, self).__setattr__(name, value)

    def __getattribute__(self, item):
        attr = object.__getattribute__(self, item)

        if not item.startswith('_') and not callable(attr):
            attr._web_driver = self._web_driver
            attr._page = self

        return attr

    def get(self, url):
        self._web_driver.get(url)
        self.wait_page_loaded()

    def go_back(self):
        self._web_driver.back()
        self.wait_page_loaded()

    def refresh(self):
        self._web_driver.refresh()
        self.wait_page_loaded()

    def screenshot(self, file_name='screenshot.png'):
        self._web_driver.save_screenshot(file_name)

    def scroll_down(self, offset=0):
        """ Прокрутите страницу вниз. """

        if offset:
            self._web_driver.execute_script(
                'window.scrollTo(0, {0});'.format(offset)
            )
        else:
            self._web_driver.execute_script(
                'window.scrollTo(0, document.body.scrollHeight);'
            )

    def scroll_up(self, offset=0):
        """ Прокрутить страницу вверх. """

        if offset:
            self._web_driver.execute_script(
                'window.scrollTo(0, -{0});'.format(offset)
            )
        else:
            self._web_driver.execute_script(
                'window.scrollTo(0, -document.body.scrollHeight);'
            )

    def switch_to_iframe(self, iframe):
        """ Переключитесь на iframe по его имени. """
        self._web_driver.switch_to.frame(iframe)

    def get_cookies(self):
        """ Этот метод выводит все доступные файлы cookie
        для текущей сессии. """
        return self._web_driver.get_cookies()

    def add_cookie(self, name, value):
        """ Этот метод помогает настроить файл cookie для сессии. """
        return self._web_driver.add_cookie(name=name, value=value)

    def switch_to_alert_accept(self):
        """ Deprecated use switch_to_alert. """
        self._web_driver.switch_to.alert.accept()

    def switch_to_window(self, window=0):
        """ Переключитесь на вкладку по его индексу. """
        self._web_driver.switch_to.window(
            self._web_driver.window_handles[window]
        )

    def switch_out_iframe(self):
        """ Отменить фокус iframe. """
        self._web_driver.switch_to.default_content()

    def validate_html(self, url):
        """Функция для проверки валидации HTML страницы"""
        validator_url = 'https://validator.w3.org/nu/?out=json'
        headers = {'Content-Type': 'text/html; charset=utf-8'}
        data = requests.get(url).text
        response = requests.post(
            validator_url, headers=headers,
            data=data.encode('utf-8')
        )
        results = response.json()
        return results

    def get_current_url(self):
        """ Возвращает URL текущего браузера. """
        return self._web_driver.current_url

    def execute_script(self, script):
        """ Возвращает JS скрипт. """
        return self._web_driver.execute_script(script)

    def get_page_source(self):
        """ Возвращает тело текущей страницы. """

        source = ''
        try:
            source = self._web_driver.page_source
        except Exception:
            print(colored('Can not get page source', 'red'))

        return source

    def check_js_errors(self, ignore_list=None):
        """ Эта функция проверяет ошибки JS на странице. """

        ignore_list = ignore_list or []

        logs = self._web_driver.get_log('browser')
        for log_message in logs:
            if log_message['level'] != 'WARNING':
                ignore = False
                for issue in ignore_list:
                    if issue in log_message['message']:
                        ignore = True
                        break

                assert ignore, (
                    'JS error "{0}" on the page!'
                    .format(log_message)
                )

    def wait_page_loaded(self, timeout=10, check_js_complete=True,
                         check_page_changes=False, check_images=False,
                         wait_for_element=None,
                         wait_for_xpath_to_disappear='',
                         sleep_time=0):
        """ Ждём загрузки страницы через readyState. """
        try:
            WebDriverWait(self._web_driver, timeout).until(
                lambda d: d.execute_script(
                    "return document.readyState"
                ) == "complete"
            )
        except Exception:
            pass
        time.sleep(0.2)
