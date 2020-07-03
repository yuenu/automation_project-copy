import time
import base64
import pytesseract
from PIL import Image
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from parserImage import idenitfy_img
pytesseract.pytesseract.tesseract_cmd = r'.\Tesseract-OCR\tesseract.exe'

driver = webdriver.Chrome()
driver.set_window_size(1080,800)
driver.get('http://www.fnjtd.com/')
account = 'yuenu'
password = 'a123456'
wait = WebDriverWait(driver, 20, 0.25)
filepath = f'./recaptcha/captcha.png'


def close_announcement():
	element = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="marquee"]/footer/span')))
	driver.execute_script("arguments[0].click();", element)

def send_user_login_info():
	driver.find_element_by_id('login_account').send_keys(account)
	driver.find_element_by_id('login_password').send_keys(password)

def parsing_the_page_source_and_decode_base64():
	driver.find_element_by_css_selector('#login_code').click()
	time.sleep(0.5)
	
	soup = BeautifulSoup(driver.page_source,'lxml')
	time.sleep(2)
	imgstring = soup.select('#captcha')[0].get('ng-src')[22:]
	imgdata = base64.b64decode(imgstring)
	return imgdata

def save_image(imgdata):
	with open(filepath, 'wb') as f:
		f.write(imgdata)
	
def click_login():
	driver.find_element_by_css_selector('#login-box').click()

def determine_captcha_code_satisfy_and_send__login_code():
	captcha_code = idenitfy_img(filepath)
	if len(captcha_code) == 4:
		driver.find_element_by_css_selector('#login_code').send_keys(captcha_code)
	else:
		print('The cpatcha_code < 4')
		driver.find_element_by_css_selector('#login_code').send_keys('0000')

def click_logout():
	element = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="action-box"]/a')))
	element.click()



for i in range(20):

	close_announcement()
	send_user_login_info()

	time.sleep(0.25)

	save_image(parsing_the_page_source_and_decode_base64())
	determine_captcha_code_satisfy_and_send__login_code()

	click_login()
	time.sleep(2)

	alert = driver.find_elements_by_xpath('//*[@id="ng-app"]/body/div[12]/div/div/div[3]/button[2]')
#	announcement = driver.find_elements_by_xpath('//*[@id="marquee"]/footer/span')

	if len(alert):
		for j in range(10):
			if len(alert):

				print(f'Error {j+1} times')
				element = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="ng-app"]/body/div[12]/div/div/div[3]/button[2]')))
				element.click()
				time.sleep(0.5)
				
				save_image(parsing_the_page_source_and_decode_base64())
				determine_captcha_code_satisfy_and_send__login_code()
				click_login()
				time.sleep(1.5)
			else:
				print('Out')
				break

	time.sleep(6)
	close_announcement()
	click_logout()

	print(f'complete {i+1} times  test!!')
	print('-------------------------')


print('Complete x times TEST!!')

