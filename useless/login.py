from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import base64
import pytesseract
from PIL import Image
from bs4 import BeautifulSoup
from parserImage import idenitfy_img

pytesseract.pytesseract.tesseract_cmd = r'.\Tesseract-OCR\tesseract.exe'

driver = webdriver.Chrome()
driver.set_window_size(1080,800)
driver.get('http://www.fnjtd.com/')
account = 'yuenu'
password = 'a123456'
wait = WebDriverWait(driver, 20, 0.25)

for i in range(100):    
    # Check the tag is ckickable,and close the announcement
    element = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="marquee"]/footer/span')))
    driver.execute_script("arguments[0].click();", element)
    
    # Input the account & password 
    driver.find_element_by_id('login_account').send_keys(account)
    driver.find_element_by_id('login_password').send_keys(password)
    time.sleep(0.5)

    # Calculate which "click the button -> get image -> idenitfy img ->input code" times
    starttime = time.time()

    # click login code button
    driver.find_element_by_css_selector('#login_code').click()  

    # Reserve 1.5s to get page_source, if not enough , everytime plus 0.1s until "#captcha" 
    # on page_source 
    time.sleep(1.5)
    soup = BeautifulSoup(driver.page_source,'lxml')
    for x in range(20):
        if driver.find_elements_by_id('captcha'):
            break
        else:
            sleeptime = sleeptime + 0.1
   
    # Get what we need the image url ,use base64 module to catch binary code 
    imgstring = soup.select('#captcha')[0].get('ng-src')[22:]
    imgdata = base64.b64decode(imgstring)

    # Save the image to local 
    filepath = f'./recaptcha/captcha.png'
    with open(filepath, 'wb') as f:
        f.write(imgdata)


    # Idenitfy the image and send in -> click the login button
    captcha_code = idenitfy_img(filepath)

    if len(captcha_code) == 4:
        driver.find_element_by_css_selector('#login_code').send_keys(captcha_code)
    else:
        print('The cpatcha_code < 4')
        driver.find_element_by_css_selector('#login_code').send_keys('0000')
    driver.find_element_by_css_selector('#login-box').click()

    # Collect what we need data and printout
    endtime = time.time()
    print (f'The {i+1} times cost time:' ,endtime - starttime )
    time.sleep(0.5)

    # check out if not the send_code is correct answer 
    if len(driver.find_elements_by_xpath('//*[@id="ng-app"]/body/div[12]/div/div/div[3]/button[2]')):
        for j in range(10):
            if len(driver.find_elements_by_xpath('//*[@id="ng-app"]/body/div[12]/div/div/div[3]/button[2]')):

                print(f'The {j+1} times to get error captcha')

                element = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="ng-app"]/body/div[12]/div/div/div[3]/button[2]')))
                element.click()

                time.sleep(0.25)
                starttime = time.time()
                driver.find_element_by_css_selector('#login_code').click()
                time.sleep(1.5)

                soup = BeautifulSoup(driver.page_source,'lxml')

                try:
                    for po in range(20):
                        if driver.find_elements_by_id('captcha'):
                            break
                        else:
                            sleeptime = sleeptime + 0.1
                except:
                    print('The break po:',po)


                imgstring = soup.select('#captcha')[0].get('ng-src')[22:]
                imgdata = base64.b64decode(imgstring)
                filepath = f'./recaptcha/captcha.png'
                with open(filepath, 'wb') as f:
                    f.write(imgdata)

                # Idenitfy the image and send in -> click the login button
                captcha_code = idenitfy_img(filepath)

                if len(captcha_code) == 4:
                    driver.find_element_by_css_selector('#login_code').send_keys(captcha_code)
                else:
                    print('The captcha_code < 4')
                    driver.find_element_by_css_selector('#login_code').send_keys('0000')
                driver.find_element_by_css_selector('#login-box').click()



                endtime = time.time()
                print (f'Error {j+1} times in cost time:' ,endtime - starttime)

                time.sleep(1.5)

    time.sleep(6)

    element = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="marquee"]/footer/span')))
    driver.execute_script("arguments[0].click();", element)
    driver.implicitly_wait(2)
    driver.find_element_by_css_selector('.logout-btn').click()
    

    print(f'complete {i+1} times  test!!')
    print('-------------------------')
print('complete all test!!.congratulations')
    


