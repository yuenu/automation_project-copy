import time
import base64
import pytesseract
from bs4 import BeautifulSoup
from parserImage import idenitfy_img
from PIL import UnidentifiedImageError
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementNotInteractableException, NoSuchElementException, UnexpectedAlertPresentException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

pytesseract.pytesseract.tesseract_cmd = r'.\Tesseract-OCR\tesseract.exe'


class PortalLoginConfig(object):

    def __init__(self, driver, url):
        self.url = url
        self.driver = driver
        self.account = 'yuenu002'
        self.password = 'a123456'
        self.file_path = f'./recaptcha/captcha.png'
        self.withdraw_password = '123456'
        self.wait = WebDriverWait(self.driver, 3.5, poll_frequency=0.25)
        self.enter_lobby_wait = WebDriverWait(self.driver, 10, poll_frequency=0.25)

    def check_has_announcement(self):
        try:
            element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[ng-bind="langs.Common_Closed"]')))
            self.driver.execute_script("arguments[0].click();", element)
        except:
            print('None announcement')

        try:
            element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.fal.fa-2x.fa-times-circle')))
            self.driver.execute_script("arguments[0].click();", element)
        except:
            pass
            # print('None announcement2')

        # 舊寫法，改用顯示等待較有彈性
        # soup = BeautifulSoup(self.driver.page_source, 'lxml')
        # announcement_element = soup.select('div.show#marquee-wrapper')
        # announcement2 = soup.find_all(class_='modal-overlay modal-show')
        # time.sleep(2)
        # if len(announcement_element) != 0:
        #     self.driver.find_element_by_xpath('//*[@id="marquee"]/footer/span').click()
        # else:
        #     print('None announcement')
        #
        # if len(announcement2) != 0:
        #     self.driver.find_element_by_xpath('/html/body/div[7]/div[2]/div[2]/i').click()

    def device_verification(self):
        try:
            wait = WebDriverWait(self.driver, 5, poll_frequency=0.25)
            element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.fas.fa-times-circle.close')))
            self.driver.execute_script("arguments[0].click();", element)
        except:
            pass

        # 舊寫法，改用顯示等待較有彈性
        # soup = BeautifulSoup(self.driver.page_source, 'lxml')
        # device_verification = soup.select('i.fas.fa-times-circle.close')
        # device_verification2 = self.driver.find_elements_by_css_selector('.fas.fa-times-circle.close')
        # time.sleep(0.4)
        # # 裝置驗證彈窗辨識
        # if len(device_verification) != 0 or len(device_verification2) != 0:
        #     self.driver.find_element_by_css_selector('.fas.fa-times-circle.close').click()
        # else:
        #     time.sleep(3)

    def send_user_info(self, account, password):
        time.sleep(1.5)
        self.driver.find_element_by_id('login_account').send_keys(account)
        self.driver.find_element_by_id('login_password').send_keys(password)

    def parsing_page_source_and_save_image_send_code(self):
        self.driver.find_element_by_css_selector('#login_code').click()
        time.sleep(2)
        soup = BeautifulSoup(self.driver.page_source, 'lxml')
        image_string = soup.select('#captcha')[0].get('ng-src')[22:]
        image_data = base64.b64decode(image_string)
        try:
            with open(self.file_path, 'wb') as f:
                f.write(image_data)

        except UnidentifiedImageError:
            self.driver.find_element_by_css_selector('#login_code').click()
            time.sleep(2.5)
            soup = BeautifulSoup(self.driver.page_source, 'lxml')
            image_string = soup.select('#captcha')[0].get('ng-src')[22:]
            image_data = base64.b64decode(image_string)
            with open(self.file_path, 'wb') as f:
                f.write(image_data)

        captcha_code = idenitfy_img(self.file_path)
        if len(captcha_code) == 4:
            self.driver.find_element_by_css_selector('#login_code').send_keys(captcha_code)
        else:
            print('The cpatcha_code < 4')
            self.driver.find_element_by_css_selector('#login_code').send_keys('0000')

    def click_loginIn(self):
        self.driver.find_element_by_css_selector('#login-box').click()
        self.device_verification()
        self.check_has_announcement()

    def login_failed(self):
        soup = BeautifulSoup(self.driver.page_source, 'lxml')
        time.sleep(1)
        alert = soup.find_all(class_='custom-modal')
        valid = soup.select("#cms-modal-input")
        if len(alert) == 1 or len(valid) == 1:
            for i in range(10):
                soup = BeautifulSoup(self.driver.page_source, 'lxml')
                alert = soup.find_all(class_='custom-modal')
                valid = soup.select("#cms-modal-input")
                if len(alert) == 1 and len(valid) == 0:
                    print('驗證碼錯誤')
                    self.driver.find_element_by_css_selector('[ng-click="ok()"]').click()
                    self.parsing_page_source_and_save_image_send_code()
                    self.click_loginIn()
                    time.sleep(2)

                elif len(alert) == 1 and len(valid) == 1:
                    print('跨區驗證')
                    time.sleep(1)
                    self.driver.find_element_by_xpath('//*[@id="cms-modal-input"]').send_keys(self.withdraw_password)
                    self.driver.find_element_by_css_selector('[ng-click="ok()"]').click()
                    self.device_verification()
                    self.check_has_announcement()
                else:
                    break
        else:
            pass

    def login(self):
        self.check_has_announcement()
        self.send_user_info(self.account, self.password)
        self.parsing_page_source_and_save_image_send_code()
        self.click_loginIn()
        self.login_failed()
        time.sleep(2)

    def logout(self):
        self.driver.get('http://www.jp777.net/Account/SignOut')

    def switch_window(self):
        windows = self.driver.window_handles  # 獲得當前瀏覽器所有視窗
        self.driver.switch_to.window(windows[-1])  # 切換至最新彈窗

    def switch_frame(self):
        frame = self.driver.find_element_by_css_selector('frame')
        self.driver.switch_to.frame(frame)

    def switch_iframe(self):
        iframe = self.driver.find_element_by_css_selector('iframe')
        self.driver.switch_to.frame(iframe)

    def close_window_buffer(self):
        self.driver.close()
        self.switch_window()
        time.sleep(2.5)
        click_space = self.driver.find_element_by_css_selector('.top-header .wrapper')
        ActionChains(self.driver).move_to_element_with_offset(click_space, 600, 15).click().perform()
        time.sleep(2)

    def detect_maintain(self):
        time.sleep(3)
        try:
            maintain = self.driver.find_element_by_css_selector('.maintain').text
            if '系统维护中' in maintain:
                print(maintain)
                return True
            time.sleep(3)
            self.close_window_buffer()
        except:
            return False

    def into_game_lobby_setting(self, game_name):
        # game_name is what you want to enter game
        time.sleep(2)
        self.switch_window()
        time.sleep(1)
        self.switch_iframe()
        page_num = self.driver.find_element_by_css_selector('[ng-bind="page.total"]').text
        find_game = self.driver.find_elements_by_css_selector(f'[title="{game_name}"]')
        try:
            if page_num == 0:
                # if total page is zero, then no game display
                print('此娛樂城大廳沒開遊戲')
            elif page_num == 1:
                element = self.enter_lobby_wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, f'[title="{game_name}"]')))
                self.driver.execute_script("arguments[0].click();", element)
            else:
                # total page is multiple, check every page whether or not the game
                for x in range(int(page_num)):
                    try:
                        if len(find_game) != 0:
                            game = self.driver.find_element_by_css_selector(f'[title="{game_name}"]')
                            self.driver.execute_script("arguments[0].click();", game)
                        else:
                            self.driver.find_element_by_css_selector('[ng-click="changePage(page.index+1)"]').click()
                            time.sleep(2)
                            game = self.driver.find_element_by_css_selector(f'[title="{game_name}"]')
                            self.driver.execute_script("arguments[0].click();", game)
                    except:
                        pass
        except:
            pass

class GameHall(PortalLoginConfig):

    # """捕鱼游戏"""
    def goAPfish(self):
        lobby_fish = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[3]/a')  # "捕鱼游戏"下拉式選單
        ap_fish = self.driver.find_element_by_css_selector('[game-box="ap-jinchan"]')  # AP金蟾捕鱼
        ActionChains(self.driver).move_to_element(lobby_fish).click(ap_fish).perform()
        time.sleep(12)
        self.switch_window()
        self.detect_maintain()
        time.sleep(1)
        try:
            canvas = self.driver.find_element_by_id('layaCanvas')
            ActionChains(self.driver).move_to_element_with_offset(canvas, 600, 300).click().perform()  # 點擊0.1元炮場
            time.sleep(8)
            for j in range(3):
                ActionChains(self.driver).move_by_offset(0, 0).click().perform()  # 發炮
        except:
            self.switch_window()
            self.switch_iframe()
            canvas = self.driver.find_element_by_id('layaCanvas')
            ActionChains(self.driver).move_to_element_with_offset(canvas, 600, 300).click().perform()  # 點擊0.1元炮場
            time.sleep(8)
            for j in range(3):
                ActionChains(self.driver).move_by_offset(0, 0).click().perform()  # 發炮
        finally:
            time.sleep(8)
            self.close_window_buffer()

    def goFGbird(self):
        lobby_fish = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[3]/a')  # "捕鱼游戏"下拉式選單
        fg_bird = self.driver.find_element_by_css_selector('[game-box="fg-bird"]')
        ActionChains(self.driver).move_to_element(lobby_fish).click(fg_bird).perform()
        time.sleep(12)
        self.switch_window()
        self.detect_maintain()
        time.sleep(1)
        canvas = self.driver.find_element_by_id('GameCanvas')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 235, 335).click().perform()  # 點擊0.1元炮場
        time.sleep(4)
        for j in range(5):
            ActionChains(self.driver).move_by_offset(0, 0).click().perform()  # 發炮
        time.sleep(10)
        self.close_window_buffer()

    def goFGfish(self):
        lobby_fish = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[3]/a')  # "捕鱼游戏"下拉式選單
        fg_fish = self.driver.find_element_by_css_selector('[game-box="fg-beauty"]')  # FG美人捕鱼
        ActionChains(self.driver).move_to_element(lobby_fish).click(fg_fish).perform()
        time.sleep(10)
        self.switch_window()
        time.sleep(2)
        canvas = self.driver.find_element_by_id('GameCanvas')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 250, 400).click().perform()  # 點擊0.1元炮場
        time.sleep(5)
        ActionChains(self.driver).move_by_offset(830, -370).click().perform()  # Close "x"
        for j in range(5):
            ActionChains(self.driver).move_by_offset(0, 0).click().perform()  # 發炮
        time.sleep(8)
        self.close_window_buffer()

    def goGPKfish(self):
        lobby_fish = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[3]/a')  # "捕鱼游戏"下拉式選單
        gpk_fish = self.driver.find_element_by_css_selector('[game-box="gpk-monopoly"]')  # GPK捕鱼大富翁
        ActionChains(self.driver).move_to_element(lobby_fish).click(gpk_fish).perform()
        time.sleep(14)
        self.switch_window()
        time.sleep(1)
        try:
            canvas = self.driver.find_element_by_id('layaCanvas')
            ActionChains(self.driver).move_to_element_with_offset(canvas, 250, 400).click().perform()  # 點擊0.1元炮場
            time.sleep(12)
            for j in range(3):
                ActionChains(self.driver).move_by_offset(0, 0).click().perform()  # 發炮
            time.sleep(8)
        except:
            maintain = self.driver.find_element_by_css_selector('.maintain').text
            if '系统维护中' in maintain:
                print(maintain)
            time.sleep(2)
        self.close_window_buffer()

    def goGPK2fish(self):
        if self.url != 'http://www.jp777.net/':
            lobby_fish = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[3]/a')  # "捕鱼游戏"下拉式選單
            gpk2_fish = self.driver.find_element_by_css_selector('[ng-click="toGpk2Fish()"]')  # GPK2大圣降魔
            ActionChains(self.driver).move_to_element(lobby_fish).click(gpk2_fish).perform()
            time.sleep(16)
            self.switch_window()
            time.sleep(1)
            try:
                canvas = self.driver.find_element_by_id('gamec')
                ActionChains(self.driver).move_to_element_with_offset(canvas, 1000, 720).click().perform()  # 確認玩家身分
                time.sleep(2)
                ActionChains(self.driver).move_by_offset(220, -590).click().perform()  # 排行榜 點擊'x'
                time.sleep(2)
                ActionChains(self.driver).move_by_offset(-700, 300).click().perform()
                time.sleep(6)
                for j in range(50):
                    ActionChains(self.driver).move_by_offset(0, 0).click().perform()  # 發炮
                time.sleep(6)
            except:
                maintain = self.driver.find_element_by_css_selector('.maintain').text
                if '系统维护中' in maintain:
                    print(maintain)
                time.sleep(2)
            self.close_window_buffer()
        else:
            print('AB007沒有GPK2捕魚')

    def goJDBfish(self):
        lobby_fish = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[3]/a')  # "捕鱼游戏"下拉式選單
        jdb_fish = self.driver.find_element_by_css_selector('[game-box="jdb-dragon"]')  # JDB龙王捕鱼
        ActionChains(self.driver).move_to_element(lobby_fish).click(jdb_fish).perform()
        time.sleep(14)
        self.switch_window()
        time.sleep(1)
        canvas = self.driver.find_element_by_id('StageDelegateDiv')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 400, 300).click().perform()  # 點擊0.1元炮場
        time.sleep(4)
        for j in range(3):
            ActionChains(self.driver).move_by_offset(0, 0).click().perform()  # 發炮
        time.sleep(10)
        self.close_window_buffer()

    # TH捕魚關閉的話不會馬上把錢轉出來，後面有皆其他娛樂城的話不會帶錢進去
    def goTHfish(self):
        lobby_fish = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[3]/a')  # "捕鱼游戏"下拉式選單
        th_fish = self.driver.find_element_by_css_selector('[game-box="th-toad"]')  # TH金蟾捕鱼
        ActionChains(self.driver).move_to_element(lobby_fish).click(th_fish).perform()
        time.sleep(14)
        self.switch_window()
        time.sleep(2)
        canvas = self.driver.find_element_by_id('StageDelegateDiv')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 600, 350).click().perform()  # 點擊0.1元炮場
        time.sleep(8)
        for j in range(70):
            ActionChains(self.driver).move_by_offset(0, 0).click().perform()  # 發炮
        time.sleep(5)
        self.close_window_buffer()

    def goLEGfish(self):
        lobby_fish = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[3]/a')  # "捕鱼游戏"下拉式選單
        leg_fish = self.driver.find_element_by_css_selector('[game-box="leg-fish"]')  # LEG捕鱼大作战
        ActionChains(self.driver).move_to_element(lobby_fish).click(leg_fish).perform()
        time.sleep(14)
        self.switch_window()
        time.sleep(2)
        canvas = self.driver.find_element_by_id('StageDelegateDiv')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 250, 400).click().perform()  # 點擊0.1元炮場
        time.sleep(5)
        ActionChains(self.driver).move_by_offset(975, 215).click().perform()  # 自動射擊
        time.sleep(2)
        ActionChains(self.driver).move_by_offset(0, 0).click().perform()
        time.sleep(5)
        self.close_window_buffer()

    '''MV捕魚花錢可能會比較多一點,一發1元'''
    def goMTfish(self):
        lobby_fish = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[3]/a')  # "捕鱼游戏"下拉式選單
        mt_fish = self.driver.find_element_by_css_selector('[game-box="mt-lee"]')  # MT美天李逵劈鱼
        ActionChains(self.driver).move_to_element(lobby_fish).click(mt_fish).perform()
        time.sleep(15)
        self.switch_window()
        time.sleep(2)
        canvas = self.driver.find_element_by_id('layaCanvas')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 250, 450).click().perform()  # 點擊0.1元炮場
        time.sleep(11)
        ActionChains(self.driver).move_by_offset(885, -340).click().perform()  # 點"x"
        time.sleep(1)
        for j in range(3):
            ActionChains(self.driver).move_by_offset(0, 0).click().perform()  # 發炮
        time.sleep(5)
        self.close_window_buffer()

    def goMWfish(self):
        lobby_fish = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[3]/a')  # "捕鱼游戏"下拉式選單
        mw_fish = self.driver.find_element_by_css_selector('[game-box="mw-fish"]')  # MW千炮捕鱼
        ActionChains(self.driver).move_to_element(lobby_fish).click(mw_fish).perform()
        time.sleep(20)
        self.switch_window()
        time.sleep(2)
        canvas = self.driver.find_element_by_id('StageDelegateDiv')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 200, 250).click().perform()  # 點擊0.1元炮場
        time.sleep(15)
        ActionChains(self.driver).move_by_offset(450, 140).click().perform()  # 點"確定"
        time.sleep(1)
        for j in range(3):
            ActionChains(self.driver).move_by_offset(0, 0).click().perform()  # 點擊
            time.sleep(2)
        time.sleep(5)
        self.close_window_buffer()

    def goVGfish(self):
        lobby_fish = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[3]/a')  # "捕鱼游戏"下拉式選單
        vg_fish = self.driver.find_element_by_css_selector('[game-box="vg-fish"]')  # VG龙王捕鱼
        ActionChains(self.driver).move_to_element(lobby_fish).click(vg_fish).perform()
        self.switch_window()
        check_is_maintain = self.detect_maintain()
        if not check_is_maintain:
            time.sleep(13)
            try:
                canvas = self.driver.find_element_by_id('StageDelegateDiv')
                ActionChains(self.driver).move_to_element_with_offset(canvas, 270, 500).click().perform()  # 點擊0.1元炮場
                time.sleep(7)
                for j in range(5):
                    ActionChains(self.driver).move_by_offset(0, 0).click().perform()  # 發炮
            except:
                print('pass here')
        time.sleep(6)
        self.close_window_buffer()

    def goBSPfish(self):
        if self.url == 'http://www.jp777.net/':
            lobby_fish = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[5]/a')  # "电子游艺"下拉式選單
            gpk_slot = self.driver.find_element_by_css_selector('[ng-click="toGpkSlot()"]')  # GPK电子游艺
            ActionChains(self.driver).move_to_element(lobby_fish).click(gpk_slot).perform()
            time.sleep(5)
            self.switch_window()
            time.sleep(1)
            lobby_sport = self.driver.find_element_by_css_selector('.lobbyNav-pager')  # 導航
            ActionChains(self.driver).move_to_element(lobby_sport).click().perform()
            self.driver.find_elements_by_css_selector('.lobbyNav-category [ng-repeat="nav in navInfoList"]')[
                6].click()  # 捕魚
            time.sleep(2)
            bsp_fish = self.driver.find_element_by_css_selector('[game-box="BspFishCannon"]')  # BSP 千炮捕魚王 3D
            ActionChains(self.driver).move_to_element(bsp_fish).click().perform()
        else:
            lobby_fish = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[3]/a')  # "捕鱼游戏"下拉式選單
            fish = self.driver.find_element_by_css_selector('[ng-click="toBspFishCannon()"]')  # BSP千炮捕鱼王3D
            ActionChains(self.driver).move_to_element(lobby_fish).click(fish).perform()
        time.sleep(12)
        self.switch_window()
        self.detect_maintain()
        time.sleep(2)
        canvas = self.driver.find_element_by_css_selector('.home')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 1100, 150).click().perform()  # 'x'
        time.sleep(1)
        ActionChains(self.driver).move_by_offset(-800, 250).click().perform()  # 點擊0.1元炮場
        time.sleep(10)
        ActionChains(self.driver).move_by_offset(290, 415).click().perform()  # 點擊自動
        time.sleep(2)
        ActionChains(self.driver).move_by_offset(0, 0).click().perform()
        time.sleep(5)
        self.close_window_buffer()

    def goICGfish(self):
        if self.url == 'http://www.jp777.net/':
            lobby_fish = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[5]/a')  # "电子游艺"下拉式選單
            gpk_elgame = self.driver.find_element_by_css_selector('[ng-click="toGpkSlot()"]')  # GPK电子游艺
            ActionChains(self.driver).move_to_element(lobby_fish).click(gpk_elgame).perform()
            time.sleep(5)
            self.switch_window()
            time.sleep(1)
            lobby_sport = self.driver.find_element_by_css_selector('.lobbyNav-pager')  # 導航
            ActionChains(self.driver).move_to_element(lobby_sport).click().perform()
            self.driver.find_elements_by_css_selector('.lobbyNav-category [ng-repeat="nav in navInfoList"]')[
                6].click()  # 捕魚
            time.sleep(2)
            icg_fish = self.driver.find_element_by_css_selector('[game-box="IcgFish"]')  # ICG 龙珠捕鱼
            ActionChains(self.driver).move_to_element(icg_fish).click().perform()
        else:
            lobby_fish = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[3]/a')  # "电子游艺"下拉式選單
            fish = self.driver.find_element_by_css_selector('[ng-click="toIcgFish()"]')  # GPK电子游艺
            ActionChains(self.driver).move_to_element(lobby_fish).click(fish).perform()
        time.sleep(10)
        self.switch_window()
        self.switch_iframe()
        canvas = self.driver.find_element_by_id('GameCanvas')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 250, 400).click().perform()  # '0.01炮場'
        time.sleep(10)
        for j in range(10):
            ActionChains(self.driver).move_by_offset(0, 0).click().perform()
        time.sleep(8)
        if self.url == 'http://www.jp777.net/':
            self.driver.close()
            self.switch_window()
        self.close_window_buffer()

    '''停止代理'''
    # def goYGfish(self):
    #     lobby_fish = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[3]/a')  # "捕鱼游戏"下拉式選單
    #     goYGfish = self.driver.find_element_by_css_selector('[game-box="yg-fishseaking"]')  # YG超级海王
    #     ActionChains(self.driver).move_to_element(lobby_fish).click(goYGfish).perform()
    #     time.sleep(10)
    #     self.switch_window()
    #     time.sleep(2)
    #     ActionChains(self.driver).move_by_offset(0, 0).click().perform()  # 點擊0.1元炮場
    #     time.sleep(2)
    #     ActionChains(self.driver).move_by_offset(115, 225).click().perform()  # 點擊自動
    #     time.sleep(2)
    #     ActionChains(self.driver).move_by_offset(0, 0).click().perform()
    #     time.sleep(8)
    #     self.close_window_buffer()

    def goKAfish(self):
        if self.url == 'http://www.jp777.net/':
            lobby_fish = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[5]/a')  # "电子游艺"下拉式選單
            gpk_elgame = self.driver.find_element_by_css_selector('[ng-click="toGpkSlot()"]')  # GPK电子游艺
            ActionChains(self.driver).move_to_element(lobby_fish).click(gpk_elgame).perform()
            time.sleep(5)
            self.switch_window()
            time.sleep(1)
            lobby_sport = self.driver.find_element_by_css_selector('.lobbyNav-pager')  # 導航
            ActionChains(self.driver).move_to_element(lobby_sport).click().perform()
            self.driver.find_elements_by_css_selector('.lobbyNav-category [ng-repeat="nav in navInfoList"]')[
                6].click()  # 捕魚
            time.sleep(1)
            ka_fish = self.driver.find_element_by_css_selector('[game-box="KaFish"]')  # KA
            ActionChains(self.driver).move_to_element(ka_fish).click().perform()
        else:
            lobby_fish = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[3]/a')  # "捕鱼游戏"下拉式選單
            gpk_elgame = self.driver.find_element_by_css_selector('[ng-click="toKaFish()"]')  # KA爽爽捕鱼
            ActionChains(self.driver).move_to_element(lobby_fish).click(gpk_elgame).perform()
        time.sleep(13)
        self.switch_window()
        time.sleep(1)
        canvas = self.driver.find_element_by_id('GameCanvas')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 250, 400).click().perform()  # '0.01炮
        time.sleep(5)
        ActionChains(self.driver).move_by_offset(1000, 0).click().perform() # 點擊自動射擊
        time.sleep(1)
        ActionChains(self.driver).move_by_offset(0, 0).click().perform()  # click dou dou
        time.sleep(6)
        self.close_window_buffer()

    def goBBINfish(self):
        lobby_fish = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[3]/a')  # "捕鱼游戏"下拉式選單
        fish = self.driver.find_element_by_css_selector('[ng-click="toBbFish2()"]')  # BBIN捕鱼大师
        ActionChains(self.driver).move_to_element(lobby_fish).click(fish).perform()
        time.sleep(22)
        self.switch_window()
        self.detect_maintain()
        canvas = self.driver.find_element_by_id('gameCanvas')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 150, 240).click().perform()  # 點擊0.1元炮場
        time.sleep(6)
        ActionChains(self.driver).move_by_offset(590, 190).click().perform()  # 其他
        time.sleep(2)
        ActionChains(self.driver).move_by_offset(0, 110).click().perform()  # confirm
        time.sleep(2)
        for i in range(50):
            ActionChains(self.driver).move_to_element_with_offset(canvas, 150, 250).click().perform()
        time.sleep(6)
        self.close_window_buffer()

    def goCQ9fish(self):
        lobby_fish = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[3]/a')  # "捕鱼游戏"下拉式選單
        fish = self.driver.find_element_by_css_selector('[ng-click="toCq9Fish()"]')  # CQ9皇金渔场
        ActionChains(self.driver).move_to_element(lobby_fish).click(fish).perform()
        time.sleep(42)
        self.switch_window()
        self.detect_maintain()
        canvas = self.driver.find_element_by_id('game-container')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 180, 330).click().perform()  # 點擊0.1元炮場
        time.sleep(92)
        for i in range(30):
            ActionChains(self.driver).move_by_offset(0, 0).click().perform()
        time.sleep(6)
        self.close_window_buffer()

    def goBGfish(self):
        lobby_fish = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[3]/a')  # "捕鱼游戏"下拉式選單
        fish = self.driver.find_element_by_css_selector('[ng-click="toBgFish()"]')  # BG捕鱼大师
        ActionChains(self.driver).move_to_element(lobby_fish).click(fish).perform()
        time.sleep(36)
        self.switch_window()
        self.detect_maintain()
        canvas = self.driver.find_element_by_id('layaCanvas')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 180, 330).click().perform()  # 點擊0.1元炮場
        time.sleep(28)
        for i in range(5):
            ActionChains(self.driver).move_by_offset(0, 0).click().perform()
        time.sleep(8)
        self.close_window_buffer()

    '''
    
    电子游艺 (AB005)
    
    '''
    def goAEelgame(self):
        lobby_elgame = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[5]/a')  # "电子游艺"下拉式選單
        ae_elgame = self.driver.find_element_by_css_selector('[ng-click="toAeHtml()"]')  # AE阿米巴电子游艺
        ActionChains(self.driver).move_to_element(lobby_elgame).click(ae_elgame).perform()
        self.into_game_lobby_setting('一本万利')
        time.sleep(8)
        self.switch_window()
        self.switch_iframe()
        canvas = self.driver.find_element_by_id('gameDiv')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 210, 640).click().perform()
        for i in range(4):
            ActionChains(self.driver).move_by_offset(0, 0).click().perform()  # 3 確定
            time.sleep(0.3)
        ActionChains(self.driver).move_by_offset(425, 0).click().perform()  # 3 確定
        time.sleep(8)
        self.close_window_buffer()

    def goPGelgame(self):
        lobby_elgame = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[5]/a')  # "电子游艺"下拉式選單
        pg_elgame = self.driver.find_element_by_css_selector('[ng-click="toJtnHtml()"]')  # PG电子游艺
        ActionChains(self.driver).move_to_element(lobby_elgame).click(pg_elgame).perform()
        if self.url == 'http://www.rfben.com/':
            self.into_game_lobby_setting('麻将胡了')
        else:
            self.into_game_lobby_setting('赏金船长')
        time.sleep(14)
        self.switch_window()
        self.switch_iframe()
        canvas = self.driver.find_element_by_id('Cocos2dGameContainer')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 640, 660).click().perform()  # 開始
        time.sleep(2)
        ActionChains(self.driver).move_by_offset(-110, 90).click().perform()  # "減碼按鈕"
        time.sleep(1)
        for j in range(10):
            ActionChains(self.driver).move_by_offset(0, 0).click().perform()
        ActionChains(self.driver).move_by_offset(100, 0).click().perform()
        time.sleep(5)
        ActionChains(self.driver).move_by_offset(0, 0).click().perform()  # "轉動按鈕"
        time.sleep(8)
        self.close_window_buffer()

    def goSGelgame(self):
        lobby_elgame = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[5]/a')  # "电子游艺"下拉式選單
        sg_elgame = self.driver.find_element_by_css_selector('[ng-click="toSgFlash()"]')  # SG电子游艺
        ActionChains(self.driver).move_to_element(lobby_elgame).click(sg_elgame).perform()
        self.into_game_lobby_setting('金鸡')
        # time.sleep(5)
        # self.switch_window()
        # self.switch_iframe()
        # time.sleep(1)
        # self.driver.find_element_by_css_selector('[title="金鸡"]').click()
        time.sleep(12)
        self.switch_window()
        time.sleep(1)
        ActionChains(self.driver).move_by_offset(-230, 570).click().perform()  # 有活動頁暫先註解
        for j in range(8):
            ActionChains(self.driver).move_by_offset(0, 0).click().perform()
        ActionChains(self.driver).move_by_offset(920, 0).click().perform()  # "轉動按鈕"
        time.sleep(4)
        for j in range(2):
            ActionChains(self.driver).move_by_offset(0, 0).click().perform()
            time.sleep(4)
        time.sleep(8)
        self.driver.close()
        self.switch_window()
        self.close_window_buffer()

    def goSWelgame(self):
        lobby_elgame = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[5]/a')  # "电子游艺"下拉式選單
        sw_elgame = self.driver.find_element_by_css_selector('[ng-click="toPtsHtml()"]')  # 天风电子游艺
        ActionChains(self.driver).move_to_element(lobby_elgame).click(sw_elgame).perform()
        self.into_game_lobby_setting('天上凤凰')
        # # time.sleep(6)
        # self.switch_window()
        # self.switch_iframe()
        # game_name = self.into_lobby_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[title="天上凤凰"]')))
        # # self.driver.execute_script("arguments[0].click();", game_name)
        # if len(self.driver.find_elements_by_css_selector('[title="天上凤凰"]')) != 0:
        #     self.driver.execute_script("arguments[0].click();", game_name)
        # elif len(self.driver.find_elements_by_css_selector('[title="天上凤凰"]')) == 0:
        #     self.driver.find_element_by_css_selector('[ng-click="changePage(page.index+1)"]').click()
        #     time.sleep(2)
        #     self.driver.execute_script("arguments[0].click();", game_name)
        # else:
        #     pass
        time.sleep(16)
        self.switch_window()
        self.switch_iframe()
        canvas = self.driver.find_element_by_id('canvas')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 640, 650).click().perform()  # "減碼按鈕"
        time.sleep(2)
        ActionChains(self.driver).move_by_offset(-325, 50).click().perform()  # "減碼按鈕"
        for j in range(10):
            ActionChains(self.driver).move_by_offset(0, 0).click().perform()
        ActionChains(self.driver).move_by_offset(800, 0).click().perform()  # "轉動按鈕"
        for j in range(3):
            ActionChains(self.driver).move_by_offset(0, 0).click().perform()
            time.sleep(4)
        time.sleep(6)
        self.close_window_buffer()

    def goDTelgame(self):
        lobby_elgame = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[5]/a')  # "电子游艺"下拉式選單
        DT_elgame = self.driver.find_element_by_css_selector('[ng-click="toDtHtml()"]')  # DT梦想电子游艺
        ActionChains(self.driver).move_to_element(lobby_elgame).click(DT_elgame).perform()
        self.into_game_lobby_setting('赛亚烈战')
        # time.sleep(8)
        # self.switch_window()
        # self.switch_iframe()
        # pagenum = self.driver.find_element_by_css_selector('[ng-bind="page.total"]').text
        # for x in range(int(pagenum)):
        #     try:
        #         if len(self.driver.find_elements_by_css_selector('[title="赛亚烈战"]')) != 0:
        #             self.driver.find_element_by_css_selector('[title="赛亚烈战"]').click()
        #         else:
        #             self.driver.find_element_by_css_selector('[ng-click="changePage(page.index+1)"]').click()
        #             time.sleep(1)
        #             self.driver.find_element_by_css_selector('[title="赛亚烈战"]').click()
        #     except:
        #         pass
        time.sleep(18)
        self.switch_window()
        self.switch_iframe()
        canvas = self.driver.find_element_by_id('gameCanvas')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 60, 680).click().perform() # '-注'
        for i in range(6):
            ActionChains(self.driver).move_by_offset(0, 0).click().perform()
        ActionChains(self.driver).move_by_offset(1100, 0).click().perform()  # 攻擊
        time.sleep(5)
        ActionChains(self.driver).move_by_offset(0, 0).click().perform()
        time.sleep(8)
        self.close_window_buffer()

    def goDT2elgame(self):
        lobby_elgame = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[5]/a')  # "电子游艺"下拉式選單
        DT_elgame = self.driver.find_element_by_css_selector('[ng-click="toDtHtml()"]')  # DT梦想电子游艺
        ActionChains(self.driver).move_to_element(lobby_elgame).click(DT_elgame).perform()
        time.sleep(8)
        self.switch_window()
        self.switch_iframe()
        self.driver.find_element_by_css_selector('[title="武松传"]').click()  # 武松传
        time.sleep(15)
        self.switch_window()
        self.switch_iframe()
        canvas = self.driver.find_element_by_id('gameCanvas')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 230, 685).click().perform() # '-注'
        for i in range(10):
            ActionChains(self.driver).move_by_offset(0, 0).click().perform()
        ActionChains(self.driver).move_by_offset(-195, 0).click().perform()  # '-數'
        for j in range(24):
            ActionChains(self.driver).move_by_offset(0, 0).click().perform()
        time.sleep(1)
        ActionChains(self.driver).move_by_offset(1165, 0).click().perform()  # 旋轉
        for k in range(3):
            ActionChains(self.driver).move_by_offset(0, 0).click().perform()
            time.sleep(5)
        time.sleep(6)
        self.close_window_buffer()

    def goTOGelgame(self):
        lobby_elgame = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[5]/a')  # "电子游艺"下拉式選單
        TOG_elgame = self.driver.find_element_by_css_selector('[ng-click="toTogHtml()"]')  # TOG星球电子游艺
        ActionChains(self.driver).move_to_element(lobby_elgame).click(TOG_elgame).perform()
        self.into_game_lobby_setting('大闹天宫')
        # time.sleep(6)
        # self.switch_window()
        # self.switch_iframe()
        # time.sleep(1)
        # self.driver.find_element_by_css_selector('[title="大闹天宫"]').click()  # 大闹天宫
        time.sleep(26)
        self.switch_window()
        self.switch_iframe()
        canvas = self.driver.find_element_by_id('GameLauncher')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 835, 720).click().perform()  # 籌碼
        time.sleep(1)
        ActionChains(self.driver).move_by_offset(-147, -90).click().perform()  # '-'數
        for i in range(5):
            ActionChains(self.driver).move_by_offset(0, 0).click().perform()
        time.sleep(1)
        ActionChains(self.driver).move_by_offset(450, 80).click().perform()  # 轉動開始
        time.sleep(10)
        self.close_window_buffer()

    def goGPKelgame(self):
        lobby_elgame = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[5]/a')  # "电子游艺"下拉式選單
        GPK_elgame = self.driver.find_element_by_css_selector('[ng-click="toGpkSlot()"]')  # GPK电子游艺
        ActionChains(self.driver).move_to_element(lobby_elgame).click(GPK_elgame).perform()
        self.into_game_lobby_setting('秦皇传说')
        # time.sleep(5)
        # self.switch_window()
        # self.switch_iframe()
        # time.sleep(1)
        # pagenum = self.driver.find_element_by_css_selector('[ng-bind="page.total"]').text
        # for x in range(int(pagenum)):
        #     try:
        #         if len(self.driver.find_elements_by_css_selector('[title="秦皇传说"]')) != 0:
        #             self.driver.find_element_by_css_selector('[title="秦皇传说"]').click()  # 秦皇传说
        #         else:
        #             self.driver.find_element_by_css_selector('[ng-click="changePage(page.index+1)"]').click()
        #             time.sleep(1)
        #             self.driver.find_element_by_css_selector('[title="秦皇传说"]').click()
        #     except:
        #         pass
        check_is_maintain = self.detect_maintain()
        if not check_is_maintain:
            time.sleep(18)
            self.switch_window()
            self.switch_iframe()
            canvas = self.driver.find_element_by_id('GameCanvas')
            ActionChains(self.driver).move_to_element_with_offset(canvas, 1140, 120).click().perform()  # 'x'
            time.sleep(2)
            ActionChains(self.driver).move_by_offset(0, 0).click().perform()  # 'x'
            time.sleep(2)
            ActionChains(self.driver).move_by_offset(0, 0).click().perform()  # 'x'
            time.sleep(2)
            ActionChains(self.driver).move_by_offset(-700, 560).click().perform()  # 押注
            time.sleep(1)
            ActionChains(self.driver).move_by_offset(150, -70).click().perform()  # 1
            ActionChains(self.driver).move_by_offset(600, 0).click().perform()  # 開始
            time.sleep(6)
        else:
            time.sleep(6)
        self.close_window_buffer()

    def goGPK2elgame(self):
        lobby_elgame = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[5]/a')  # "电子游艺"下拉式選單
        GPK2_elgame = self.driver.find_element_by_css_selector('[ng-click="toGpk2Html()"]')  # 战游电子游艺
        ActionChains(self.driver).move_to_element(lobby_elgame).click(GPK2_elgame).perform()
        if self.url == 'http://www.rfben.com/':
            self.into_game_lobby_setting('兔女郎')
        else:
            self.into_game_lobby_setting('海底世界')
        check_is_maintain = self.detect_maintain()
        if not check_is_maintain:
            time.sleep(16)
            self.switch_window()
            self.switch_iframe()
            self.switch_iframe()
            canvas = self.driver.find_element_by_css_selector('canvas')
            ActionChains(self.driver).move_to_element_with_offset(canvas, 640, 670).click().perform()  # '確認'
            time.sleep(3)
            ActionChains(self.driver).move_by_offset(0, 0).click().perform()
            time.sleep(2)
            ActionChains(self.driver).move_by_offset(-220, 0).click().perform()
            for i in range(5):
                ActionChains(self.driver).move_by_offset(0, 0).click().perform()
            ActionChains(self.driver).move_by_offset(800, 0).click().perform()  # 開始
            time.sleep(6)
            for j in range(2):
                ActionChains(self.driver).move_by_offset(0, 0).click().perform()
                time.sleep(5)
        time.sleep(3)
        self.close_window_buffer()

    def goJSelgame(self):
        lobby_elgame = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[5]/a')  # "电子游艺"下拉式選單
        JS_elgame = self.driver.find_element_by_css_selector('[ng-click="toJsHtml()"]')  # JS金龙电子游艺
        ActionChains(self.driver).move_to_element(lobby_elgame).click(JS_elgame).perform()
        if self.url == 'http://www.rfben.com/':
            self.into_game_lobby_setting('五星宏辉')
            time.sleep(14)
            self.switch_window()
            self.switch_iframe()
            canvas = self.driver.find_element_by_id('GameCanvas')
            ActionChains(self.driver).move_to_element_with_offset(canvas, 650, 150).click().perform()
            time.sleep(12)
            ActionChains(self.driver).move_by_offset(-170, 630).click().perform()
            time.sleep(10)
        else:
            self.into_game_lobby_setting('水果机')
            time.sleep(14)
            self.switch_window()
            self.switch_iframe()
            try:
                canvas = self.driver.find_element_by_id('GameCanvas')
                ActionChains(self.driver).move_to_element_with_offset(canvas, 720, 50).click().perform()  # '電玩'
                time.sleep(1)
                ActionChains(self.driver).move_by_offset(80, 400).click().perform()  # '牛仔王'
                time.sleep(3)
                ActionChains(self.driver).move_by_offset(-100, -250).click().perform()  # '新手場'
                time.sleep(5)
                for i in range(25):
                    ActionChains(self.driver).move_by_offset(0, 0).click().perform()
                time.sleep(5)
        # try:  # 水滸傳
        #     canvas = self.driver.find_element_by_id('GameCanvas')
        #     ActionChains(self.driver).move_to_element_with_offset(canvas, 720, 50).click().perform()  # '電玩'
        #     time.sleep(2)
        #     ActionChains(self.driver).move_by_offset(80, 600).click().perform()  # '水滸'
        #     time.sleep(3)
        #     ActionChains(self.driver).move_by_offset(-150, -450).click().perform()
        #     time.sleep(5)
        #     ActionChains(self.driver).move_by_offset(-200, 480).click().perform()  # 'x'
        #     for i in range(5):
        #         ActionChains(self.driver).move_by_offset(0, 0).click().perform()  # 'x'
        #     ActionChains(self.driver).move_by_offset(300, 120).click().perform()  # '旋轉'
        #     time.sleep(8)
        #     ActionChains(self.driver).move_by_offset(-300, -120).click().perform()  # '收分'
        #     time.sleep(2)
        #     ActionChains(self.driver).move_by_offset(0, 0).click().perform()  # 補沒按到收分
        #     time.sleep(5)
            except NoSuchElementException:
                print('JS電子進行系統維護中')
        self.close_window_buffer()

    def goPTelgame(self):
        lobby_elgame = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[5]/a')  # "电子游艺"下拉式選單
        PT_elgame = self.driver.find_element_by_css_selector('[ng-click="toPtFlash()"]')  # PT电子游艺
        ActionChains(self.driver).move_to_element(lobby_elgame).click(PT_elgame).perform()
        self.into_game_lobby_setting('熊之舞')
        # # time.sleep(5)
        # self.switch_window()
        # self.switch_iframe()
        # time.sleep(1)
        # game_name = self.into_lobby_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[title="银行大劫案"]')))
        # self.driver.execute_script("arguments[0].click();", game_name)
        # pagenum = self.driver.find_element_by_css_selector('[ng-bind="page.total"]').text
        # for x in range(int(pagenum)):
        #     try:
        #         if len(self.driver.find_elements_by_css_selector('[title="熊之舞"]')) != 0:
        #             self.driver.find_element_by_css_selector('[title="熊之舞"]').click()
        #         elif len(self.driver.find_elements_by_css_selector('[title="熊之舞"]')) == 0:
        #             self.driver.find_element_by_css_selector('[ng-click="changePage(page.index+1)"]').click()
        #             time.sleep(2)
        #             self.driver.find_element_by_css_selector('[title="熊之舞"]').click()
        #         else:
        #             print('目前PT電子沒有熊之舞')
        #     except:
        #         pass
        time.sleep(18)
        self.switch_window()
        for x in range(7):
            if len(self.driver.find_elements_by_css_selector('#messageBoxButtonYes')) == 1:
                messageBoxButton = self.driver.find_element_by_css_selector('#messageBoxButtonYes')
                ActionChains(self.driver).move_to_element(messageBoxButton).click().perform()
                time.sleep(1)
        self.switch_iframe()
        canvas = self.driver.find_element_by_id('ngm-uicore2-root')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 330, 700).click().perform()  # '確定'
        for i in range(10):
            ActionChains(self.driver).move_by_offset(0, 0).click().perform()
        ActionChains(self.driver).move_by_offset(-130, 0).click().perform()  # '-'
        for j in range(25):
            ActionChains(self.driver).move_by_offset(0, 0).click().perform()
        ActionChains(self.driver).move_by_offset(800, 0).click().perform()  # '旋轉'
        time.sleep(6)
        for k in range(2):
            ActionChains(self.driver).move_by_offset(0, 0).click().perform()
        time.sleep(6)
        self.driver.close()
        self.switch_window()
        self.close_window_buffer()

    '''卡在是否關掉聲音那關，用ActionChain沒有反應'''
    def goFBGelgame(self):
        lobby_elgame = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[5]/a')  # "电子游艺"下拉式選單
        FBG_elgame = self.driver.find_element_by_css_selector('[ng-click="toJv8Html()"]')  # FBG发宝电子游艺
        ActionChains(self.driver).move_to_element(lobby_elgame).click(FBG_elgame).perform()
        time.sleep(6)
        self.switch_window()
        self.switch_iframe()
        time.sleep(1)
        self.driver.find_element_by_css_selector('[title="松鼠战士"]').click()
        time.sleep(30)
        self.switch_window()
        self.switch_iframe()
        self.switch_iframe()
        self.switch_iframe()
        checkbox = self.driver.find_element_by_css_selector('.button--secondary')
        self.driver.execute_script("arguments[0].click();", checkbox)
        time.sleep(3)
        self.driver.switch_to.default_content()
        self.switch_iframe()
        self.switch_iframe()
        canvas = self.driver.find_element_by_css_selector('button[data-auto="COIN_SELECTOR_DEC"]')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 385, 766).click().perform()  # '-'數
        for i in range(6):
            ActionChains(self.driver).move_by_offset(0, 0).click().perform()
        ActionChains(self.driver).move_by_offset(-190, 0).click().perform()
        for j in range(25):
            ActionChains(self.driver).move_by_offset(0, 0).click().perform()
        time.sleep(1)
        ActionChains(self.driver).move_by_offset(850, 0).click().perform()  # 轉動開始
        time.sleep(10)
        self.close_window_buffer()

    def goJDBelgame(self):
        lobby_elgame = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[5]/a')  # "电子游艺"下拉式選單
        JDB_elgame = self.driver.find_element_by_css_selector('[ng-click="toJdbHtml()"]')  # 夺宝电子游艺
        ActionChains(self.driver).move_to_element(lobby_elgame).click(JDB_elgame).perform()
        self.into_game_lobby_setting('芝麻开门')
        # time.sleep(5)
        # self.switch_window()
        # self.switch_iframe()
        # time.sleep(1)
        # if len(self.driver.find_elements_by_css_selector('[title="芝麻开门"]')) != 0:
        #     self.driver.find_element_by_css_selector('[title="芝麻开门"]').click()
        # elif len(self.driver.find_elements_by_css_selector('[title="芝麻开门"]')) == 0:
        #     self.driver.find_element_by_css_selector('[ng-click="changePage(page.index+1)"]').click()
        #     time.sleep(1)
        #     self.driver.find_element_by_css_selector('[title="芝麻开门"]').click()
        # else :
        #     print('JDB電子大廳顯示有問題')
        time.sleep(10)
        self.switch_window()
        self.switch_iframe()
        time.sleep(1)
        if len(self.driver.find_elements_by_css_selector('.modal-inner')) != 0:
            element = self.driver.find_element_by_css_selector('.modal-inner')
            ActionChains(self.driver).move_to_element_with_offset(element, 20, 20).click().perform()
        time.sleep(1)
        self.driver.find_element_by_css_selector('.spinButton').click()
        time.sleep(8)
        self.close_window_buffer()

    def goHBelgame(self):
        lobby_elgame = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[5]/a')  # "电子游艺"下拉式選單
        HB_elgame = self.driver.find_element_by_css_selector('[ng-click="toHabaHtml()"]')  # HB电子游艺
        ActionChains(self.driver).move_to_element(lobby_elgame).click(HB_elgame).perform()
        self.into_game_lobby_setting('鲤鱼门')
        # time.sleep(5)
        # self.switch_window()
        # self.switch_iframe()
        # time.sleep(1)
        # self.driver.find_element_by_css_selector('[title="鲤鱼门"]').click()
        time.sleep(12)
        self.switch_window()
        self.switch_iframe()
        time.sleep(1)
        canvas = self.driver.find_element_by_css_selector('canvas')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 650, 750).click().perform()
        time.sleep(12)
        self.close_window_buffer()

    def goSYelgame(self):
        lobby_elgame = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[5]/a')  # "电子游艺"下拉式選單
        SY_elgame = self.driver.find_element_by_css_selector('[ng-click="toIm2Html()"]')  # SY双赢电子游艺
        ActionChains(self.driver).move_to_element(lobby_elgame).click(SY_elgame).perform()
        self.into_game_lobby_setting('银行大劫案')
        time.sleep(20)
        self.switch_window()
        self.switch_iframe()
        time.sleep(1)
        canvas = self.driver.find_element_by_css_selector('#GameCanvas')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 1030, 575).click().perform()
        time.sleep(8)
        self.close_window_buffer()

    def goFGargame(self):
        lobby_elgame = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[5]/a')  # "电子游艺"下拉式選單
        FG_argame = self.driver.find_element_by_css_selector('[ng-click="toFsHtml()"]')  # 乐游电子游艺
        ActionChains(self.driver).move_to_element(lobby_elgame).click(FG_argame).perform()
        time.sleep(5)
        self.switch_window()
        self.switch_iframe()
        time.sleep(1)
        self.driver.find_element_by_css_selector('[title="幸运5"]').click()
        time.sleep(10)
        self.switch_window()
        self.switch_iframe()
        time.sleep(1)
        try:
            canvas = self.driver.find_element_by_css_selector('#GameCanvas')
            ActionChains(self.driver).move_to_element_with_offset(canvas, 1200, 780).click().perform()
            time.sleep(3)
            ActionChains(self.driver).move_by_offset(0, 0).click().perform()
        except NoSuchElementException:
            print('FG街機進行系統維護中')
        time.sleep(8)
        self.close_window_buffer()

    def goKAelgame(self):
        lobby_elgame = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[5]/a')  # "电子游艺"下拉式選單
        KA_elgame = self.driver.find_element_by_css_selector('[ng-click="toKaHtml()"]')  # KA开发电子游艺
        ActionChains(self.driver).move_to_element(lobby_elgame).click(KA_elgame).perform()
        if self.url == 'http://www.rfben.com/':
            self.into_game_lobby_setting('聚宝盆')
        else:
            self.into_game_lobby_setting('失落的王国')
        time.sleep(12)
        self.switch_window()
        self.switch_iframe()
        time.sleep(1)
        canvas = self.driver.find_element_by_css_selector('#gameCanvas')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 700, 460).click().perform()
        time.sleep(2)
        ActionChains(self.driver).move_by_offset(-135, 90).click().perform()
        time.sleep(8)
        self.close_window_buffer()

    def goPNGelgame(self):
        lobby_elgame = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[5]/a')  # "电子游艺"下拉式選單
        png_elgame = self.driver.find_element_by_css_selector('[ng-click="toPngHtml()"]')  # PNG电子游艺
        ActionChains(self.driver).move_to_element(lobby_elgame).click(png_elgame).perform()
        if self.url == 'http://www.rfben.com/':
            self.into_game_lobby_setting('神秘小丑')
        else:
            self.into_game_lobby_setting('好运招财猫')
        time.sleep(14)
        self.switch_window()
        self.switch_iframe()
        self.switch_iframe()
        time.sleep(1)
        canvas = self.driver.find_element_by_css_selector('#pngCasinoGame')

        if self.url == 'http://www.rfben.com/':
            ActionChains(self.driver).move_to_element_with_offset(canvas, 650, 600).click().perform()
            time.sleep(5)
            ActionChains(self.driver).move_by_offset(-310, 110).click().perform()  # '-'
            for i in range(4):
                ActionChains(self.driver).move_by_offset(0, 0).click().perform()
            ActionChains(self.driver).move_by_offset(710, 0).click().perform()
        else:
            ActionChains(self.driver).move_to_element_with_offset(canvas, 640, 660).click().perform()
            time.sleep(5)
            ActionChains(self.driver).move_by_offset(-210, 50).click().perform()  # '-'
            for i in range(4):
                ActionChains(self.driver).move_by_offset(0, 0).click().perform()
            ActionChains(self.driver).move_by_offset(590, -10).click().perform()
        time.sleep(8)
        self.close_window_buffer()

    def goMTelgame(self):
        lobby_elgame = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[5]/a')  # "电子游艺"下拉式選單
        mt_elgame = self.driver.find_element_by_css_selector('[ng-click="toMtHtml()"]')  # MT美天电子游艺
        ActionChains(self.driver).move_to_element(lobby_elgame).click(mt_elgame).perform()
        time.sleep(5)
        self.switch_window()
        self.switch_iframe()
        time.sleep(1)
        self.driver.find_element_by_css_selector('[title="水浒传"]').click()
        time.sleep(13)
        self.switch_window()
        self.switch_iframe()
        time.sleep(1)
        canvas = self.driver.find_element_by_css_selector('#layaCanvas')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 270, 400).click().perform()
        time.sleep(6)
        ActionChains(self.driver).move_by_offset(830, 300).click().perform()  # 開始
        time.sleep(8)
        self.close_window_buffer()

    def goGHelgame(self):
        lobby_elgame = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[5]/a')  # "电子游艺"下拉式選單
        gh_elgame = self.driver.find_element_by_css_selector('[ng-click="toGhHtml()"]')  # MT美天电子游艺
        ActionChains(self.driver).move_to_element(lobby_elgame).click(gh_elgame).perform()
        if self.url == 'http://www.rfben.com/':
            self.into_game_lobby_setting('鸿运大转盘')
        else:
            self.into_game_lobby_setting('皇炫')
        time.sleep(13)
        self.switch_window()
        self.switch_iframe()
        time.sleep(1)
        canvas = self.driver.find_element_by_css_selector('#canvas')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 760, 550).click().perform()
        time.sleep(3)
        ActionChains(self.driver).move_by_offset(380, 250).click().perform()  # 開始
        time.sleep(8)
        self.close_window_buffer()

    def goICGelgame(self):
        lobby_elgame = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[5]/a')  # "电子游艺"下拉式選單
        icg_elgame = self.driver.find_element_by_css_selector('[ng-click="toIcgHtml()"]')  # GPK电子游艺
        ActionChains(self.driver).move_to_element(lobby_elgame).click(icg_elgame).perform()
        self.into_game_lobby_setting('后羿射日')
        # time.sleep(5)
        # self.switch_window()
        # self.switch_iframe()
        # self.driver.find_element_by_css_selector('[title="后羿射日"]').click()
        time.sleep(12)
        self.switch_window()
        self.switch_iframe()
        # self.switch_iframe()
        time.sleep(1)
        canvas = self.driver.find_element_by_css_selector('#GameCanvas')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 1180, 400).click().perform()
        time.sleep(3)
        time.sleep(8)
        self.driver.close()
        self.switch_window()
        self.close_window_buffer()

    def go07ICGelgame(self):
        lobby_fish = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[5]/a')  # "电子游艺"下拉式選單
        GPK_elgame = self.driver.find_element_by_css_selector('[ng-click="toGpkSlot()"]')  # GPK电子游艺
        ActionChains(self.driver).move_to_element(lobby_fish).click(GPK_elgame).perform()
        time.sleep(5)
        self.switch_window()
        time.sleep(1)
        lobby_sport = self.driver.find_element_by_css_selector('.lobbyNav-pager')  # 導航
        ActionChains(self.driver).move_to_element(lobby_sport).click().perform()
        self.driver.find_elements_by_css_selector('.lobbyNav-category [ng-repeat="nav in navInfoList"]')[
            2].click()  # 捕魚
        time.sleep(1)
        icg_elgame = self.driver.find_element_by_css_selector('[game-box="IcgHtml"]')
        ActionChains(self.driver).move_to_element(icg_elgame).click().perform()
        time.sleep(3)
        self.switch_window()
        self.switch_iframe()
        self.driver.find_element_by_css_selector('[title="后羿射日"]').click()
        time.sleep(12)
        self.switch_window()
        self.switch_iframe()
        self.switch_iframe()
        time.sleep(1)
        canvas = self.driver.find_element_by_css_selector('#GameCanvas')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 1180, 400).click().perform()
        time.sleep(3)
        time.sleep(8)
        self.close_window_buffer()

    def goR8elgame(self):
        lobby_elgame = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[5]/a')  # "电子游艺"下拉式選單
        r8_elgame = self.driver.find_element_by_css_selector('[ng-click="toR8Html()"]')  # R8乐发电子游艺
        ActionChains(self.driver).move_to_element(lobby_elgame).click(r8_elgame).perform()
        if self.url == 'http://www.rfben.com/':
            self.into_game_lobby_setting('鼠来宝')
        else:
            self.into_game_lobby_setting('幸运象神')
        time.sleep(14)
        self.switch_window()
        time.sleep(1)
        canvas = self.driver.find_element_by_css_selector('#gameCanvas')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 40, 787).click().perform()
        time.sleep(2)
        ActionChains(self.driver).move_by_offset(0, 0).click().perform()  # 開始
        time.sleep(1)
        ActionChains(self.driver).move_by_offset(330, -500).click().perform()
        time.sleep(1)
        ActionChains(self.driver).move_by_offset(-50, 440).click().perform()
        time.sleep(1)
        ActionChains(self.driver).move_by_offset(-90, 20).click().perform()  # 轉動
        time.sleep(8)
        self.driver.close()
        self.switch_window()
        self.close_window_buffer()

    def goPPelgame(self):
        lobby_elgame = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[5]/a')  # "电子游艺"下拉式選單
        pp_elgame = self.driver.find_element_by_css_selector('[ng-click="toPrgFlash()"]')  # PP电子游艺
        ActionChains(self.driver).move_to_element(lobby_elgame).click(pp_elgame).perform()
        self.into_game_lobby_setting('西游记')
        # time.sleep(5)
        # self.switch_window()
        # self.switch_iframe()
        # time.sleep(1)
        # self.driver.find_element_by_css_selector('[title="西游记"]').click()
        time.sleep(10)
        self.switch_window()
        self.switch_iframe()
        time.sleep(1)
        canvas = self.driver.find_element_by_css_selector('canvas')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 640, 710).click().perform()
        time.sleep(2)
        ActionChains(self.driver).move_by_offset(0, -110).click().perform()  # 開始
        for i in range(3):
            time.sleep(0.8)
            ActionChains(self.driver).move_by_offset(0, 0).click().perform()
        time.sleep(1)
        ActionChains(self.driver).move_by_offset(290, 200).click().perform()
        time.sleep(1)
        for j in range(8):
            ActionChains(self.driver).move_by_offset(0, 0).click().perform()  # '-'
        ActionChains(self.driver).move_by_offset(120, 0).click().perform()  # 轉動
        time.sleep(8)
        self.close_window_buffer()

    def goBSPelgame(self):
        lobby_elgame = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[5]/a')  # "电子游艺"下拉式選單
        bsp_elgame = self.driver.find_element_by_css_selector('[ng-click="toBspHtml()"]')  # BSP百胜电子游艺
        ActionChains(self.driver).move_to_element(lobby_elgame).click(bsp_elgame).perform()
        self.into_game_lobby_setting('欧式轮盘')
        # time.sleep(5)
        # self.switch_window()
        # self.switch_iframe()
        # time.sleep(1)
        # self.driver.find_element_by_css_selector('[title="欧式轮盘"]').click()
        check_is_maintain = self.detect_maintain()
        if not check_is_maintain:
            time.sleep(15)
            self.switch_window()
            self.switch_iframe()
            if len(self.driver.find_elements_by_css_selector('.btn.btn-close.close-pop-message')) != 0:
                self.driver.find_element_by_css_selector('.btn.btn-close.close-pop-message').click()  # Close announcement
            time.sleep(4)
            self.switch_window()
            self.switch_iframe()
            self.switch_iframe()
            time.sleep(1)
            canvas = self.driver.find_element_by_css_selector('canvas')
            ActionChains(self.driver).move_to_element_with_offset(canvas, 750, 350).click().perform()
            time.sleep(10)
            bet = self.driver.find_element_by_css_selector('canvas')
            ActionChains(self.driver).move_to_element_with_offset(bet, 1040, 850).click().perform()
            time.sleep(3)
            ActionChains(self.driver).move_by_offset(0, 0).click().perform()
            time.sleep(35)
        self.close_window_buffer()

    def goMWelgame(self):
        lobby_elgame = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[5]/a')  # "棋牌游戏"下拉式選單
        mw_elgame = self.driver.find_element_by_css_selector('[ng-click="toMwHtml()"]')  # MW棋牌
        ActionChains(self.driver).move_to_element(lobby_elgame).click(mw_elgame).perform()
        if self.url == 'http://www.rfben.com/':
            self.into_game_lobby_setting('水浒传')
            self.driver.find_element_by_css_selector('[title="水浒传"]').click()
            time.sleep(15)
            self.switch_window()
            self.switch_iframe()
            time.sleep(1)
            canvas = self.driver.find_element_by_css_selector('canvas')
            ActionChains(self.driver).move_to_element_with_offset(canvas, 635, 435).click().perform()
            time.sleep(1)
            ActionChains(self.driver).move_to_element_with_offset(canvas, 700, 660).click().perform()
            for i in range(5):
                ActionChains(self.driver).move_by_offset(0, 0).click().perform()
            ActionChains(self.driver).move_by_offset(300, 0).click().perform()
        else:
            self.into_game_lobby_setting('好运5扑克')
            time.sleep(15)
            self.switch_window()
            self.switch_iframe()
            time.sleep(1)
            canvas = self.driver.find_element_by_css_selector('canvas')
            ActionChains(self.driver).move_to_element_with_offset(canvas, 1200, 690).click().perform()
            time.sleep(3)
            ActionChains(self.driver).move_by_offset(0, 0).click().perform()
        time.sleep(6)
        self.close_window_buffer()

    '''
    
    彩票游戏
    樂透有可能閉盤，目前解決方式是如果閉盤換另一個盤下注，如果兩個盤都閉盤就會報錯
    
    
    '''
    def goSYlottery(self):
        lobby_lottery = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[7]/a')  # "彩票游戏"下拉式選單
        sy_lottery = self.driver.find_element_by_css_selector('[ng-click="toSyLottery()"]')  # SY双赢彩票
        ActionChains(self.driver).move_to_element(lobby_lottery).click(sy_lottery).perform()
        time.sleep(8)
        self.switch_window()
        self.switch_iframe()
        time.sleep(2)
        try:
            self.driver.find_element_by_xpath('//*[@id="bet_panel"]/table[1]/tbody/tr[3]/td[8]/input').send_keys('5')

        except NoSuchElementException:
            self.driver.switch_to.default_content()
            self.driver.find_element_by_css_selector('#l_GXK3').click()
            time.sleep(1)
            self.switch_iframe()
            self.driver.find_element_by_xpath('//*[@id="bet_panel"]/table[1]/tbody/tr[2]/td[8]/input').send_keys('5')

        except ElementNotInteractableException:
            self.driver.switch_to.default_content()
            self.driver.find_element_by_css_selector('#l_GXK3').click()
            time.sleep(1)
            self.switch_iframe()
            self.driver.find_element_by_xpath('//*[@id="bet_panel"]/table[1]/tbody/tr[2]/td[8]/input').send_keys('5')

        finally:
            time.sleep(0.5)
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()  # 確認
            time.sleep(1)
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()  # 再確認
            time.sleep(8)
            self.close_window_buffer()

    def goIGlottery(self):
        lobby_lottery = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[7]/a')  # "彩票游戏"下拉式選單
        ig_lottery = self.driver.find_element_by_css_selector('[ng-click="toIgLottery()"]')  # IG彩票
        ActionChains(self.driver).move_to_element(lobby_lottery).click(ig_lottery).perform()
        time.sleep(8)
        self.switch_window()
        time.sleep(2)
        try:
            self.driver.find_element_by_xpath('//*[@id="twoGall_Num"]/div[2]/table[2]/tbody/tr[2]/td[1]/table/tbody/tr/td[3]/span/input').send_keys('1')
            time.sleep(1)
            sumbit = self.driver.find_element_by_css_selector('#submit_top')
            self.driver.execute_script("arguments[0].click();", sumbit)  # 確認
            time.sleep(1)
            self.driver.find_element_by_css_selector('.buttondiv.confirmBet_yes').click()

        except ElementNotInteractableException:
            self.driver.find_element_by_css_selector('#t5').click()
            time.sleep(3)
            self.driver.find_elements_by_css_selector('.amount-input[bettype="BIG"]')[0].send_keys('1')
            time.sleep(1)
            sumbit = self.driver.find_element_by_css_selector('#submit_top')
            self.driver.execute_script("arguments[0].click();", sumbit)  # 確認
            time.sleep(1)
            self.driver.find_element_by_css_selector('.buttondiv.confirmBet_yes').click()

        except UnexpectedAlertPresentException:
            print('IG彩票已经关盘')

        finally:
            time.sleep(6)
            self.close_window_buffer()

    def goGPKlotteryvideo(self):
        lobby_lottery = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[7]/a')  # "彩票游戏"下拉式選單
        gpk_lottery = self.driver.find_element_by_css_selector('[ng-click="toGpkLotteryVideo()"]')  # GPK视讯彩票
        ActionChains(self.driver).move_to_element(lobby_lottery).click(gpk_lottery).perform()
        time.sleep(15)
        self.switch_window()
        time.sleep(1)
        try:
            bet = self.driver.find_element_by_xpath(
                '//*[@id="container"]/div/div[2]/div/div/div[2]/div[3]/div[2]/div[1]/div[2]/div[2]/div[2]')
            self.driver.execute_script("arguments[0].click();", bet)
            time.sleep(1)
            checkbox = self.driver.find_element_by_css_selector('.BM-UxnZ.u-M3xGA._3P29b9O')
            self.driver.execute_script("arguments[0].click();", checkbox)

        except NoSuchElementException:
            self.driver.find_elements_by_css_selector('._2q21mRr')[1].click()
            time.sleep(1)
            self.driver.find_elements_by_css_selector('canvas[width="200"]')[1].click()
            time.sleep(1)
            self.driver.find_elements_by_css_selector('._2dIV0IL')[0].click()  # 大
            time.sleep(1)
            checkbox = self.driver.find_element_by_css_selector('.BM-UxnZ.u-M3xGA._3P29b9O')
            self.driver.execute_script("arguments[0].click();", checkbox)

        except:
            maintain = self.driver.find_element_by_css_selector('.maintain').text
            if '系统维护中' in maintain:
                print(maintain)

        finally:
            time.sleep(6)
            self.close_window_buffer()

    def goGPKlottery(self):
        lobby_lottery = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[7]/a')  # "彩票游戏"下拉式選單
        rg_lottery = self.driver.find_element_by_css_selector('[ng-click="toRgLottery()"]')  # 本站彩票
        ActionChains(self.driver).move_to_element(lobby_lottery).click(rg_lottery).perform()
        time.sleep(14)
        self.switch_window()
        self.switch_iframe()
        time.sleep(1)
        if self.url == 'http://www.rfben.com/':
            self.switch_iframe()
            time.sleep(1)
        if len(self.driver.find_elements_by_css_selector('.layui-layer-ico.layui-layer-close.layui-layer-close1')) == 1:
            self.driver.find_element_by_css_selector('.layui-layer-ico.layui-layer-close.layui-layer-close1').click()  # close
        time.sleep(3)
        try:
            self.switch_iframe()
            self.driver.find_element_by_css_selector('#ball_1_11').send_keys('1')
            time.sleep(1)
            self.driver.find_element_by_css_selector('.btn_bet.bg.xiazhu').click()
            time.sleep(1)
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        except:
            self.driver.switch_to.default_content()
            time.sleep(1)
            if self.url == 'http://www.rfben.com/':
                self.switch_iframe()
            time.sleep(1)
            self.switch_iframe()
            time.sleep(1)
            self.driver.find_element_by_css_selector('[data-class-name="六合彩"]').click()
            time.sleep(1)
            self.driver.find_element_by_css_selector('#ball_1_1').send_keys('1')
            time.sleep(1)
            self.driver.find_element_by_css_selector('.btn_bet.bg.xiazhu').click()
            time.sleep(1)
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        finally:
            time.sleep(6)
            self.close_window_buffer()

    def goGPK2lottery(self):
        lobby_lottery = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[7]/a')  # "彩票游戏"下拉式選單
        gpk2_lottery = self.driver.find_element_by_css_selector('[ng-click="toGpk2Lottery()"]')  # GPK2战游彩票
        ActionChains(self.driver).move_to_element(lobby_lottery).click(gpk2_lottery).perform()
        time.sleep(10)
        self.switch_window()
        if self.url != 'http://www.rfben.com/':
            self.switch_iframe()
        time.sleep(1)
        self.driver.find_elements_by_css_selector('.el-submenu')[0].click()  # 時時彩
        time.sleep(2)
        try:
            self.driver.find_elements_by_css_selector('.el-menu-item')[1].click()
            time.sleep(1)
            self.driver.find_elements_by_css_selector('.bottom .btn')[2].click()  # 隨選
            time.sleep(3)
            self.driver.find_elements_by_css_selector('.bottom .btn')[1].click()  # 添加至購注區
            time.sleep(2)
            self.driver.find_element_by_css_selector('.submitBtnInner').click()
        except:
            self.driver.find_elements_by_css_selector('.el-menu-item')[2].click()
            time.sleep(1)
            self.driver.find_elements_by_css_selector('.bottom .btn')[2].click()  # 隨選
            time.sleep(3)
            self.driver.find_elements_by_css_selector('.bottom .btn')[1].click()  # 添加至購注區
            time.sleep(2)
            self.driver.find_element_by_css_selector('.submitBtnInner').click()
        finally:
            time.sleep(6)
            self.close_window_buffer()

    def goGPK3lottery(self):
        lobby_lottery = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[7]/a')  # "彩票游戏"下拉式選單
        gpk3_lottery = self.driver.find_element_by_css_selector('[ng-click="toGpkLotterySport()"]')  # GPK3运彩彩票
        ActionChains(self.driver).move_to_element(lobby_lottery).click(gpk3_lottery).perform()
        time.sleep(14)
        self.switch_window()
        time.sleep(1)
        self.driver.find_elements_by_css_selector('.menuExpandToggle___6R_TS')[1].click()  # 時時彩
        time.sleep(2)
        try:
            self.driver.find_elements_by_css_selector('[data-gameuniqueid="HF_CQSSC"]')[1].click()  # 五分时时彩
            time.sleep(2)
            self.driver.find_elements_by_css_selector('.betCenter_boardActionBtn___1Slzk')[-1].click()  # 隨選
            time.sleep(2)
            self.driver.find_element_by_css_selector('.betCenter_submitBtn___8dKWz').click()  # 投 注
        except:
            self.driver.find_elements_by_css_selector('[data-gameuniqueid="PL5"]')[1].click()  # 排列五
            time.sleep(2)
            self.driver.find_elements_by_css_selector('.betCenter_boardActionBtn___1Slzk')[-1].click()  # 隨選
            time.sleep(2)
            self.driver.find_element_by_css_selector('.betCenter_submitBtn___8dKWz').click()  # 投 注
        finally:
            time.sleep(6)
            self.close_window_buffer()

    # 不合作
    def goLXlottery(self):
        lobby_lottery = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[7]/a')  # "彩票游戏"下拉式選單
        lx_lottery = self.driver.find_element_by_css_selector('[ng-click="toLxLottery()"]')  # LX利鑫彩票
        ActionChains(self.driver).move_to_element(lobby_lottery).click(lx_lottery).perform()
        time.sleep(12)
        self.switch_window()
        try:
            self.driver.find_element_by_css_selector('.btn.Random-btn').click()  # 隨機
            time.sleep(1)
            self.driver.find_element_by_css_selector('.btn.deter-btn').click()  # 確認下注
            time.sleep(1)
            self.driver.find_element_by_css_selector('.ui-dialog-autofocus').click()  # 確定
        except:
            print('LX利鑫彩票閉盤中')
        finally:
            time.sleep(6)
            self.close_window_buffer()

    def go168lottery(self):
        lobby_lottery = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[7]/a')  # "彩票游戏"下拉式選單
        _168_lottery = self.driver.find_element_by_css_selector('[ng-click="toRg168Lottery()"]')  # 168彩票
        ActionChains(self.driver).move_to_element(lobby_lottery).click(_168_lottery).perform()
        check_is_maintain = self.detect_maintain()
        if not check_is_maintain:
            time.sleep(13)
            self.switch_window()
            try:
                closed1 = self.driver.find_element_by_css_selector('#show_time1').text
                closed2 = self.driver.find_element_by_css_selector('#show_time2').text
                if closed1 == '封盘中':
                    self.driver.find_elements_by_css_selector('.item.bg-primary')[1].click()
                elif (closed1 == closed2) == '封盘中':
                    self.driver.find_elements_by_css_selector('.item.bg-primary')[2].click()
                else:
                    self.driver.find_elements_by_css_selector('.item.bg-primary')[0].click()
                time.sleep(3)
                self.driver.find_elements_by_css_selector('.bet-item')[0].click()
                time.sleep(2)
                self.driver.find_element_by_css_selector('[value="投注"]').click()
                time.sleep(2)
                self.driver.find_elements_by_css_selector('.bet-btn')[1].click()
            except NoSuchElementException:
                maintain = self.driver.find_element_by_css_selector('.maintain').text
                if '系统维护中' in maintain:
                    print(maintain)
        time.sleep(6)
        self.close_window_buffer()

    def goLLlottery(self):
        lobby_lottery = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[7]/a')  # "彩票游戏"下拉式選單
        ll_lottery = self.driver.find_element_by_css_selector('[ng-click="toLlLottery()"]')  # LL乐利彩票
        ActionChains(self.driver).move_to_element(lobby_lottery).click(ll_lottery).perform()
        check_is_maintain = self.detect_maintain()
        if not check_is_maintain:
            time.sleep(13)
            self.switch_window()
            time.sleep(1)
            ActionChains(self.driver).move_by_offset(0, 0).click().perform()
            time.sleep(3)
            self.driver.find_elements_by_css_selector('.sub-title')[0].click()  # 时时彩系列
            time.sleep(2)
            self.driver.find_element_by_css_selector('.sub-list-item.FHJLSSC').click()  # 吉利时时彩
            time.sleep(3)
            self.driver.find_elements_by_css_selector('.gametypes-menu-quwei')[0].click()  # 趣味
            time.sleep(3)
            self.driver.find_elements_by_css_selector('[data-param="action=ball&value=0&row=0"]')[1].click()  # 0
            time.sleep(2)
            self.driver.find_element_by_css_selector('#J-fast-submit').click()  # 立即投注
            time.sleep(2)
            self.driver.find_element_by_css_selector('.j-ui-miniwindow.pop.pop.w-auto .pop-control .btn.confirm').click()  # 确 认
        time.sleep(6)
        self.close_window_buffer()

    '''
    
    体育赛事 all-sport
    
    
    '''
    def go3singsport(self):
        lobby_sport = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[6]/a')  # "体育赛事"下拉式選單
        _3sing_sport = self.driver.find_element_by_css_selector('[ng-click="toSingSport()"]')  # 三昇体育
        ActionChains(self.driver).move_to_element(lobby_sport).click(_3sing_sport).perform()
        time.sleep(5)
        self.switch_window()
        self.switch_frame()
        multiple = self.driver.find_element_by_css_selector('[class="a_link_gamemanu a_link_gamemanu_sc8"]')
        self.driver.execute_script("arguments[0].click();", multiple)  # 混合过关
        time.sleep(1)
        self.driver.switch_to.default_content()
        time.sleep(1)
        frame1 = self.driver.find_element_by_css_selector('[name="mainFrame"]')
        self.driver.switch_to.frame(frame1)
        frame2 = self.driver.find_element_by_css_selector('#bettingMatchesMainFrame2')
        self.driver.switch_to.frame(frame2)
        self.switch_frame()
        time.sleep(1)
        try:
            for i in range(0, 25, 5):
                self.driver.find_elements_by_css_selector('td:nth-child(4) table tr td.odds')[i].click()
                time.sleep(0.5)
            time.sleep(1)

        except IndexError:
            self.driver.find_elements_by_css_selector('.date')[0].click()
            time.sleep(5)
            for i in range(0, 25, 5):
                self.driver.find_elements_by_css_selector('td:nth-child(4) table tr td.odds')[i].click()
                time.sleep(0.5)
            time.sleep(1)
        self.driver.switch_to.default_content()
        self.driver.switch_to.frame(frame1)
        frame3 = self.driver.find_element_by_css_selector('[name="bettingLeftFrame"]')
        self.driver.switch_to.frame(frame3)
        self.driver.find_element_by_css_selector('#fr_betamount').send_keys('5')
        time.sleep(1)
        ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        time.sleep(1)
        ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        time.sleep(4)
        self.driver.switch_to.alert.accept()
        time.sleep(3)
        self.close_window_buffer()

    def goSABAsport(self):
        lobby_sport = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[6]/a')  # "体育赛事"下拉式選單
        saba_sport = self.driver.find_element_by_css_selector('[ng-click="toSabaESport()"]')  # 沙巴体育
        ActionChains(self.driver).move_to_element(lobby_sport).click(saba_sport).perform()
        time.sleep(12)
        self.switch_window()
        self.switch_iframe()
        time.sleep(1)
        self.driver.find_element_by_css_selector('.filter.primary').click() # 串關
        time.sleep(6)
        for i in range(1, 26, 6):
            self.driver.find_elements_by_css_selector('.matchArea .multiOdds .odds.subtxt:nth-child(2) .betArea:nth-child(1) span')[i].click()
            time.sleep(1)
        time.sleep(3)
        ActionChains(self.driver).send_keys('10').perform()
        time.sleep(2)
        ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        time.sleep(2)
        ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        time.sleep(8)
        self.close_window_buffer()

    def goCRsport(self):
        lobby_sport = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[6]/a')  # "体育赛事"下拉式選單
        cr_sport = self.driver.find_element_by_css_selector('[ng-click="toIboSport()"]')  # 皇冠体育
        ActionChains(self.driver).move_to_element(lobby_sport).click(cr_sport).perform()
        time.sleep(16)
        self.switch_window()
        frame1 = self.driver.find_element_by_css_selector('#mem_order')
        self.driver.switch_to.frame(frame1)
        self.driver.find_element_by_css_selector('#title_parlay').click()
        time.sleep(10)
        self.driver.switch_to.default_content()
        frame2 = self.driver.find_element_by_css_selector('#body')
        self.driver.switch_to.frame(frame2)
        time.sleep(1)
        self.driver.find_elements_by_css_selector('#showDateSel span')[1].click()
        time.sleep(3)
        try:
            for i in range(0, 7, 2):
                self.driver.find_elements_by_css_selector('tbody.tr_content td:nth-child(4) div span span a')[i].click()
                time.sleep(1)
        except:
            pass
        time.sleep(5)
        ActionChains(self.driver).send_keys('2').perform()
        time.sleep(2)
        ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        time.sleep(2)
        ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        time.sleep(8)
        self.close_window_buffer()

    def goDTsport(self):
        lobby_sport = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[6]/a')  # "体育赛事"下拉式選單
        dt_sport = self.driver.find_element_by_css_selector('[ng-click="toDtESport()"]')  #DT泛亚电竞
        ActionChains(self.driver).move_to_element(lobby_sport).click(dt_sport).perform()
        time.sleep(14)
        self.switch_window()
        time.sleep(2)
        try:
            self.driver.find_elements_by_css_selector('.tab-text')[3].click()  # 串關
            time.sleep(4)
            for i in range(3):
                self.driver.find_elements_by_css_selector('.el-tooltip.bet-label.bet-box.home-box')[int(f'{i}')].click()
                time.sleep(0.8)

            if len(self.driver.find_elements_by_css_selector('.tips-item.error')) != 0:
                self.driver.find_elements_by_css_selector('.el-tooltip.bet-label.bet-box.home-box')[4].click()
                time.sleep(0.8)
                self.driver.find_elements_by_css_selector('.el-tooltip.bet-label.bet-box.home-box')[5].click()
                time.sleep(0.8)
            else:
                pass
            time.sleep(3)
            self.driver.find_elements_by_css_selector('.el-select__caret.el-input__icon.el-icon-arrow-up')[
                1].click()
            time.sleep(2)
            self.driver.find_elements_by_css_selector('.el-select-dropdown__item')[-5].click()
            time.sleep(2)
            self.driver.find_element_by_css_selector('.btn.btn-accept').click()
            time.sleep(8)
            self.driver.find_element_by_css_selector('.btn.btn-accept').click()
        except:
            print('DT电竞未完成下注')
        finally:
            time.sleep(8)
            self.close_window_buffer()

    def goIMsport(self):
        lobby_sport = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[6]/a')  # "体育赛事"下拉式選單
        im_sport = self.driver.find_element_by_css_selector('[ng-click="toImsSport()"]')  # IM体育
        ActionChains(self.driver).move_to_element(lobby_sport).click(im_sport).perform()
        time.sleep(12)
        self.switch_window()
        time.sleep(1)
        self.driver.find_elements_by_css_selector('.tab_label')[2].click()
        time.sleep(5)
        for i in range(2, 9, 2):
            self.driver.find_elements_by_css_selector(f'.event_listing:nth-child({i}) .row_normal:nth-child(1) .event_row:nth-child(1) .event_even:nth-child(3) div:nth-child(1) span')[0].click()
            time.sleep(1)
        time.sleep(3)
        self.driver.find_element_by_css_selector('.placebet_input').send_keys('5')
        time.sleep(3)
        self.driver.find_element_by_css_selector('.btn_placebet.btn').click()
        time.sleep(8)
        self.close_window_buffer()

    def goESBsport(self):
        lobby_sport = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[6]/a')  # "体育赛事"下拉式選單
        esb_sport = self.driver.find_element_by_css_selector('[ng-click="toImSport()"]')  # ESB电竞
        ActionChains(self.driver).move_to_element(lobby_sport).click(esb_sport).perform()
        time.sleep(12)
        self.switch_window()
        time.sleep(3)
        for i in range(5):
            self.driver.find_elements_by_css_selector('.eachItem_gamelist')[i+1].click()
            time.sleep(3)
            try:
                if len(self.driver.find_elements_by_css_selector('.parlayAddButton')) != 0:
                    self.driver.find_elements_by_css_selector('.parlayAddButton')[0].click()
                else:
                    time.sleep(1)
                    self.driver.find_element_by_css_selector('.homeBtn_style').click()
                    self.driver.find_elements_by_css_selector('.eachItem_gamelist')[i+4].click()
            except:
                pass
            time.sleep(1)
            self.driver.find_element_by_css_selector('.homeBtn_style').click()
            time.sleep(2)
        time.sleep(2)
        self.driver.find_element_by_css_selector('.float_button.parlay_button').click()
        time.sleep(2)
        for j in range(3):
            if int(self.driver.find_element_by_css_selector('.market_num_pad').text.strip('+')) >= 4:
                self.driver.find_elements_by_css_selector('.delete_icon.active')[0].click()
                time.sleep(0.5)
        time.sleep(2)
        self.driver.find_element_by_css_selector('.confirmButton').click()
        time.sleep(2)
        self.driver.find_element_by_css_selector('#inputCombo').send_keys('5')
        time.sleep(2)
        self.driver.find_element_by_css_selector('.betButtonBg').click()
        time.sleep(8)
        self.close_window_buffer()

    def goBBINsport(self):
        lobby_sport = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[6]/a')  # "体育赛事"下拉式選單
        bbin_sport = self.driver.find_element_by_css_selector('[ng-click="toBbSport()"]')  # BBIN体育
        ActionChains(self.driver).move_to_element(lobby_sport).click(bbin_sport).perform()
        time.sleep(16)
        self.switch_window()
        self.switch_iframe()
        self.switch_iframe()
        time.sleep(1)
        self.driver.find_element_by_css_selector('[data-period="PC"]').click()  # '过关'
        time.sleep(4)
        self.driver.find_element_by_css_selector('#js-date').click()  # 日期
        time.sleep(1)
        self.driver.find_elements_by_css_selector('.date-choose-block')[1].click()  # 隔天日期
        time.sleep(1)
        self.driver.find_elements_by_css_selector('.js-assign-submit.btn.confirm-btn')[1].click()  # 送出
        time.sleep(2)
        for i in range(0, 10, 2):
            self.driver.find_elements_by_css_selector('.table-normal .js-fadetoggle-content tr td:nth-child(3)')[int(f'{i}')].click()
            time.sleep(0.5)
        time.sleep(3)
        self.driver.find_element_by_css_selector('#js-parlay-total').send_keys('10')
        time.sleep(2)
        self.driver.find_element_by_css_selector('#js-parlay-submit').click()
        time.sleep(2)
        self.driver.switch_to.alert.accept()
        time.sleep(5)
        self.close_window_buffer()

    def goCMDsport(self):
        lobby_sport = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[6]/a')  # "体育赛事"下拉式選單
        cmd_sport = self.driver.find_element_by_css_selector('[ng-click="toCmdSport()"]')  # BBIN体育
        ActionChains(self.driver).move_to_element(lobby_sport).click(cmd_sport).perform()
        time.sleep(20)
        self.switch_window()
        time.sleep(1)
        self.driver.find_element_by_css_selector('[title="混合过关"]').click()  # 混合过关
        time.sleep(8)
        self.driver.find_element_by_css_selector('#date-container li:nth-child(2) input').click()
        time.sleep(3)
        self.driver.find_element_by_css_selector('#date-container li:nth-child(3) input').click()
        time.sleep(3)
        time.sleep(5)
        self.close_window_buffer()

    '''
    
    棋牌游戏
    
    '''
    def goDTboard(self):
        lobby_board = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[2]/a')  # "棋牌游戏"下拉式選單
        dt_board = self.driver.find_element_by_css_selector('[ng-click="toDtBoard()"]')  # DT梦想棋牌
        ActionChains(self.driver).move_to_element(lobby_board).click(dt_board).perform()
        time.sleep(5)
        self.switch_window()
        self.switch_iframe()
        time.sleep(1)
        self.driver.find_element_by_css_selector('[title="三公"]').click()
        time.sleep(12)
        self.switch_window()
        self.switch_iframe()
        time.sleep(1)
        canvas = self.driver.find_element_by_css_selector('#GameCanvas')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 700, 400).click().perform()
        time.sleep(6)
        ActionChains(self.driver).move_by_offset(-165, 100).click().perform()
        time.sleep(26)
        self.close_window_buffer()

    def goTHboard(self):
        lobby_board = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[2]/a')  # "棋牌游戏"下拉式選單
        th_board = self.driver.find_element_by_css_selector('[ng-click="toThBoard()"]')  # TH天豪棋牌
        ActionChains(self.driver).move_to_element(lobby_board).click(th_board).perform()
        time.sleep(5)
        self.switch_window()
        self.switch_iframe()
        time.sleep(1)
        self.driver.find_element_by_css_selector('[title="通比梭哈"]').click()
        time.sleep(12)
        self.switch_window()
        time.sleep(1)
        canvas = self.driver.find_element_by_css_selector('#StageDelegateDiv')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 350, 370).click().perform()
        time.sleep(2)
        ActionChains(self.driver).move_by_offset(250, 0).click().perform()
        time.sleep(26)
        self.driver.close()
        self.switch_window()
        self.close_window_buffer()

    def goFGboard(self):
        lobby_board = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[2]/a')  # "棋牌游戏"下拉式選單
        th_board = self.driver.find_element_by_css_selector('[ng-click="toFsBoard()"]')  # 乐游棋牌
        ActionChains(self.driver).move_to_element(lobby_board).click(th_board).perform()
        time.sleep(5)
        self.switch_window()
        self.switch_iframe()
        time.sleep(1)
        self.driver.find_element_by_css_selector('[title="骰宝"]').click()
        time.sleep(12)
        self.switch_window()
        time.sleep(1)
        canvas = self.driver.find_element_by_css_selector('#StageDelegateDiv')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 350, 370).click().perform()
        time.sleep(2)
        ActionChains(self.driver).move_by_offset(250, 0).click().perform()
        time.sleep(26)
        self.driver.close()
        self.switch_window()
        self.close_window_buffer()

    def goJDBboard(self):
        lobby_board = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[2]/a')  # "棋牌游戏"下拉式選單
        jdb_board = self.driver.find_element_by_css_selector('[ng-click="toJdbBoard()"]')  # 乐游棋牌
        ActionChains(self.driver).move_to_element(lobby_board).click(jdb_board).perform()
        time.sleep(5)
        self.switch_window()
        self.switch_iframe()
        time.sleep(1)
        self.driver.find_element_by_css_selector('[title="JDB通比牛牛"]').click()
        time.sleep(13)
        self.switch_window()
        self.switch_iframe()
        canvas = self.driver.find_elements_by_css_selector('canvas')[1]
        ActionChains(self.driver).move_to_element_with_offset(canvas, 900, 200).click().perform()
        time.sleep(27)
        self.close_window_buffer()

    def goKGboard(self):
        lobby_board = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[2]/a')  # "棋牌游戏"下拉式選單
        kg_board = self.driver.find_element_by_css_selector('[ng-click="toKgHtml()"]')  # KG开元棋牌
        ActionChains(self.driver).move_to_element(lobby_board).click(kg_board).perform()
        time.sleep(5)
        self.switch_window()
        self.switch_iframe()
        time.sleep(1)
        self.driver.find_element_by_css_selector('[title="三公"]').click()
        time.sleep(13)
        self.switch_window()
        canvas = self.driver.find_element_by_css_selector('canvas')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 600, 400).click().perform()
        time.sleep(38)
        self.driver.close()
        self.switch_window()
        self.close_window_buffer()

    def goYGboard(self):
        lobby_board = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[2]/a')  # "棋牌游戏"下拉式選單
        yg_board = self.driver.find_element_by_css_selector('[ng-click="toYgBoard()"]')  # YG云迹棋牌
        ActionChains(self.driver).move_to_element(lobby_board).click(yg_board).perform()
        time.sleep(5)
        self.switch_window()
        self.switch_iframe()
        time.sleep(1)
        self.driver.find_element_by_css_selector('[title="抢庄三公"]').click()
        time.sleep(13)
        self.switch_window()
        self.switch_iframe()
        canvas = self.driver.find_element_by_css_selector('#GameCanvas')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 700, 300).click().perform()
        time.sleep(28)
        self.close_window_buffer()

    def goNWboard(self):
        lobby_board = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[2]/a')  # "棋牌游戏"下拉式選單
        nw_board = self.driver.find_element_by_css_selector('[ng-click="toNwBoard()"]')  # 新世界棋牌
        ActionChains(self.driver).move_to_element(lobby_board).click(nw_board).perform()
        time.sleep(5)
        self.switch_window()
        self.switch_iframe()
        time.sleep(1)
        self.driver.find_element_by_css_selector('[title="三公"]').click()
        time.sleep(13)
        self.switch_window()
        self.switch_iframe()
        canvas = self.driver.find_element_by_css_selector('canvas')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 450, 300).click().perform()
        time.sleep(10)
        ActionChains(self.driver).move_by_offset(50, 480).click().perform()
        for i in range(3):
            ActionChains(self.driver).move_by_offset(0, 0).click().perform()
        time.sleep(3)
        ActionChains(self.driver).move_by_offset(-300, -50).click().perform()
        for j in range(5):
            ActionChains(self.driver).move_by_offset(0, 0).click().perform()
        time.sleep(28)
        self.close_window_buffer()

    def goLEGboard(self):
        lobby_board = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[2]/a')  # "棋牌游戏"下拉式選單
        leg_board = self.driver.find_element_by_css_selector('[ng-click="toLegBoard()"]')  # LEG乐棋牌
        ActionChains(self.driver).move_to_element(lobby_board).click(leg_board).perform()
        time.sleep(5)
        self.switch_window()
        self.switch_iframe()
        time.sleep(1)
        self.driver.find_elements_by_css_selector('#pager li')[3].click()
        time.sleep(2)
        self.driver.find_element_by_css_selector('[title="三公"]').click()
        time.sleep(13)
        self.switch_window()
        self.switch_iframe()
        canvas = self.driver.find_elements_by_css_selector('canvas')[1]
        ActionChains(self.driver).move_to_element_with_offset(canvas, 450, 300).click().perform()
        time.sleep(45)
        self.close_window_buffer()

    def goAPboard(self):
        lobby_board = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[2]/a')  # "棋牌游戏"下拉式選單
        ap_board = self.driver.find_element_by_css_selector('[ng-click="toCity761Html()"]')  # AP爱棋牌
        ActionChains(self.driver).move_to_element(lobby_board).click(ap_board).perform()
        time.sleep(5)
        self.switch_window()
        self.switch_iframe()
        self.driver.find_element_by_css_selector('[title="炸金花"]').click()
        time.sleep(13)
        self.switch_window()
        self.switch_iframe()
        canvas = self.driver.find_element_by_css_selector('#layaContainer')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 600, 300).click().perform()
        time.sleep(10)
        ActionChains(self.driver).move_by_offset(-200, 440).click().perform()
        time.sleep(6)
        self.close_window_buffer()

    def goBSPboard(self):
        if self.url == 'http://www.jp777.net/':
            lobby_fish = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[5]/a')  # "电子游艺"下拉式選單
            GPK_elgame = self.driver.find_element_by_css_selector('[ng-click="toGpkSlot()"]')  # GPK电子游艺
            ActionChains(self.driver).move_to_element(lobby_fish).click(GPK_elgame).perform()
            time.sleep(5)
            self.switch_window()
            time.sleep(1)
            lobby_sport = self.driver.find_element_by_css_selector('.lobbyNav-pager')  # 導航
            ActionChains(self.driver).move_to_element(lobby_sport).click().perform()
            self.driver.find_elements_by_css_selector('.lobbyNav-category [ng-repeat="nav in navInfoList"]')[
                4].click()  # 棋牌
            time.sleep(2)
            bsp_board = self.driver.find_element_by_css_selector('[game-box="BspBoard"]')  # BSP百胜棋牌
            ActionChains(self.driver).move_to_element(bsp_board).click().perform()
            time.sleep(10)
        else :
            lobby_board = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[2]/a')  # "棋牌游戏"下拉式選單
            ap_board = self.driver.find_element_by_css_selector('[ng-click="toCity761Html()"]')  # BSP百胜棋牌
            ActionChains(self.driver).move_to_element(lobby_board).click(ap_board).perform()
            time.sleep(5)
        self.switch_window()
        self.switch_iframe()
        self.driver.find_element_by_css_selector('[title="三公"]').click()
        time.sleep(12)
        self.switch_window()
        self.switch_iframe()
        self.driver.find_element_by_css_selector('.btn.btn-close.close-pop-message').click()
        time.sleep(3)
        self.switch_iframe()
        canvas = self.driver.find_element_by_css_selector('canvas')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 700, 350).click().perform()
        time.sleep(6)
        ActionChains(self.driver).move_by_offset(-250, 70).click().perform()
        time.sleep(5)
        ActionChains(self.driver).move_by_offset(200, 60).click().perform()
        time.sleep(10)
        self.close_window_buffer()

    def goJSboard(self):
        lobby_board = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[2]/a')  # "棋牌游戏"下拉式選單
        leg_board = self.driver.find_element_by_css_selector('[ng-click="toJsBoard()"]')  # JS金龙棋牌
        ActionChains(self.driver).move_to_element(lobby_board).click(leg_board).perform()
        time.sleep(5)
        self.switch_window()
        self.switch_iframe()
        self.driver.find_element_by_css_selector('[title="炸金花"]').click()
        time.sleep(13)
        try:
            canvas = self.driver.find_element_by_id('GameCanvas')
            ActionChains(self.driver).move_to_element_with_offset(canvas, 400, 50).click().perform()  # '電玩'
            time.sleep(1)
            ActionChains(self.driver).move_by_offset(400, 380).click().perform()  # '通比牛牛'
            time.sleep(2)
            ActionChains(self.driver).move_by_offset(-150, -300).click().perform()  # '新手場'
            time.sleep(5)
            ActionChains(self.driver).move_by_offset(350, 670).click().perform()  # 開始遊戲
            time.sleep(10)
            for i in range(10):
                ActionChains(self.driver).move_by_offset(0, 0).click().perform()
                time.sleep(0.8)
            time.sleep(10)
        except:
            pass


        self.switch_window()
        self.switch_iframe()
        canvas = self.driver.find_elements_by_css_selector('canvas')[1]
        ActionChains(self.driver).move_to_element_with_offset(canvas, 450, 300).click().perform()
        time.sleep(45)
        self.close_window_buffer()

    '''
    
    使用者模擬
    
        (1)操作portal站內功能
    
        (2)進入娛樂城後後直接關閉視窗
    
    '''


class UserSimulation(PortalLoginConfig):

    def BetRecoed(self):
        self.driver.find_element_by_css_selector('#account-nav [title="投注记录"]').click()
        time.sleep(3)
        betdetail = self.driver.find_element_by_css_selector('[ng-click="toggleMemberCenterWidth()"]')
        self.driver.execute_script("arguments[0].scrollIntoView();", betdetail)
        time.sleep(5)

    def WithdrawApplication(self):
        try:
            self.driver.find_element_by_css_selector('#account-nav [title="线上取款"]').click()
            time.sleep(2)
            withdrawType = self.driver.find_elements_by_css_selector('[ng-change="payTypeChange()"]')
            if len(withdrawType) != 0:
                self.driver.find_element_by_css_selector('[ng-change="payTypeChange()"]').click()  # 取款方式 - 銀行
            time.sleep(2)
            self.driver.find_element_by_css_selector('#inputAmount').send_keys('1')  # 取款金额
            time.sleep(3)
            self.driver.find_element_by_css_selector('#money-pwd-input').send_keys(self.withdraw_password)  # 取款密码
            time.sleep(1)
            self.driver.find_element_by_css_selector('.btn.btn-submit').click()
            time.sleep(2)
            self.driver.find_element_by_css_selector('[ng-click="ok()"]').click()
            time.sleep(3)
            self.driver.execute_script("window.scrollTo(0,0)")

        except NoSuchElementException:
            time.sleep(3)
            self.driver.execute_script("window.scrollTo(0,0)")

    def Deposit(self):
        self.driver.find_element_by_css_selector('#account-nav [title="线上存款"]').click()
        time.sleep(3)
        self.driver.find_element_by_link_text('公司入款').click()
        self.switch_window()
        time.sleep(3)
        bank_input = self.driver.find_element_by_css_selector('#bank-input')
        ActionChains(self.driver).move_to_element(bank_input).click().perform()
        time.sleep(2)
        ActionChains(self.driver).move_to_element_with_offset(bank_input, 0, 40).click().perform()  # 中國農業銀行
        time.sleep(1)
        self.driver.find_element_by_css_selector('[name="accountId"]').click()
        time.sleep(1)
        self.driver.find_element_by_css_selector('[ng-show="Accounts[depositType].length"]').click()  # 下一步
        time.sleep(2)
        self.driver.find_element_by_css_selector('#amount').send_keys('1')  # 存款金額
        time.sleep(1.5)
        self.driver.find_element_by_css_selector('#depositName').send_keys('yue')  # 存款人姓名
        time.sleep(1.5)
        self.driver.find_elements_by_css_selector('[ng-model="params.type"]')[6].click()  # 其他
        time.sleep(1)
        self.driver.find_elements_by_css_selector('.footer-btn button.ng-binding')[2].click()  # 提交申請
        time.sleep(5)
        self.driver.find_element_by_css_selector('[ng-disabled="isProcessing"]').click()  # 確認
        time.sleep(3)
        self.driver.find_element_by_css_selector('[ng-click="closeWindow()"]').click()  # 關閉視窗
        self.switch_window()
        self.driver.execute_script("window.scrollTo(0,0)")
        time.sleep(3)

    def Transaction(self):
        self.driver.find_element_by_css_selector('#account-nav [title="交易记录"]').click()
        time.sleep(3)
        transaction = self.driver.find_element_by_css_selector('[title="活动专区"]')
        self.driver.execute_script("arguments[0].scrollIntoView();", transaction)
        for i in range(4):
            self.driver.find_elements_by_css_selector('.btn.btn-default.btn-sm')[int('{}'.format(i))].click()
            time.sleep(3)
        self.driver.execute_script("window.scrollTo(0,0)")
        time.sleep(3)

    def ChangeMoneyPassword(self):
        self.driver.find_element_by_css_selector('#account-nav [title="修改取款密码"]').click()
        time.sleep(3)

    def SecurityList_sendEmail(self):
        self.driver.find_element_by_css_selector('#account-nav [title="会员中心"]').click()
        time.sleep(3)
        self.driver.find_element_by_css_selector('[title="站內信件"]').click()
        time.sleep(3)
        openNewMail = self.driver.find_element_by_css_selector('[ng-click="openNewMail()"]')  # 发信
        self.driver.execute_script("arguments[0].scrollIntoView();", openNewMail)
        time.sleep(1)
        openNewMail.click()
        time.sleep(3)
        self.driver.find_element_by_css_selector('.form-control.ng-pristine.ng-invalid.ng-invalid-required').send_keys('TestMessageByYue')  # 主旨
        self.switch_iframe()
        time.sleep(1)
        self.driver.find_element_by_css_selector('body').send_keys('TestByYueBodyMessage')  # 內容
        time.sleep(3)
        self.driver.switch_to.default_content()
        self.driver.find_element_by_css_selector('.btn.btn-blue.pull-right.ng-binding').click()  # 送出
        time.sleep(2.5)
        self.driver.find_element_by_css_selector('[ng-click="ok()"]').click()
        time.sleep(2.5)
        self.driver.execute_script("window.scrollTo(0,0)")
        time.sleep(3)

    def updatingBalance(self):
        time.sleep(1)
        for i in range(3):
            self.driver.find_element_by_css_selector('[ng-show="!updatingBalance"]').click()  # 送出
            time.sleep(0.4)
        time.sleep(5)

'''

純粹進遊戲2秒後關掉
For模擬真實使用者情境測試用，
目前沒在維護
By yue,on 2020/7/7
'''


class entergmae(PortalLoginConfig):

    '''棋排遊戲'''
    def enterKGboard(self):
        lobby_board = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[2]/a')  # "棋牌游戏"下拉式選單
        KG_board = self.driver.find_element_by_css_selector('[ng-click="toKgHtml()"]')  # KG开元棋牌
        ActionChains(self.driver).move_to_element(lobby_board).click(KG_board).perform()
        time.sleep(5)
        self.switch_window()
        self.switch_iframe()
        self.driver.find_element_by_css_selector('[title="KG 抢庄牌九"]').click()
        time.sleep(1)
        self.switch_window()
        self.close_window_buffer()

    def enterRMboard(self):
        lobby_board = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[2]/a')  # "棋牌游戏"下拉式選單
        RM_board = self.driver.find_element_by_css_selector('[ng-click="toDhBoard()"]')  # RM富豪棋牌
        ActionChains(self.driver).move_to_element(lobby_board).click(RM_board).perform()
        time.sleep(5)
        self.switch_window()
        self.switch_iframe()
        self.driver.find_element_by_css_selector('[title="抢庄牌九"]').click()
        time.sleep(1)
        self.switch_window()
        self.close_window_buffer()

    def enterGPKboard(self):
        lobby_board = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[2]/a')  # "棋牌游戏"下拉式選單
        GPK_board = self.driver.find_element_by_css_selector('[ng-click="toGpkBoard()"]')  # GPK棋牌
        ActionChains(self.driver).move_to_element(lobby_board).click(GPK_board).perform()
        time.sleep(5)
        self.switch_window()
        self.switch_iframe()
        self.driver.find_element_by_css_selector('[title="百家樂"]').click()
        time.sleep(1)
        self.switch_window()
        self.close_window_buffer()

    def enterDTboard(self):
        lobby_board = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[2]/a')  # "棋牌游戏"下拉式選單
        DT_board = self.driver.find_element_by_css_selector('[ng-click="toDtBoard()"]')  # DT梦想棋牌
        ActionChains(self.driver).move_to_element(lobby_board).click(DT_board).perform()
        time.sleep(5)
        self.switch_window()
        self.switch_iframe()
        self.driver.find_element_by_css_selector('[title="看三张抢庄牛牛"]').click()
        time.sleep(1)
        self.switch_window()
        self.close_window_buffer()

    def enterAPboard(self):
        lobby_board = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[2]/a')  # "棋牌游戏"下拉式選單
        AP_board = self.driver.find_element_by_css_selector('[ng-click="toCity761Html()"]')  # AP爱棋牌
        ActionChains(self.driver).move_to_element(lobby_board).click(AP_board).perform()
        time.sleep(5)
        self.switch_window()
        self.switch_iframe()
        self.driver.find_element_by_css_selector('[title="AP 二八杠"]').click()
        time.sleep(1)
        self.switch_window()
        self.close_window_buffer()

    def enterVGboard(self):
        lobby_board = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[2]/a')  # "棋牌游戏"下拉式選單
        VG_board = self.driver.find_element_by_css_selector('[ng-click="toVgBoard()"]')  # VG财神棋牌
        ActionChains(self.driver).move_to_element(lobby_board).click(VG_board).perform()
        time.sleep(5)
        self.switch_window()
        self.switch_iframe()
        self.driver.find_element_by_css_selector('[title="血战麻将"]').click()
        time.sleep(1)
        self.switch_window()
        self.close_window_buffer()

    def enterFSboard(self):
        lobby_board = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[2]/a')  # "棋牌游戏"下拉式選單
        FS_board = self.driver.find_element_by_css_selector('[ng-click="toFsBoard()"]')  # 乐游棋牌
        ActionChains(self.driver).move_to_element(lobby_board).click(FS_board).perform()
        time.sleep(5)
        self.switch_window()
        self.switch_iframe()
        self.driver.find_element_by_css_selector('[title="炸金花"]').click()
        time.sleep(1)
        self.switch_window()
        self.close_window_buffer()

    def enterTOGboard(self):
        lobby_board = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[2]/a')  # "棋牌游戏"下拉式選單
        TOG_board = self.driver.find_element_by_css_selector('[ng-click="toTogBoard()"]')  # TOG星球棋牌
        ActionChains(self.driver).move_to_element(lobby_board).click(TOG_board).perform()
        time.sleep(5)
        self.switch_window()
        self.switch_iframe()
        self.driver.find_element_by_css_selector('[title="骰宝"]').click()
        time.sleep(1)
        self.switch_window()
        self.close_window_buffer()

    def enterNWboard(self):
        lobby_board = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[2]/a')  # "棋牌游戏"下拉式選單
        NW_board = self.driver.find_element_by_css_selector('[ng-click="toNwBoard()"]')  # 新世界棋牌
        ActionChains(self.driver).move_to_element(lobby_board).click(NW_board).perform()
        time.sleep(5)
        self.switch_window()
        self.switch_iframe()
        self.driver.find_element_by_css_selector('[title="炸金花"]').click()
        time.sleep(1)
        self.switch_window()
        self.close_window_buffer()

    def enterMWboard(self):
        lobby_board = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[2]/a')  # "棋牌游戏"下拉式選單
        MW_board = self.driver.find_element_by_css_selector('[ng-click="toMwBoard()"]')  # MW棋牌
        ActionChains(self.driver).move_to_element(lobby_board).click(MW_board).perform()
        time.sleep(5)
        self.switch_window()
        self.switch_iframe()
        self.driver.find_element_by_css_selector('[title="好运5扑克"]').click()
        time.sleep(1)
        self.switch_window()
        self.close_window_buffer()

    def enterJSboard(self):
        lobby_board = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[2]/a')  # "棋牌游戏"下拉式選單
        JS_board = self.driver.find_element_by_css_selector('[ng-click="toJsBoard()"]')  # JS金龙棋牌
        ActionChains(self.driver).move_to_element(lobby_board).click(JS_board).perform()
        time.sleep(5)
        self.switch_window()
        self.switch_iframe()
        self.driver.find_element_by_css_selector('[title="对战十三水"]').click()
        time.sleep(1)
        self.switch_window()
        self.close_window_buffer()

    def enterLEGboard(self):
        lobby_board = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[2]/a')  # "棋牌游戏"下拉式選單
        LEG_board = self.driver.find_element_by_css_selector('[ng-click="toLegBoard()"]')  # LEG乐棋牌
        ActionChains(self.driver).move_to_element(lobby_board).click(LEG_board).perform()
        time.sleep(5)
        self.switch_window()
        self.switch_iframe()
        self.driver.find_element_by_css_selector('[title="森林舞会"]').click()
        time.sleep(1)
        self.switch_window()
        self.close_window_buffer()

    def enterJDBboard(self):
        lobby_board = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[2]/a')  # "棋牌游戏"下拉式選單
        JDB_board = self.driver.find_element_by_css_selector('[ng-click="toJdbBoard()"]')  # JDB夺宝棋牌
        ActionChains(self.driver).move_to_element(lobby_board).click(JDB_board).perform()
        time.sleep(5)
        self.switch_window()
        self.switch_iframe()
        self.driver.find_element_by_css_selector('[title="通比牛牛"]').click()
        time.sleep(1)
        self.switch_window()
        self.close_window_buffer()

    def enterGMGboard(self):
        lobby_board = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[2]/a')  # "棋牌游戏"下拉式選單
        GMG_board = self.driver.find_element_by_css_selector('[ng-click="toGmgBoard()"]')  # GMG光明棋牌
        ActionChains(self.driver).move_to_element(lobby_board).click(GMG_board).perform()
        time.sleep(5)
        self.switch_window()
        self.switch_iframe()
        self.driver.find_element_by_css_selector('[title="二人血战"]').click()
        time.sleep(2)
        self.switch_window()
        self.close_window_buffer()

    def enterMTboard(self):
        lobby_board = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[2]/a')  # "棋牌游戏"下拉式選單
        MT_board = self.driver.find_element_by_css_selector('[ng-click="toMtBoard()"]')  # MT美天棋牌
        ActionChains(self.driver).move_to_element(lobby_board).click(MT_board).perform()
        time.sleep(5)
        self.switch_window()
        self.switch_iframe()
        self.driver.find_element_by_css_selector('[title="西游争霸"]').click()
        time.sleep(2)
        self.switch_window()
        self.close_window_buffer()

    def enterSYboard(self):
        lobby_board = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[2]/a')  # "棋牌游戏"下拉式選單
        SY_board = self.driver.find_element_by_css_selector('[ng-click="toIm2Board()"]')  # SY双赢棋牌
        ActionChains(self.driver).move_to_element(lobby_board).click(SY_board).perform()
        time.sleep(5)
        self.switch_window()
        self.switch_iframe()
        self.driver.find_element_by_css_selector('[title="二八杠"]').click()
        time.sleep(2)
        self.switch_window()
        self.close_window_buffer()

    def enterTHboard(self):
        lobby_board = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[2]/a')  # "棋牌游戏"下拉式選單
        TH_board = self.driver.find_element_by_css_selector('[ng-click="toThBoard()"]')  # TH天豪棋牌
        ActionChains(self.driver).move_to_element(lobby_board).click(TH_board).perform()
        time.sleep(5)
        self.switch_window()
        self.switch_iframe()
        self.driver.find_element_by_css_selector('[title="百人牌九"]').click()
        time.sleep(2)
        self.driver.close()
        self.switch_window()
        self.close_window_buffer()

    '''捕魚遊戲'''
    def enterGPKfish(self):
        lobby_fish = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[3]/a')  # "捕鱼游戏"下拉式選單
        GPK_fish = self.driver.find_element_by_css_selector('[game-box="gpk-monopoly"]')  # GPK王者捕鱼
        ActionChains(self.driver).move_to_element(lobby_fish).click(GPK_fish).perform()
        time.sleep(1)
        self.switch_window()
        self.close_window_buffer()

    def enterAPfish(self):
        lobby_fish = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[3]/a')  # "捕鱼游戏"下拉式選單
        AP_fish = self.driver.find_element_by_css_selector('[game-box="ap-fish"]')  # AP李逵劈鱼
        ActionChains(self.driver).move_to_element(lobby_fish).click(AP_fish).perform()
        time.sleep(1)
        self.switch_window()
        self.close_window_buffer()

    def enterJDBfish(self):
        lobby_fish = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[3]/a')  # "捕鱼游戏"下拉式選單
        JDB_fish = self.driver.find_element_by_css_selector('[game-box="jdb-dragon"]')  # JDB龙王捕鱼
        ActionChains(self.driver).move_to_element(lobby_fish).click(JDB_fish).perform()
        time.sleep(1)
        self.switch_window()
        self.close_window_buffer()

    def enterFGfish(self):
        lobby_fish = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[3]/a')  # "捕鱼游戏"下拉式選單
        FG_fish = self.driver.find_element_by_css_selector('[game-box="fg-happy"]')  # FG欢乐捕鱼
        ActionChains(self.driver).move_to_element(lobby_fish).click(FG_fish).perform()
        time.sleep(1)
        self.switch_window()
        self.close_window_buffer()

    def enterPSfish(self):
        lobby_fish = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[3]/a')  # "捕鱼游戏"下拉式選單
        PS_fish = self.driver.find_element_by_css_selector('[game-box="ps-fish"]')  # PS海底捞
        ActionChains(self.driver).move_to_element(lobby_fish).click(PS_fish).perform()
        time.sleep(1)
        self.switch_window()
        self.close_window_buffer()

    def enterTHfish(self):
        lobby_fish = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[3]/a')  # "捕鱼游戏"下拉式選單
        TH_fish = self.driver.find_element_by_css_selector('[game-box="th-bird"]')  # TH捕鸟达人
        ActionChains(self.driver).move_to_element(lobby_fish).click(TH_fish).perform()
        time.sleep(1)
        self.switch_window()
        self.close_window_buffer()

    def enterLEGfish(self):
        lobby_fish = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[3]/a')  # "捕鱼游戏"下拉式選單
        LEG_fish = self.driver.find_element_by_css_selector('[game-box="leg-fish"]')  # LEG捕鱼大作战
        ActionChains(self.driver).move_to_element(lobby_fish).click(LEG_fish).perform()
        time.sleep(1)
        self.switch_window()
        self.close_window_buffer()

    def enterMTfish(self):
        lobby_fish = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[3]/a')  # "捕鱼游戏"下拉式選單
        MT_fish = self.driver.find_element_by_css_selector('[game-box="mt-lee"]')  # MT美天李逵劈鱼
        ActionChains(self.driver).move_to_element(lobby_fish).click(MT_fish).perform()
        time.sleep(1)
        self.switch_window()
        self.close_window_buffer()

    def enterVGfish(self):
        lobby_fish = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[3]/a')  # "捕鱼游戏"下拉式選單
        LEG_fish = self.driver.find_element_by_css_selector('[game-box="vg-fish"]')  # VG龙王捕鱼
        ActionChains(self.driver).move_to_element(lobby_fish).click(LEG_fish).perform()
        time.sleep(1)
        self.switch_window()
        self.close_window_buffer()

    def enterR8fish(self):
        lobby_fish = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[3]/a')  # "捕鱼游戏"下拉式選單
        R8_fish = self.driver.find_element_by_css_selector('[game-box="r8-fish"]')  # R8寻宝捕鱼王
        ActionChains(self.driver).move_to_element(lobby_fish).click(R8_fish).perform()
        time.sleep(1)
        self.switch_window()
        self.close_window_buffer()

    '''真人视讯'''
    def enterBBINlive(self):
        lobby_live = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[4]/a')  # "真人视讯"下拉式選單
        BBIN_live = self.driver.find_element_by_css_selector('[ng-click="toBbLive()"]')  # BBIN真人视讯
        ActionChains(self.driver).move_to_element(lobby_live).click(BBIN_live).perform()
        time.sleep(1)
        self.switch_window()
        self.close_window_buffer()

    def enterAGlive(self):
        lobby_live = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[4]/a')  # "真人视讯"下拉式選單
        AG_live = self.driver.find_element_by_css_selector('[ng-click="toAgLive()"]')  # AG真人视讯
        ActionChains(self.driver).move_to_element(lobby_live).click(AG_live).perform()
        time.sleep(1)
        self.switch_window()
        self.close_window_buffer()

    def enterPTlive(self):
        lobby_live = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[4]/a')  # "真人视讯"下拉式選單
        PT_live = self.driver.find_element_by_css_selector('[ng-click="toBbLive()"]')  # PT真人视讯
        ActionChains(self.driver).move_to_element(lobby_live).click(PT_live).perform()
        time.sleep(1)
        self.switch_window()
        self.close_window_buffer()

    def enterMGlive(self):
        lobby_live = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[4]/a')  # "真人视讯"下拉式選單
        MG_live = self.driver.find_element_by_css_selector('[ng-click="toBbLive()"]')  # MG真人视讯
        ActionChains(self.driver).move_to_element(lobby_live).click(MG_live).perform()
        time.sleep(1)
        self.switch_window()
        self.close_window_buffer()

    def enterABlive(self):
        lobby_live = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[4]/a')  # "真人视讯"下拉式選單
        AB_live = self.driver.find_element_by_css_selector('[ng-click="toAbLive()"]')  # AB真人视讯
        ActionChains(self.driver).move_to_element(lobby_live).click(AB_live).perform()
        time.sleep(1)
        self.switch_window()
        self.close_window_buffer()

    def enterEVOlive(self):
        lobby_live = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[4]/a')  # "真人视讯"下拉式選單
        EVO_live = self.driver.find_element_by_css_selector('[ng-click="toEvoLive()"]')  # EVO真人视讯
        ActionChains(self.driver).move_to_element(lobby_live).click(EVO_live).perform()
        time.sleep(1)
        self.switch_window()
        self.close_window_buffer()

    def enterGDlive(self):
        lobby_live = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[4]/a')  # "真人视讯"下拉式選單
        GD_live = self.driver.find_element_by_css_selector('[ng-click="toGdLive()"]')  # GD真人视讯
        ActionChains(self.driver).move_to_element(lobby_live).click(GD_live).perform()
        time.sleep(1)
        self.switch_window()
        self.close_window_buffer()

    def enterGPKlive(self):
        lobby_live = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[4]/a')  # "真人视讯"下拉式選單
        GPK_live = self.driver.find_element_by_css_selector('[ng-click="toGpkLive()"]')  # GPK真人视讯
        ActionChains(self.driver).move_to_element(lobby_live).click(GPK_live).perform()
        time.sleep(1)
        self.switch_window()
        self.close_window_buffer()

    def enterSBlive(self):
        lobby_live = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[4]/a')  # "真人视讯"下拉式選單
        SB_live = self.driver.find_element_by_css_selector('[ng-click="toSunbetLive()"]')  # 申博真人视讯
        ActionChains(self.driver).move_to_element(lobby_live).click(SB_live).perform()
        time.sleep(1)
        self.switch_window()
        self.close_window_buffer()

    def enterOGlive(self):
        lobby_live = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[4]/a')  # "真人视讯"下拉式選單
        OG_live = self.driver.find_element_by_css_selector('[ng-click="toOgLive()"]')  # OG真人视讯
        ActionChains(self.driver).move_to_element(lobby_live).click(OG_live).perform()
        time.sleep(1)
        self.switch_window()
        self.close_window_buffer()

    '''体育赛事'''
    def enterSABAsport(self):
        lobby_sport = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[6]/a')  # "体育赛事"下拉式選單
        saba_sport = self.driver.find_element_by_css_selector('[ng-click="toSabaGame()"]')  # 沙巴体育
        ActionChains(self.driver).move_to_element(lobby_sport).click(saba_sport).perform()
        time.sleep(1.5)
        self.switch_window()
        self.close_window_buffer()

    def enter3singsport(self):
        lobby_sport = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[6]/a')  # "体育赛事"下拉式選單
        _3sing_sport = self.driver.find_element_by_css_selector('[ng-click="toSingSport()"]')  # 三昇体育
        ActionChains(self.driver).move_to_element(lobby_sport).click(_3sing_sport).perform()
        time.sleep(1.5)
        self.switch_window()
        self.close_window_buffer()

    def enterBBINsport(self):
        lobby_sport = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[6]/a')  # "体育赛事"下拉式選單
        bbin_sport = self.driver.find_element_by_css_selector('[ng-click="toBbSport()"]')  # BBIN体育
        ActionChains(self.driver).move_to_element(lobby_sport).click(bbin_sport).perform()
        time.sleep(1.5)
        self.switch_window()
        self.close_window_buffer()

    def enterCMDsport(self):
        lobby_sport = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[6]/a')  # "体育赛事"下拉式選單
        cmd_sport = self.driver.find_element_by_css_selector('[ng-click="toCmdSport()"]')  # CMD体育
        ActionChains(self.driver).move_to_element(lobby_sport).click(cmd_sport).perform()
        time.sleep(1.5)
        self.switch_window()
        self.close_window_buffer()

    def enterIMsport(self):
        lobby_sport = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[6]/a')  # "体育赛事"下拉式選單
        im_sport = self.driver.find_element_by_css_selector('[ng-click="toImSport()"]')  # IM体育
        ActionChains(self.driver).move_to_element(lobby_sport).click(im_sport).perform()
        time.sleep(1.5)
        self.switch_window()
        self.close_window_buffer()

    def enterCRsport(self):
        lobby_sport = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[6]/a')  # "体育赛事"下拉式選單
        cr_sport = self.driver.find_element_by_css_selector('[ng-click="toIboSport()"]')  # 皇冠体育
        ActionChains(self.driver).move_to_element(lobby_sport).click(cr_sport).perform()
        time.sleep(1.5)
        self.switch_window()
        self.close_window_buffer()

    def enterDTsport(self):
        lobby_sport = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[6]/a')  # "体育赛事"下拉式選單
        dt_sport = self.driver.find_element_by_css_selector('[ng-click="toDtESport()"]')  # DT泛亚电竞
        ActionChains(self.driver).move_to_element(lobby_sport).click(dt_sport).perform()
        time.sleep(1.5)
        self.switch_window()
        self.close_window_buffer()

    '''彩票'''
    def enterGPKlottery(self):
        lobby_lottery = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[7]/a')  # "体育赛事"下拉式選單
        gpk_lottery = self.driver.find_element_by_css_selector('[ng-click="toGpkLotteryVideo()"]')  # GPK视讯彩票
        ActionChains(self.driver).move_to_element(lobby_lottery).click(gpk_lottery).perform()
        time.sleep(1.5)
        self.switch_window()
        self.close_window_buffer()

    def enterGPK2lottery(self):
        lobby_lottery = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[7]/a')  # "体育赛事"下拉式選單
        gpk2_lottery = self.driver.find_element_by_css_selector('[ng-click="toGpk2Lottery()"]')  # GPK2战游彩票
        ActionChains(self.driver).move_to_element(lobby_lottery).click(gpk2_lottery).perform()
        time.sleep(1.5)
        self.switch_window()
        self.close_window_buffer()

    def enterGPK3lottery(self):
        lobby_lottery = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[7]/a')  # "体育赛事"下拉式選單
        gpk3_lottery = self.driver.find_element_by_css_selector('[ng-click="toGpkLotterySport()"]')  # GPK3运彩彩票
        ActionChains(self.driver).move_to_element(lobby_lottery).click(gpk3_lottery).perform()
        time.sleep(1.5)
        self.switch_window()
        self.close_window_buffer()

    def enterLLlottery(self):
        lobby_lottery = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[7]/a')  # "体育赛事"下拉式選單
        ll_lottery = self.driver.find_element_by_css_selector('[ng-click="toLlLottery()"]')  # LL乐利彩票
        ActionChains(self.driver).move_to_element(lobby_lottery).click(ll_lottery).perform()
        time.sleep(1.5)
        self.switch_window()
        self.close_window_buffer()

    def enterLBlottery(self):
        lobby_lottery = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[7]/a')  # "体育赛事"下拉式選單
        lb_lottery = self.driver.find_element_by_css_selector('[ng-click="toLbLottery()"]')  # LB快乐彩
        ActionChains(self.driver).move_to_element(lobby_lottery).click(lb_lottery).perform()
        time.sleep(1.5)
        self.switch_window()
        self.close_window_buffer()

    def enterSYlottery(self):
        lobby_lottery = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[7]/a')  # "体育赛事"下拉式選單
        sy_lottery = self.driver.find_element_by_css_selector('[ng-click="toSyLottery()"]')  # SY双赢彩票
        ActionChains(self.driver).move_to_element(lobby_lottery).click(sy_lottery).perform()
        time.sleep(1.5)
        self.switch_window()
        self.close_window_buffer()

    def enterBBINlottery(self):
        lobby_lottery = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[7]/a')  # "体育赛事"下拉式選單
        bbin_lottery = self.driver.find_element_by_css_selector('[ng-click="toBbLottery()"]')  # BBIN彩票
        ActionChains(self.driver).move_to_element(lobby_lottery).click(bbin_lottery).perform()
        time.sleep(1.5)
        self.switch_window()
        self.close_window_buffer()

    def enterIGlottery(self):
        lobby_lottery = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[7]/a')  # "体育赛事"下拉式選單
        ig_lottery = self.driver.find_element_by_css_selector('[ng-click="toIgLottery()"]')  # IG彩票
        ActionChains(self.driver).move_to_element(lobby_lottery).click(ig_lottery).perform()
        time.sleep(1.5)
        self.switch_window()
        self.close_window_buffer()

