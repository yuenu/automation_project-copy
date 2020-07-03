import random
from locust import HttpUser, task, between
from functionlist import usersimulation_list, game_list, entergame_list, member
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

pytesseract.pytesseract.tesseract_cmd = r'.\Tesseract-OCR\tesseract.exe'

class QuickstartUser(HttpUser):
    wait_time = between(35, 60)

    def on_start(self):
        driver = webdriver.Chrome()
        driver.set_window_size(1080, 800)
        driver.get('http://www.jp777.net/')
        self.portal = PortalLoginConfig(driver)
        self.game = GameHall(driver)
        self.user = UserSimulation(driver)
        self.entergame = entergmae(driver)
        self.filepath = f'./recaptcha/captcha.png'
        self.password = 'a654321'

    @task(1)
    def test_LoginSimulation(self):
        if member:
            for index in range(len(member)):
                member_now = member.pop(0)
                print(member_now)
                self.portal.isAnnuncement()
                self.portal.sendUserInfo(member_now, self.password)
                self.portal.parsingPageSourceAndSaveImageSendCode()
                self.portal.clickLoginIn()
                self.portal.loginFail()
                time.sleep(2)
                self.getUserSimulation()
                time.sleep(2)
                self.portal.logout()
                time.sleep(6)
        else:
            self.portal.close_window()


    def getUserSimulation(self):
        """
        Portal端使用者模擬做取2~3個
        玩遊戲下注取1~2個
        開啟遊戲1秒後關閉取0~1個
        """

        all_list = []
        user_times = random.randint(0, 2)
        user_randomlist = random.sample(usersimulation_list, user_times)

        game_times = random.randint(2, 3)
        game_randomlist = random.sample(game_list, game_times)

        entergame_times = random.randint(1, 2)
        entergame_randomlist = random.sample(entergame_list, entergame_times)

        all_list.extend(user_randomlist)
        all_list.extend(game_randomlist)
        all_list.extend(entergame_randomlist)
        random.shuffle(all_list)
        print('random all_list:', all_list)
        for action in all_list:
            eval(action)


class PortalLoginConfig(object):

    def __init__(self, driver):
        self.driver = driver
        self.account = 'yuenu002'
        self.password = 'a123456'
        self.filepath = f'./recaptcha/captcha.png'
        self.withdrawpassowd = 'a123456'

    def isAnnuncement(self):
        soup = BeautifulSoup(self.driver.page_source, 'lxml')
        announcement_element = soup.select('div.show#marquee-wrapper')
        announcement2 = soup.find_all(class_='modal-overlay modal-show')
        time.sleep(2)
        if len(announcement_element) != 0:
            self.driver.find_element_by_xpath('//*[@id="marquee"]/footer/span').click()
        else:
            print('None announcement')

        if len(announcement2) != 0:
            self.driver.find_element_by_xpath('/html/body/div[7]/div[2]/div[2]/i').click()

    def device_verification(self):
        soup = BeautifulSoup(self.driver.page_source, 'lxml')
        device_verification = soup.select('i.fas.fa-times-circle.close')
        # 裝置驗證彈窗辨識
        if len(device_verification) != 0:
            self.driver.find_element_by_class_name('fas.fa-times-circle.close').click()
        else:
            pass


    def sendUserInfo(self, account, password):
        time.sleep(1.5)
        self.driver.find_element_by_id('login_account').send_keys(account)
        self.driver.find_element_by_id('login_password').send_keys(password)

    def parsingPageSourceAndSaveImageSendCode(self):
        self.driver.find_element_by_css_selector('#login_code').click()
        time.sleep(2)
        soup = BeautifulSoup(self.driver.page_source, 'lxml')
        imgstring = soup.select('#captcha')[0].get('ng-src')[22:]
        imgdata = base64.b64decode(imgstring)
        try:
            with open(self.filepath, 'wb') as f:
                f.write(imgdata)

        except UnidentifiedImageError:
            self.driver.find_element_by_css_selector('#login_code').click()
            time.sleep(2.5)
            soup = BeautifulSoup(self.driver.page_source, 'lxml')
            imgstring = soup.select('#captcha')[0].get('ng-src')[22:]
            imgdata = base64.b64decode(imgstring)

        captcha_code = idenitfy_img(self.filepath)
        if len(captcha_code) == 4:
            self.driver.find_element_by_css_selector('#login_code').send_keys(captcha_code)
        else:
            print('The cpatcha_code < 4')
            self.driver.find_element_by_css_selector('#login_code').send_keys('0000')

    def clickLoginIn(self):
        self.driver.find_element_by_css_selector('#login-box').click()
        time.sleep(1)
        self.device_verification()
        self.isAnnuncement()

    def loginFail(self):
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
                    self.parsingPageSourceAndSaveImageSendCode()
                    self.clickLoginIn()
                    time.sleep(2)

                elif len(alert) == 1 and len(valid) == 1:
                    print('跨區驗證')
                    time.sleep(1)
                    self.driver.find_element_by_xpath('//*[@id="cms-modal-input"]').send_keys(self.withdrawpassowd)
                    self.driver.find_element_by_css_selector('[ng-click="ok()"]').click()
                    time.sleep(5)
                    self.device_verification()
                    self.isAnnuncement()
                else:
                    break
        else:
            pass

    def login(self):
        self.isAnnuncement()
        self.sendUserInfo(self.account, self.password)
        self.parsingPageSourceAndSaveImageSendCode()
        self.clickLoginIn()
        self.loginFail()
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
        frame = self.driver.find_element_by_css_selector('iframe')
        self.driver.switch_to.frame(frame)

    def close_window(self):
        self.driver.close()
        self.driver.quit()

    def close_window_buffer(self):
        self.driver.close()
        self.switch_window()
        time.sleep(2)
        click_space = self.driver.find_element_by_css_selector('.top-header .wrapper')
        ActionChains(self.driver).move_to_element_with_offset(click_space, 600, 15).click().perform()
        time.sleep(2)


class GameHall(PortalLoginConfig):

    # """捕鱼游戏"""
    def goAPfish(self):
        lobby_fish = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[3]/a')  # "捕鱼游戏"下拉式選單
        AP_fish = self.driver.find_element_by_css_selector('[game-box="ap-jinchan"]')  # AP金蟾捕鱼
        ActionChains(self.driver).move_to_element(lobby_fish).click(AP_fish).perform()
        time.sleep(12)
        self.switch_window()
        time.sleep(1)
        canvas = self.driver.find_element_by_id('layaCanvas')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 600, 300).click().perform()  # 點擊0.1元炮場
        time.sleep(6)
        for j in range(3):
            ActionChains(self.driver).move_by_offset(0, 0).click().perform()  # 發炮
        time.sleep(8)
        self.close_window_buffer()

    def goFGbird(self):
        lobby_fish = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[3]/a')  # "捕鱼游戏"下拉式選單
        FG_bird = self.driver.find_element_by_css_selector('[game-box="fg-bird"]')
        ActionChains(self.driver).move_to_element(lobby_fish).click(FG_bird).perform()
        time.sleep(12)
        self.switch_window()
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
        FG_fish = self.driver.find_element_by_css_selector('[game-box="fg-beauty"]')  # FG美人捕鱼
        ActionChains(self.driver).move_to_element(lobby_fish).click(FG_fish).perform()
        time.sleep(12)
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
        GPK_fish = self.driver.find_element_by_css_selector('[game-box="gpk-monopoly"]')  # GPK王者捕鱼
        ActionChains(self.driver).move_to_element(lobby_fish).click(GPK_fish).perform()
        time.sleep(10)
        self.switch_window()
        time.sleep(1)
        canvas = self.driver.find_element_by_id('layaCanvas')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 250, 400).click().perform()  # 點擊0.1元炮場
        time.sleep(8)
        for j in range(3):
            ActionChains(self.driver).move_by_offset(0, 0).click().perform()  # 發炮
        time.sleep(8)
        self.close_window_buffer()

    def goGPK2fish(self):
        lobby_fish = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[5]/a')  # "电子游艺"下拉式選單
        GPK_elgame = self.driver.find_element_by_css_selector('[ng-click="toGpkSlot()"]')  # GPK电子游艺
        ActionChains(self.driver).move_to_element(lobby_fish).click(GPK_elgame).perform()
        time.sleep(5)
        self.switch_window()
        time.sleep(1)
        lobby_sport = self.driver.find_element_by_css_selector('.lobbyNav-pager')  # 導航
        ActionChains(self.driver).move_to_element(lobby_sport).click().perform()
        self.driver.find_elements_by_css_selector('.lobbyNav-category [ng-repeat="nav in navInfoList"]')[
            6].click()  # 捕魚
        bsp_fish = self.driver.find_element_by_css_selector('[game-box="BspFishCannon"]')  # BSP 千炮捕魚王 3D
        ActionChains(self.driver).move_to_element(bsp_fish).click().perform()
        time.sleep(18)
        self.switch_window()
        time.sleep(1)
        canvas = self.driver.find_element_by_id('view')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 1000, 650).click().perform()  # 點擊進入遊戲
        time.sleep(3)
        ActionChains(self.driver).move_by_offset(-500, -300).click().perform()  # 點擊0.01
        time.sleep(8)
        for j in range(50):
            ActionChains(self.driver).move_by_offset(0, 0).click().perform()  # 發炮
        time.sleep(10)
        self.close_window_buffer()

    def goJDBfish(self):
        lobby_fish = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[3]/a')  # "捕鱼游戏"下拉式選單
        JDB_fish = self.driver.find_element_by_css_selector('[game-box="jdb-dragon"]')  # JDB龙王捕鱼
        ActionChains(self.driver).move_to_element(lobby_fish).click(JDB_fish).perform()
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
        TH_fish = self.driver.find_element_by_css_selector('[game-box="th-toad"]')  # TH金蟾捕鱼
        ActionChains(self.driver).move_to_element(lobby_fish).click(TH_fish).perform()
        time.sleep(12)
        self.switch_window()
        time.sleep(2)
        canvas = self.driver.find_element_by_id('StageDelegateDiv')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 600, 350).click().perform()  # 點擊0.1元炮場
        time.sleep(5)
        for j in range(70):
            ActionChains(self.driver).move_by_offset(0, 0).click().perform()  # 發炮
        time.sleep(5)
        self.close_window_buffer()

    def goLEGfish(self):
        lobby_fish = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[3]/a')  # "捕鱼游戏"下拉式選單
        LEG_fish = self.driver.find_element_by_css_selector('[game-box="leg-fish"]')  # LEG捕鱼大作战
        ActionChains(self.driver).move_to_element(lobby_fish).click(LEG_fish).perform()
        time.sleep(10)
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
        MT_fish = self.driver.find_element_by_css_selector('[game-box="mt-lee"]')  # MT美天李逵劈鱼
        ActionChains(self.driver).move_to_element(lobby_fish).click(MT_fish).perform()
        time.sleep(15)
        self.switch_window()
        time.sleep(2)
        canvas = self.driver.find_element_by_id('layaCanvas')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 250, 450).click().perform()  # 點擊0.1元炮場
        time.sleep(11)
        ActionChains(self.driver).move_by_offset(885, -340).click().perform()  # 點"x"
        time.sleep(1)
        for j in range(2):
            ActionChains(self.driver).move_by_offset(0, 0).click().perform()  # 發炮
        time.sleep(5)
        self.close_window_buffer()

    def goMWfish(self):
        lobby_fish = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[3]/a')  # "捕鱼游戏"下拉式選單
        MW_fish = self.driver.find_element_by_css_selector('[game-box="mw-fish"]')  # MW千炮捕鱼
        ActionChains(self.driver).move_to_element(lobby_fish).click(MW_fish).perform()
        time.sleep(22)
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
        VG_fish = self.driver.find_element_by_css_selector('[game-box="vg-fish"]')  # VG龙王捕鱼
        ActionChains(self.driver).move_to_element(lobby_fish).click(VG_fish).perform()
        time.sleep(12)
        self.switch_window()
        time.sleep(2)
        canvas = self.driver.find_element_by_id('StageDelegateDiv')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 270, 500).click().perform()  # 點擊0.1元炮場
        time.sleep(7)
        for j in range(5):
            ActionChains(self.driver).move_by_offset(0, 0).click().perform()  # 發炮
        time.sleep(6)
        self.close_window_buffer()

    def goBSPfish(self):
        lobby_fish = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[5]/a')  # "电子游艺"下拉式選單
        GPK_elgame = self.driver.find_element_by_css_selector('[ng-click="toGpkSlot()"]')  # GPK电子游艺
        ActionChains(self.driver).move_to_element(lobby_fish).click(GPK_elgame).perform()
        time.sleep(5)
        self.switch_window()
        time.sleep(1)
        lobby_sport = self.driver.find_element_by_css_selector('.lobbyNav-pager')  # 導航
        ActionChains(self.driver).move_to_element(lobby_sport).click().perform()
        self.driver.find_elements_by_css_selector('.lobbyNav-category [ng-repeat="nav in navInfoList"]')[6].click()  # 捕魚
        time.sleep(1)
        bsp_fish = self.driver.find_element_by_css_selector('[game-box="BspFishCannon"]')  # BSP 千炮捕魚王 3D
        ActionChains(self.driver).move_to_element(bsp_fish).click().perform()
        time.sleep(10)
        self.switch_window()
        time.sleep(2)
        canvas = self.driver.find_element_by_css_selector('.home')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 1100, 150).click().perform()  # 'x'
        time.sleep(1)
        ActionChains(self.driver).move_by_offset(-800, 250).click().perform()  # 點擊0.1元炮場
        time.sleep(10)
        ActionChains(self.driver).move_by_offset(280, 400).click().perform()  # 點擊自動
        time.sleep(1)
        ActionChains(self.driver).move_by_offset(0, 0).click().perform()
        time.sleep(5)
        self.driver.close()
        self.switch_window()
        self.driver.close()
        self.switch_window()
        time.sleep(2)
        self.driver.find_element_by_css_selector('#logo-bg').click()
        time.sleep(3)

    def goICGfish(self):
        lobby_fish = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[5]/a')  # "电子游艺"下拉式選單
        GPK_elgame = self.driver.find_element_by_css_selector('[ng-click="toGpkSlot()"]')  # GPK电子游艺
        ActionChains(self.driver).move_to_element(lobby_fish).click(GPK_elgame).perform()
        time.sleep(5)
        self.switch_window()
        time.sleep(1)
        lobby_sport = self.driver.find_element_by_css_selector('.lobbyNav-pager')  # 導航
        ActionChains(self.driver).move_to_element(lobby_sport).click().perform()
        self.driver.find_elements_by_css_selector('.lobbyNav-category [ng-repeat="nav in navInfoList"]')[6].click()  # 捕魚
        time.sleep(1)
        icg_fish = self.driver.find_element_by_css_selector('[game-box="IcgFish"]')  #  ICG 龙珠捕鱼
        ActionChains(self.driver).move_to_element(icg_fish).click().perform()
        time.sleep(10)
        self.switch_window()
        canvas = self.driver.find_element_by_id('GameCanvas')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 250, 400).click().perform()  # '0.01炮場'
        time.sleep(10)
        for j in range(3):
            ActionChains(self.driver).move_by_offset(0, 0).click().perform()
        time.sleep(5)
        self.driver.close()
        self.switch_window()
        self.driver.close()
        self.switch_window()
        time.sleep(2)
        self.driver.find_element_by_css_selector('#logo-bg').click()
        time.sleep(3)

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
        lobby_fish = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[5]/a')  # "电子游艺"下拉式選單
        GPK_elgame = self.driver.find_element_by_css_selector('[ng-click="toGpkSlot()"]')  # GPK电子游艺
        ActionChains(self.driver).move_to_element(lobby_fish).click(GPK_elgame).perform()
        time.sleep(5)
        self.switch_window()
        time.sleep(1)
        lobby_sport = self.driver.find_element_by_css_selector('.lobbyNav-pager')  # 導航
        ActionChains(self.driver).move_to_element(lobby_sport).click().perform()
        self.driver.find_elements_by_css_selector('.lobbyNav-category [ng-repeat="nav in navInfoList"]')[6].click()  # 捕魚
        time.sleep(1)
        ka_fish = self.driver.find_element_by_css_selector('[game-box="KaFish"]')  # ICG 龙珠捕鱼
        ActionChains(self.driver).move_to_element(ka_fish).click().perform()
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
        self.driver.close()
        self.switch_window()
        self.driver.close()
        self.switch_window()
        time.sleep(2)
        self.driver.find_element_by_css_selector('#logo-bg').click()
        time.sleep(3)


    '''
    电子游艺 (AB005)
    '''
    def goAEelgame(self):
        lobby_elgame = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[5]/a')  # "电子游艺"下拉式選單
        AE_elgame = self.driver.find_element_by_css_selector('[ng-click="toAeHtml()"]')  # AE阿米巴电子游艺
        ActionChains(self.driver).move_to_element(lobby_elgame).click(AE_elgame).perform()
        time.sleep(7)
        self.switch_window()
        self.switch_iframe()
        time.sleep(1)
        self.driver.find_element_by_css_selector('[title="一本万利"]').click()
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
        PG_elgame = self.driver.find_element_by_css_selector('[ng-click="toJtnHtml()"]')  # PG电子游艺
        ActionChains(self.driver).move_to_element(lobby_elgame).click(PG_elgame).perform()
        time.sleep(6)
        self.switch_window()
        self.switch_iframe()
        self.driver.find_element_by_css_selector('[title="金猪报财"]').click()
        time.sleep(10)
        self.switch_window()
        self.switch_iframe()
        canvas = self.driver.find_element_by_id('Cocos2dGameContainer')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 640, 660).click().perform()  # 開始
        time.sleep(2)
        ActionChains(self.driver).move_by_offset(90, 90).click().perform()  # "減碼按鈕"
        time.sleep(1)
        ActionChains(self.driver).move_by_offset(100, -270).click().perform()
        for j in range(10):
            ActionChains(self.driver).move_by_offset(0, 0).click().perform()
            time.sleep(0.7)
        ActionChains(self.driver).move_by_offset(-130, 290).click().perform()
        time.sleep(1)
        ActionChains(self.driver).move_by_offset(-70, 0).click().perform()  # "轉動按鈕"
        time.sleep(8)
        self.close_window_buffer()

    #  定位法較特別，暫緩
    # def goSGelgame(self):
    #     lobby_elgame = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[5]/a')  # "电子游艺"下拉式選單
    #     SG_elgame = self.driver.find_element_by_css_selector('[ng-click="toSgFlash()"]')  # SG电子游艺
    #     ActionChains(self.driver).move_to_element(lobby_elgame).click(SG_elgame).perform()
    #     time.sleep(8)
    #     self.switch_window()
    #     self.switch_iframe()
    #     time.sleep(1)
    #     self.driver.find_element_by_css_selector('[title="金鸡"]').click()
    #     time.sleep(8)
    #     self.switch_window()
    #     self.switch_iframe()
    #     canvas = self.driver.find_element_by_id('controlbarH5')
    #     ActionChains(self.driver).move_to_element_with_offset(canvas, 200, 730).click().perform()  # "減碼按鈕"
    #     for j in range(8):
    #         ActionChains(self.driver).move_by_offset(0, 0).click().perform()
    #     ActionChains(self.driver).move_by_offset(920, 0).click().perform()  # "轉動按鈕"
    #     for j in range(2):
    #         ActionChains(self.driver).move_by_offset(0, 0).click().perform()
    #         time.sleep(4)
    #     time.sleep(8)
    #     self.close_window_buffer()

    def goSWelgame(self):
        lobby_elgame = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[5]/a')  # "电子游艺"下拉式選單
        SW_elgame = self.driver.find_element_by_css_selector('[ng-click="toPtsHtml()"]')  # 天风电子游艺
        ActionChains(self.driver).move_to_element(lobby_elgame).click(SW_elgame).perform()
        time.sleep(6)
        self.switch_window()
        self.switch_iframe()
        self.driver.find_element_by_css_selector('[title="天上凤凰"]').click()
        time.sleep(20)
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
        time.sleep(6)
        self.switch_window()
        self.switch_iframe()
        time.sleep(1)
        self.driver.find_element_by_css_selector('[title="大闹天宫"]').click()  # 大闹天宫
        time.sleep(28)
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
        time.sleep(5)
        self.switch_window()
        self.switch_iframe()
        time.sleep(1)
        self.driver.find_element_by_css_selector('[title="秦皇传说"]').click()  # 秦皇传说
        time.sleep(15)
        self.switch_window()
        self.switch_iframe()
        canvas = self.driver.find_element_by_id('GameCanvas')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 1140, 120).click().perform()  # 'x'
        time.sleep(1)
        ActionChains(self.driver).move_by_offset(-700, 560).click().perform()  # 押注
        time.sleep(1)
        ActionChains(self.driver).move_by_offset(150, -70).click().perform()  # 1
        ActionChains(self.driver).move_by_offset(600, 0).click().perform()  # 開始
        time.sleep(6)
        self.close_window_buffer()

    def goGPK2elgame(self):
        lobby_elgame = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[5]/a')  # "电子游艺"下拉式選單
        GPK2_elgame = self.driver.find_element_by_css_selector('[ng-click="toGpk2Html()"]')  # 战游电子游艺
        ActionChains(self.driver).move_to_element(lobby_elgame).click(GPK2_elgame).perform()
        time.sleep(5)
        self.switch_window()
        self.switch_iframe()
        time.sleep(1)
        self.driver.find_element_by_css_selector('[title="海底世界"]').click()
        time.sleep(18)
        self.switch_window()
        self.switch_iframe()
        self.switch_iframe()
        canvas = self.driver.find_element_by_id('GTSLOT0030')
        time.sleep(2)
        ActionChains(self.driver).move_to_element_with_offset(canvas, 640, 674).click().perform()  # '確認'
        time.sleep(1)

        ActionChains(self.driver).move_by_offset(-200, 0).click().perform()
        for i in range(5):
            ActionChains(self.driver).move_by_offset(0, 0).click().perform()
        ActionChains(self.driver).move_by_offset(800, 0).click().perform()  # 開始
        for j in range(3):
            ActionChains(self.driver).move_by_offset(0, 0).click().perform()
            time.sleep(6)
        time.sleep(6)
        self.close_window_buffer()

    def goJSelgame(self):
        lobby_elgame = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[5]/a')  # "电子游艺"下拉式選單
        JS_elgame = self.driver.find_element_by_css_selector('[ng-click="toJsHtml()"]')  # JS金龙电子游艺
        ActionChains(self.driver).move_to_element(lobby_elgame).click(JS_elgame).perform()
        time.sleep(5)
        self.switch_window()
        self.switch_iframe()
        time.sleep(1)
        self.driver.find_element_by_css_selector('[title="水果机"]').click()
        time.sleep(14)
        self.switch_window()
        self.switch_iframe()
        try:
            canvas = self.driver.find_element_by_id('GameCanvas')
            ActionChains(self.driver).move_to_element_with_offset(canvas, 700, 400).click().perform()  # '新手'
            time.sleep(8)
            ActionChains(self.driver).move_by_offset(270, 180).click().perform()
            time.sleep(1)
            ActionChains(self.driver).move_by_offset(-155, -235).click().perform()
            time.sleep(15)
        except NoSuchElementException:
            print('JS電子進行系統維護中')
        self.close_window_buffer()

    def goPTelgame(self):
        lobby_elgame = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[5]/a')  # "电子游艺"下拉式選單
        PT_elgame = self.driver.find_element_by_css_selector('[ng-click="toPtFlash()"]')  # PT电子游艺
        ActionChains(self.driver).move_to_element(lobby_elgame).click(PT_elgame).perform()
        time.sleep(5)
        self.switch_window()
        self.switch_iframe()
        time.sleep(1)
        self.driver.find_element_by_css_selector('[title="招财进宝彩池游戏"]').click()
        time.sleep(12)
        self.switch_window()
        for x in range(4):
            if len(self.driver.find_elements_by_css_selector('#messageBoxButtonYes')) == 1:
                messageBoxButton = self.driver.find_element_by_css_selector('#messageBoxButtonYes')
                ActionChains(self.driver).move_to_element(messageBoxButton).click().perform()
                time.sleep(1)
        self.switch_iframe()
        canvas = self.driver.find_element_by_id('ngm-uicore2-root')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 350, 620).click().perform()  # '確定'
        for i in range(10):
            ActionChains(self.driver).move_by_offset(0, 0).click().perform()
        ActionChains(self.driver).move_by_offset(-150, 0).click().perform()  # '-'
        for j in range(20):
            ActionChains(self.driver).move_by_offset(0, 0).click().perform()
        ActionChains(self.driver).move_by_offset(800, 0).click().perform()  # '旋轉'
        time.sleep(6)
        for k in range(3):
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
        time.sleep(5)
        self.switch_window()
        self.switch_iframe()
        time.sleep(1)
        self.driver.find_element_by_css_selector('[title="齐天大圣"]').click()
        time.sleep(10)
        self.switch_window()
        self.switch_iframe()
        time.sleep(1)
        self.driver.find_element_by_css_selector('.spinButton').click()
        time.sleep(8)
        self.close_window_buffer()

    def goHBelgame(self):
        lobby_elgame = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[5]/a')  # "电子游艺"下拉式選單
        HB_elgame = self.driver.find_element_by_css_selector('[ng-click="toHabaHtml()"]')  # HB电子游艺
        ActionChains(self.driver).move_to_element(lobby_elgame).click(HB_elgame).perform()
        time.sleep(5)
        self.switch_window()
        self.switch_iframe()
        time.sleep(1)
        self.driver.find_element_by_css_selector('[title="公鸡王"]').click()
        time.sleep(12)
        self.switch_window()
        self.switch_iframe()
        time.sleep(1)
        canvas = self.driver.find_element_by_css_selector('canvas')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 650, 750).click().perform()
        time.sleep(8)
        self.close_window_buffer()

    def goSYelgame(self):
        lobby_elgame = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[5]/a')  # "电子游艺"下拉式選單
        SY_elgame = self.driver.find_element_by_css_selector('[ng-click="toIm2Html()"]')  # SY双赢电子游艺
        ActionChains(self.driver).move_to_element(lobby_elgame).click(SY_elgame).perform()
        time.sleep(5)
        self.switch_window()
        self.switch_iframe()
        time.sleep(1)
        self.driver.find_element_by_css_selector('[title="银行大劫案"]').click()
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
        time.sleep(5)
        self.switch_window()
        self.switch_iframe()
        time.sleep(1)
        self.driver.find_element_by_css_selector('[title="失落的王国"]').click()
        time.sleep(10)
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
        time.sleep(5)
        self.switch_window()
        self.switch_iframe()
        time.sleep(1)
        self.driver.find_element_by_css_selector('[title="好运招财猫"]').click()
        time.sleep(14)
        self.switch_window()
        self.switch_iframe()
        self.switch_iframe()
        time.sleep(1)
        canvas = self.driver.find_element_by_css_selector('#pngCasinoGame')
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
        time.sleep(5)
        self.switch_window()
        self.switch_iframe()
        time.sleep(1)
        self.driver.find_element_by_css_selector('[title="皇炫"]').click()
        time.sleep(12)
        self.switch_window()
        self.switch_iframe()
        time.sleep(1)
        canvas = self.driver.find_element_by_css_selector('#canvas')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 740, 550).click().perform()
        time.sleep(3)
        ActionChains(self.driver).move_by_offset(380, 230).click().perform()  # 開始
        time.sleep(8)
        self.close_window_buffer()

    def goICGelgame(self):
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
        time.sleep(1)
        canvas = self.driver.find_element_by_css_selector('#GameCanvas')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 1180, 400).click().perform()
        time.sleep(3)
        time.sleep(8)
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
            self.driver.find_element_by_xpath('//*[@id="l_GXK3"]/span').click()
            time.sleep(1)
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
            time.sleep(0.5)
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()  # 確認
            time.sleep(1)
            self.driver.find_element_by_xpath('//*[@id="bodyModule"]/div[24]/div[2]/div/button[2]').click()

        except NoSuchElementException:
            self.driver.find_element_by_css_selector('[onclick="showMenu(1)"]').click()
            time.sleep(1)
            self.driver.find_element_by_xpath('//*[@id="common_div"]/div[2]/table/tbody[2]/tr/td[1]/table/tbody/tr[1]/td[3]/input').send_keys('1')
            time.sleep(0.5)
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()  # 確認
            time.sleep(1)
            self.driver.find_element_by_xpath('//*[@id="bodyModule"]/div[24]/div[2]/div/button[2]').click()

        finally:
            time.sleep(6)
            self.close_window_buffer()

    '''体育赛事'''
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
        self.switch_window()
        frame1 = self.driver.find_element_by_css_selector('[name="mainFrame"]')
        self.driver.switch_to.frame(frame1)
        frame2 = self.driver.find_element_by_css_selector('#bettingMatchesMainFrame2')
        self.driver.switch_to.frame(frame2)
        self.switch_frame()
        time.sleep(1)
        bet = self.driver.find_element_by_xpath(f'/html/body/form/div[2]/div/div/table/tbody/tr[6]/td[4]/table/tbody/tr[1]/td[2]/a')
        bet.click()
        time.sleep(0.5)
        ActionChains(self.driver).move_to_element_with_offset(bet, 0, 124).click().perform()
        for i in range(3):
            ActionChains(self.driver).move_by_offset(0, 125).click().perform()
            time.sleep(1)
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
        saba_sport = self.driver.find_element_by_css_selector('[ng-click="toSabaGame()"]')  # 沙巴体育
        ActionChains(self.driver).move_to_element(lobby_sport).click(saba_sport).perform()
        time.sleep(10)
        self.switch_window()
        self.switch_iframe()
        for i in range(1, 5):
            self.driver.find_element_by_xpath(f'//*[@id="mainArea"]/div/div[4]/div[2]/div[2]/div[{i}]/div/div[2]/div[3]/div[1]/div/span').click()
            time.sleep(0.5)
        self.driver.find_element_by_css_selector('#mainSection > div > div > div:nth-child(2) > div.betOtherArea > div:nth-child(1) > ul > li.active > div > div.entry > span.content > input').send_keys('10')
        time.sleep(1)
        self.driver.find_element_by_css_selector('#mainSection > div > div > div:nth-child(2) > div.betOtherArea > div.btnArea > button:nth-child(1)').click()
        time.sleep(1)
        self.driver.find_element_by_css_selector('#parlayBetSlipConfirm > div:nth-child(1)')
        time.sleep(8)
        self.driver.close()
        self.switch_window()
        time.sleep(3)

    def goCRsport(self):
        lobby_sport = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[6]/a')  # "体育赛事"下拉式選單
        cr_sport = self.driver.find_element_by_css_selector('[ng-click="toIboSport()"]')  # 皇冠体育
        ActionChains(self.driver).move_to_element(lobby_sport).click(cr_sport).perform()
        time.sleep(14)
        self.switch_window()
        frame1 = self.driver.find_element_by_css_selector('#mem_order')
        self.driver.switch_to.frame(frame1)
        self.driver.find_element_by_css_selector('#title_parlay').click()
        time.sleep(4)
        self.driver.switch_to.default_content()
        frame2 = self.driver.find_element_by_css_selector('#body')
        self.driver.switch_to.frame(frame2)
        self.driver.find_element_by_css_selector('#showDateSel > span.bet_date_color')
        for i in range(3):
            time.sleep(2)
            ActionChains(self.driver).move_by_offset(300, 130).click().perform()  # 串關1
            for j in range(4):
                ActionChains(self.driver).move_by_offset(0, 90).click().perform()  # 串關2.3.4.5
                time.sleep(2)
            ActionChains(self.driver).send_keys('2').perform()
            time.sleep(1)
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            time.sleep(1)
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            time.sleep(5)
            ActionChains(self.driver).move_by_offset(-300, -490).click().perform()  # 在案一次明日
        self.driver.close()
        self.switch_window()
        time.sleep(5)

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
            self.driver.find_element_by_css_selector('#money-pwd-input').send_keys(self.withdrawpassowd)  # 取款密码
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
        time.sleep(2)
        self.driver.find_element_by_css_selector('[ng-click="ok()"]').click()
        time.sleep(2)
        self.driver.execute_script("window.scrollTo(0,0)")
        time.sleep(3)

    def updatingBalance(self):
        time.sleep(1)
        for i in range(3):
            self.driver.find_element_by_css_selector('[ng-show="!updatingBalance"]').click()  # 送出
            time.sleep(0.4)
        time.sleep(5)

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

