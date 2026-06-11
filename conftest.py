import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import allure


@pytest.fixture
def driver():
    chrome_options = Options()
    chrome_options.add_argument('--start-maximized')
    # chrome_options.add_argument('--headless')

    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)

    yield driver
    driver.quit()
