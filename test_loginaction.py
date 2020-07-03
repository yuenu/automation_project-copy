import unittest
import time
import random
from selenium import webdriver
from LoingConfig import PortalLoginConfig, GameHall, UserSimulation ,entergmae
from functionlist import usersimulation_list, game_list, entergame_list, member


class PortalLoginTest(unittest.TestCase):

    def setUp(self):

        """
        AB005 - http://www.fnjtd.com/
        AB006 - http://www.rfben.com/
        AB007 - http://www.jp777.net/
        """
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        url = 'http://www.fnjtd.com/'
        driver = webdriver.Chrome(chrome_options=options)
        driver.set_window_size(1080, 800)
        driver.get(url)

        self.portal = PortalLoginConfig(driver, url)
        self.game = GameHall(driver, url)
        self.user = UserSimulation(driver, url)
        self.entergame = entergmae(driver, url)
        self.filepath = f'./recaptcha/captcha.png'
        self.password = 'a654321'


    def tearDown(self):
        self.portal.driver.close()
        self.portal.driver.quit()

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

    def test_captcha_pass(self):
        # for index in range(len(member)):
        #     member_now = member.pop(0)
        #     print(member_now)
        #     self.portal.isAnnuncement()
        #     self.portal.sendUserInfo(member_now, self.password)
        #     self.portal.parsingPageSourceAndSaveImageSendCode()
        #     self.portal.clickLoginIn()
        #     self.portal.loginFail()
        #     time.sleep(2)
        #     self.getUserSimulation()
        #     time.sleep(2)
        #     self.portal.logout()
        #     time.sleep(6)

        self.portal.login()
        time.sleep(2)

        #  UserSimulation
        # self.user.SecurityList_sendEmail()
        # self.user.BetRecoed()
        # self.user.Deposit()
        # self.user.Transaction()
        # self.user.WithdrawApplication()

        # 彩票 - 確認ok 0622test
        # self.game.goIGlottery()
        # self.game.goSYlottery()
        # self.game.goGPKlotteryvideo()
        # self.game.goGPKlottery()
        # self.game.goGPK2lottery()
        # self.game.goLXlottery()
        # self.game.goGPK3lottery()  # 維修,應該已經不合作

        # 體育(串關定位要研究) 0622test
        # self.game.goSABAsport()
        # self.game.goIMsport()
        # self.game.goESBsport()
        # self.game.go3singsport() #
        # self.game.goBBINsport() #
        # self.game.goCRsport()  # 有時候單沒送出

        # 牌類 0622test
        # self.game.goJDBboard()
        # self.game.goDTboard()
        # self.game.goKGboard()
        # self.game.goYGboard()
        # self.game.goNWboard()
        # self.game.goLEGboard()
        # self.game.goAPboard()
        # self.game.goBSPboard()
        # self.game.goTHboard()  # 沒開場
        # self.game.goJSboard() # 06不要跑

        # 別種定位 , 複雜定位  目前解決不了
        # self.game.goFBGelgame()  # 待修

        # 電子 - 確認ok 0622test
        # 05.06.07都可以

        # self.game.goTOGelgame()
        # self.game.goAEelgame()
        # self.game.goSWelgame()
        # self.game.goSYelgame()
        # self.game.goPTelgame()
        # self.game.goSGelgame()
        # self.game.goPPelgame()
        # self.game.goICGelgame()
        # self.game.goBSPelgame()
        # self.game.goGPKelgame()
        # self.game.goJDBelgame()
        # self.game.goHBelgame()
        # self.game.goDTelgame()
        # self.game.goPGelgame()
        # #
        # self.game.goKAelgame()
        # self.game.goGHelgame()
        # self.game.goR8elgame()
        # self.game.goPNGelgame()
        # self.game.goJSelgame()
        # self.game.goGPK2elgame()
        # self.game.goMTelgame()  # 改掛VPN
        # self.game.goFGargame()  # FG街機維修很久了

        # 捕魚 - 確認ok 0624test
        self.game.goKAfish()
        # self.game.goICGfish()
        # self.game.goAPfish()
        # self.game.goFGfish()
        # self.game.goJDBfish()
        # self.game.goLEGfish()
        # self.game.goVGfish()
        # self.game.goMWfish()
        # self.game.goGPK2fish()
        # self.game.goFGbird()
        # self.game.goGPKfish()
        # self.game.goBSPfish()
        # self.game.goTHfish()

        # self.game.goBBINfish()  # 待修 要兌換分數 麻煩

        # self.game.go07ICGfish()
        # self.game.go07KAfish()
        # self.game.go07BSPfish()
        #須掛VPN
        # self.game.goBGfish()
        # self.game.goCQ9fish()
        # self.game.goMTfish() # 改成需跨區

if __name__ == "__main__":
    unittest.main()