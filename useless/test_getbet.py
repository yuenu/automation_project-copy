import unittest
from LoingConfig import LoginConfig
import pyautogui
import time

class PortalLoginTest(unittest.TestCase):

    def setUp(self):
        self.login = LoginConfig()

    def tearDown(self):
        self.login.driver.get('http://www.fnjtd.com/Account/SignOut')

    def test_captch_pass(self):
        self.login.isAnnuncement()
        self.login.sendUserInfo(self.login.account, self.login.password)
        self.login.parsingPageSourceAndSaveImage(self.login.filepath)
        self.login.sendCaptchCode()
        self.login.clickLoginIn()
        self.login.loginFail()
        time.sleep(5)
        self.login.goGPKfish()
        pyautogui.PAUSE = 8
        pyautogui.moveTo(874, 553)  #
        pyautogui.click()
        pyautogui.PAUSE = 3
        pyautogui.click()
        time.sleep(4)


if __name__ == "__main__":
    unittest.main()
