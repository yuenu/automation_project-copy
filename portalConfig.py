import time
import base64
import pytesseract
from bs4 import BeautifulSoup
from selenium import webdriver
from parserImage import idenitfy_img
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementNotInteractableException, NoSuchElementException, \
    UnexpectedAlertPresentException

pytesseract.pytesseract.tesseract_cmd = r'.\Tesseract-OCR\tesseract.exe'


class PortalLoginConfig(object):
    driver = webdriver.Chrome()
    driver.set_window_size(1080, 800)
    driver.get('http://www.fnjtd.com/')
    '''
    AB005 - http://www.fnjtd.com/
    AB006 - http://www.rfben.com/
    AB007 - http://www.jp777.net/
    '''

    def __init__(self):
        self.account = 'yuenu002'
        self.password = 'a123456'
        self.filepath = f'./recaptcha/captcha.png'

    def isAnnuncement(self):
        soup = BeautifulSoup(self.driver.page_source, 'lxml')
        announcement_element = soup.select('div.show#marquee-wrapper')
        announcement2 = soup.find_all(class_='modal-overlay modal-show')
        time.sleep(3)
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
        print(len(device_verification))
        if len(device_verification) != 0:
            self.driver.find_element_by_class_name('fas.fa-times-circle.close').click()
        else:
            pass

    def sendUserInfo(self, account, password):
        time.sleep(1)
        self.driver.find_element_by_id('login_account').send_keys(self.account)
        self.driver.find_element_by_id('login_password').send_keys(self.password)

    def parsingPageSourceAndSaveImageSendCode(self, filepath):
        self.driver.find_element_by_css_selector('#login_code').click()
        time.sleep(2.5)
        soup = BeautifulSoup(self.driver.page_source, 'lxml')
        imgstring = soup.select('#captcha')[0].get('ng-src')[22:]
        imgdata = base64.b64decode(imgstring)
        with open(self.filepath, 'wb') as f:
            f.write(imgdata)

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
                    self.parsingPageSourceAndSaveImageSendCode(self.filepath)
                    self.clickLoginIn()
                    time.sleep(2)

                elif len(alert) == 1 and len(valid) == 1:
                    print('跨區驗證')
                    time.sleep(1)
                    self.driver.find_element_by_xpath('//*[@id="cms-modal-input"]').send_keys('123456')
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
        self.parsingPageSourceAndSaveImageSendCode(self.filepath)
        self.clickLoginIn()
        self.loginFail()
        time.sleep(2)

    def logout(self):
        self.driver.get('http://www.fnjtd.com/Account/SignOut')

    def switch_window(self):
        windows = self.driver.window_handles  # 獲得當前瀏覽器所有視窗
        self.driver.switch_to.window(windows[-1])  # 切換至最新彈窗

    def switch_frame(self):
        frame = self.driver.find_element_by_css_selector('frame')
        self.driver.switch_to.frame(frame)

    def switch_iframe(self):
        frame = self.driver.find_element_by_css_selector('iframe')
        self.driver.switch_to.frame(frame)

    def close_window_buffer(self):
        self.driver.close()
        self.switch_window()
        time.sleep(2)
        self.driver.find_element_by_css_selector('#logo-bg').click()
        time.sleep(3)


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
        lobby_fish = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[3]/a')  # "捕鱼游戏"下拉式選單
        GPK2_fish = self.driver.find_element_by_css_selector('[game-box="gpk2-fish"]')  # GPK2大圣降魔
        ActionChains(self.driver).move_to_element(lobby_fish).click(GPK2_fish).perform()
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
        for j in range(3):
            ActionChains(self.driver).move_by_offset(0, 0).click().perform()  # 發炮
        time.sleep(6)
        self.close_window_buffer()

    def goBSPfish(self):
        lobby_fish = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[3]/a')  # "捕鱼游戏"下拉式選單
        BSP_fish = self.driver.find_element_by_css_selector('[game-box="bsp-fishcannon"]')  # BSP千炮捕鱼王3D
        ActionChains(self.driver).move_to_element(lobby_fish).click(BSP_fish).perform()
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
        self.close_window_buffer()

    def goICGfish(self):
        lobby_fish = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[3]/a')  # "捕鱼游戏"下拉式選單
        ICG_fish = self.driver.find_element_by_css_selector('[game-box="icg-fish"]')  # ICG龙珠捕鱼
        ActionChains(self.driver).move_to_element(lobby_fish).click(ICG_fish).perform()
        time.sleep(10)
        self.switch_window()
        time.sleep(2)
        canvas = self.driver.find_element_by_id('GameCanvas')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 250, 400).click().perform()  # '0.01炮場'
        time.sleep(10)
        for j in range(3):
            ActionChains(self.driver).move_by_offset(0, 0).click().perform()
        time.sleep(5)
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
        lobby_fish = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[3]/a')  # "捕鱼游戏"下拉式選單
        goKAfish = self.driver.find_element_by_css_selector('[game-box="ka-fish"]')  # KA爽爽捕鱼
        ActionChains(self.driver).move_to_element(lobby_fish).click(goKAfish).perform()
        time.sleep(13)
        self.switch_window()
        time.sleep(1)
        canvas = self.driver.find_element_by_id('GameCanvas')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 250, 400).click().perform()  # '0.01炮
        time.sleep(5)
        ActionChains(self.driver).move_by_offset(1000, 0).click().perform()  # 點擊自動射擊
        time.sleep(1)
        ActionChains(self.driver).move_by_offset(0, 0).click().perform()  # click dou dou
        time.sleep(6)
        self.close_window_buffer()

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
        for j in range(2):
            ActionChains(self.driver).move_by_offset(0, 0).click().perform()
            time.sleep(5)
        time.sleep(5)
        self.close_window_buffer()

    def goPGelgame(self):
        lobby_elgame = self.driver.find_element_by_xpath('//*[@id="nav"]/ul/li[5]/a')  # "电子游艺"下拉式選單
        PG_elgame = self.driver.find_element_by_css_selector('[ng-click="toJtnHtml()"]')  # PG电子游艺
        ActionChains(self.driver).move_to_element(lobby_elgame).click(PG_elgame).perform()
        time.sleep(6)
        self.switch_window()
        self.switch_iframe()
        time.sleep(1)
        self.driver.find_element_by_css_selector('[title="冰雪大冲关"]').click()
        time.sleep(8)
        self.switch_window()
        self.switch_iframe()
        canvas = self.driver.find_element_by_id('Cocos2dGameContainer')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 640, 660).click().perform()  # 開始
        time.sleep(1)
        ActionChains(self.driver).move_by_offset(-110, 110).click().perform()  # "減碼按鈕"
        for j in range(8):
            ActionChains(self.driver).move_by_offset(0, 0).click().perform()
        ActionChains(self.driver).move_by_offset(100, 0).click().perform()  # "轉動按鈕"
        for j in range(3):
            ActionChains(self.driver).move_by_offset(0, 0).click().perform()
            time.sleep(4)
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
        ActionChains(self.driver).move_to_element_with_offset(canvas, 230, 685).click().perform()  # '-注'
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
        time.sleep(30)
        self.switch_window()
        self.switch_iframe()
        canvas = self.driver.find_element_by_id('GameLauncher')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 835, 720).click().perform()  # 籌碼
        time.sleep(1)
        ActionChains(self.driver).move_by_offset(-147, -90).click().perform()  # '-'數
        for i in range(5):
            ActionChains(self.driver).move_by_offset(0, 0).click().perform()
            time.sleep(0.2)
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
        time.sleep(15)
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
        time.sleep(12)
        self.switch_window()
        self.switch_iframe()
        canvas = self.driver.find_element_by_id('GameCanvas')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 700, 400).click().perform()  # '新手'
        time.sleep(8)
        ActionChains(self.driver).move_by_offset(270, 180).click().perform()
        time.sleep(1)
        ActionChains(self.driver).move_by_offset(-155, -235).click().perform()
        time.sleep(15)
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
        canvas = self.driver.find_element_by_css_selector('#GameCanvas')
        ActionChains(self.driver).move_to_element_with_offset(canvas, 1200, 780).click().perform()
        time.sleep(3)
        ActionChains(self.driver).move_by_offset(0, 0).click().perform()
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
            self.driver.find_element_by_xpath(
                '//*[@id="twoGall_Num"]/div[2]/table[2]/tbody/tr[2]/td[1]/table/tbody/tr/td[3]/span/input').send_keys(
                '1')

        except ElementNotInteractableException:
            self.driver.find_element_by_css_selector('[onclick="showMenu(1)"]').click()
            time.sleep(1)
            self.driver.find_element_by_xpath(
                '//*[@id="common_div"]/div[2]/table/tbody[2]/tr/td[1]/table/tbody/tr[1]/td[3]/input').send_keys('1')

        finally:
            time.sleep(0.5)
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()  # 確認
            time.sleep(1)
            self.driver.find_element_by_xpath('//*[@id="bodyModule"]/div[24]/div[2]/div/button[2]').click()
            time.sleep(8)
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
        bet = self.driver.find_element_by_xpath(
            f'/html/body/form/div[2]/div/div/table/tbody/tr[6]/td[4]/table/tbody/tr[1]/td[2]/a')
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
            self.driver.find_element_by_xpath(
                f'//*[@id="mainArea"]/div/div[4]/div[2]/div[2]/div[{i}]/div/div[2]/div[3]/div[1]/div/span').click()
            time.sleep(0.5)
        self.driver.find_element_by_css_selector(
            '#mainSection > div > div > div:nth-child(2) > div.betOtherArea > div:nth-child(1) > ul > li.active > div > div.entry > span.content > input').send_keys(
            '10')
        time.sleep(1)
        self.driver.find_element_by_css_selector(
            '#mainSection > div > div > div:nth-child(2) > div.betOtherArea > div.btnArea > button:nth-child(1)').click()
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
        self.driver.find_element_by_css_selector('#account-nav [title="线上取款"]').click()
        time.sleep(2)
        withdrawType = self.driver.find_elements_by_css_selector('[ng-model="applyParams.withdrawType"]')
        if len(withdrawType) == 1:
            withdrawType.click()  # 取款方式 - 銀行
        time.sleep(2)
        self.driver.find_element_by_css_selector('#inputAmount').send_keys('1')  # 取款金额
        time.sleep(3)
        self.driver.find_element_by_css_selector('#money-pwd-input').send_keys('123456')  # 取款密码
        time.sleep(1)
        self.driver.find_element_by_css_selector('.btn.btn-submit').click()
        time.sleep(2)
        self.driver.find_element_by_css_selector('[ng-click="ok()"]').click()
        time.sleep(3)

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
        time.sleep(2)
        self.driver.find_element_by_css_selector('#depositName').send_keys('yue')  # 存款人姓名
        time.sleep(2)
        self.driver.find_elements_by_css_selector('[ng-model="params.type"]')[6].click()  # 其他
        time.sleep(1)
        self.driver.find_elements_by_css_selector('.footer-btn button.ng-binding')[2].click()  # 提交申請
        time.sleep(3)
        self.driver.find_element_by_css_selector('[ng-disabled="isProcessing"]').click()  # 確認
        time.sleep(2)
        self.driver.find_element_by_css_selector('[ng-click="closeWindow()"]').click()  # 關閉視窗
        self.switch_window()
        self.driver.execute_script("window.scrollTo(0,0)")
        time.sleep(3)

    def Transaction(self):
        self.driver.find_element_by_css_selector('#account-nav [title="交易记录"]').click()
        time.sleep(3)
        for i in range(4):
            self.driver.find_elements_by_css_selector('.btn.btn-default.btn-sm')[int('{}'.format(i))].click()
            time.sleep(2)
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
        self.driver.find_element_by_css_selector('.form-control.ng-pristine.ng-invalid.ng-invalid-required').send_keys(
            'TestMessageByYue')  # 主旨
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
