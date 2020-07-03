from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup
import base64
import pytesseract
from PIL import Image
from parserImage import idenitfy_img
pytesseract.pytesseract.tesseract_cmd = r'.\Tesseract-OCR\tesseract.exe'

driver = webdriver.Chrome()
driver.set_window_size(1080,800)
driver.get('http://www.fnjtd.com/')

for i in range(1):
    account = 'yuenu'
    password = 'a123456'
    time.sleep(1)

    if driver.find_element_by_css_selector('footer>.ng-binding'):
        driver.find_element_by_css_selector('footer>.ng-binding').click()
    driver.find_element_by_id('login_account').send_keys(account)
    driver.find_element_by_id('login_password').send_keys(password)
    time.sleep(0.5)

    driver.find_element_by_css_selector('#login_code').click()
    time.sleep(1.5)

    soup = BeautifulSoup(driver.page_source,'lxml')
    imgstring = soup.select('#captcha')[0].get('ng-src')[22:]
    imgdata = base64.b64decode(imgstring)
    filepath = f'./recaptcha/captcha.png'
    with open(filepath, 'wb') as f:
        f.write(imgdata)
        

    driver.find_element_by_css_selector('#login_code').send_keys(idenitfy_img(filepath))
    driver.find_element_by_css_selector('#login-box').click()
    time.sleep(0.5)

    if driver.find_elements_by_css_selector('.btn-confirm'):
        for j in range(3):
            if driver.find_elements_by_css_selector('.btn-confirm'):
                driver.find_element_by_css_selector('.btn-confirm').click()
                driver.find_element_by_css_selector('#login_code').click()
                time.sleep(1.5)

                soup = BeautifulSoup(driver.page_source,'lxml')
                imgstring = soup.select('#captcha')[0].get('ng-src')[22:]

                imgdata = base64.b64decode(imgstring)
                filepath = f'./recaptcha/captcha.png'
                with open(filepath, 'wb') as f:
                    f.write(imgdata)

                # send captcha code
                driver.find_element_by_css_selector('#login_code').send_keys(idenitfy_img(filepath))
                driver.find_element_by_css_selector('#login-box').click()
    time.sleep(6.5)
    
    driver.find_element_by_css_selector('footer > .ng-binding').click()
    driver.get('http://www.fnjtd.com/SiteMail')
    


