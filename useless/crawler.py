from selenium import webdriver
import time
driver = webdriver.Chrome()
driver.set_window_size(1080,800)
driver.get('http://www.fnjtd.com/Partner')
from bs4 import BeautifulSoup
soup = BeautifulSoup(driver.page_source,'lxml')
time.sleep(3)
# 點擊"代理註冊"
driver.find_element_by_css_selector('.mtab-menual > li:nth-child(4)').click()
time.sleep(2)

for i in range(10000):
	driver.find_element_by_css_selector('#checkcode-input-group>input').click()  
	time.sleep(0.5)
	soup2 = BeautifulSoup(driver.page_source,'lxml')
	time.sleep(2)
	# To get CAPTCHA Image URL
	imgstring = soup2.select('.input-group-addon img')[0].get('ng-src')[22:]
	import base64
	# Decode base64code
	imgdata = base64.b64decode(imgstring)
	filename = f'../../Juypter notebook/captcha3/{i+16594}.png'
	with open(filename, 'wb') as f:
		f.write(imgdata)