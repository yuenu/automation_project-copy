import unittest
from LoingConfig import PortalLoginConfig

class PortalLoginTest(unittest.TestCase):

    def setUp(self):
        self.login = PortalLoginConfig()

    def tearDown(self):
        self.login.driver.get('http://www.fnjtd.com/Account/SignOut')

    def test_captch_pass(self):
        for i in range(100):
            self.login.isAnnuncement()
            self.login.sendUserInfo(self.login.account, self.login.password)
            self.login.parsingPageSourceAndSaveImageSendCode(self.login.filepath)

            self.login.clickLoginIn()
            self.login.loginFail()
            self.login.logout()
            print(f'Complete {i+1} times test!')

        self.assertEqual(self.login.driver.title, 'Stage 测试站')


if __name__ == "__main__":
    unittest.main()
