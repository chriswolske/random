import os
import unittest
import sys
import time
import getpass
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime

fp = webdriver.FirefoxProfile()
fp.set_preference("browser.download.folderList",2)
fp.set_preference("browser.download.manager.showWhenStarting",False)
fp.set_preference("browser.download.dir", os.getcwd())
fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/octet-stream")

def suite():
    tests = ['test_loadLoginPage', 'test_RFS', 'test_SF']
    return unittest.TestSuite(map(PrdTest, tests))

class NoLogin(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        #self.driver = webdriver.Ie('c:\\local\\bin\\IEDriverServer.exe')
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        #chrome_options.add_argument("--disable-native-events")
        #self.driver = webdriver.Chrome('c:\\local\\bin\\chromedriver.exe',chrome_options=chrome_options)
        self.driver = webdriver.Firefox()
        #self.driver.implicitly_wait(10)

    @classmethod
    def tearDownClass(self):
        self.driver.close()
        self.driver.quit()

    def loadLoginPage(self):
        br = self.driver
        br.get(self.base_URL)
        elem = br.find_elements(By.XPATH, '//INPUT')[2]
        assert 'Continue to Login' in elem.get_attribute('value')
        elem.click()

    def test_loadLoginPage(self):
        NoLogin.loadLoginPage(self)
        assert self.driver.find_element_by_name('username')
        assert self.driver.find_element_by_name('password')


class PrdTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.web_env = input('Environment:')
        self.username = input('Username: ')
        self.password = getpass.getpass()
        self.base_URL = 'http://'+web_env+'.eginniemae.net'
        self.portal_URL = self.base_URL+'/gmPortal/appmanager/GMportal/GMportalDesktop'
                #self.driver = webdriver.Ie('c:\\local\\bin\\IEDriverServer.exe')
        self.driver = webdriver.Chrome('c:\\local\\bin\\chromedriver.exe')
        #self.driver = webdriver.Firefox()
        #self.driver.implicitly_wait(10)

    @classmethod
    def tearDownClass(self):
        self.driver.close()
        self.driver.quit()

    def logout(self):
        if self.driver.find_elements_by_id('C_t_32002') == []:
            self.driver.find_element_by_link_text('Logout').click()
            time.sleep(.5)
            self.driver.switch_to.alert.accept()

    def login(self):
        NoLogin.loadLoginPage(self)
        br = self.driver
        br.find_element_by_name('username').send_keys(self.username)
        br.find_element_by_name('password').send_keys(self.password)
        br.find_element_by_name('password').send_keys(Keys.RETURN)
        #OVERRIDE if I'm still logged in from last time, or somewhere else
        try:
            br.find_element_by_xpath("//input[@type='button']").click()
        except:
            pass

    def setUp(self):
        PrdTest.login(self)

    def tearDown(self):
        # should be 'logout'
        PrdTest.logout(self)

    def test_02_login(self):
        #setUp calls PrdTest.login automatically
        assert self.driver.find_element_by_xpath('//span[contains(.,"Welcome To Ginnie Mae Portal")]')

    def test_smokeWHFIT(self):
        PrdTest.test_02_login(self)
        br=self.driver
        rfsElem = br.find_elements_by_xpath("//*[contains(text(), 'RFS')]")[0]
        ActionChains(br).move_to_element(rfsElem).perform()
        br.find_element_by_link_text('Widely Held Fixed Investment Trust (WHFIT)').click()
        assert br.find_element_by_id('whfit_portlet').text == 'Widely Held Fixed Investment Trust (WHFIT)'
        #br.find_element_by_id('ctl00_Main_WHFITMenuControl1_lnkScreens').click()


        # not sure what's going on; I never completed a fist pass of this test case
        ###'br.find_elements_by_xpath("//*[contains(text(), 'Issuer')]")[0].click()
        ###br.find_element_by_link_text('Monthly Reporting').click()
        ###time.sleep(5)


    def test_RFSMenu(self):
        br = self.driver
        # this section is ripe for cleanup; can be accomplished with more
        # fuzzy lookups, and should be no need to explicitly identify the portlet
        # that needs to be used to find the name/string...
        for link in [('Exception Feedback', 'paef_portlet'),
                    ('Pool Accounting - Single Family', 'pasf_portlet'),
                    ('Pool Accounting - Multifamily', 'pamf_portlet'),
                    ('Independent Public Accountant (IPA)', 'ipa_portlet'),
                    ('Matching and Suspense (MAS)', 'mas_portlet'),
                    ('Servicemembers Civil Relief Act (SCRA)', 'scra_portlet'),
                    ('Custodial Account Verification System (CAVS)',
                        'cavs_portlet'),
                    ('Ginnie Mae Portfolio Analysis Database System (GPADS)',
                        'gpads_portlet'),
                    ('RFS Administration (ADMIN)', 'adm_portlet'),
                    ('e-Notification (eN)', 'en_portlet'),
                    # HRA is an exception -- doesn't use the same page name
                        # as link name
                    #('HMBS Reporting and Administration (HRA)', 'hra_portlet'),
                    ('Widely Held Fixed Investment Trust (WHFIT)',
                        'whfit_portlet'),
                    ('Data Analysis & Reporting Tool (DART)', 'dart_portlet'),
                    # IOPP exception - it spawns a new window...
                    #('Issuer Operational Performance Profile (IOPP)',
                        #'iopp_portlet')
                    ]:
            rfsElem = br.find_elements_by_xpath("//*[contains(text(), 'RFS')]")[0]
            ActionChains(br).move_to_element(rfsElem).perform()
            br.find_element_by_link_text(link[0]).click()
            assert br.find_element_by_id(link[1]).text == link[0]
            time.sleep(.2)
        PrdTest.loadPortlet(self, 'HRA')
        assert 'HMBS' in br.find_element_by_id('hra_portlet').text
        PrdTest.loadPortlet(self, 'IOPP')
        time.sleep(3)
        br.switch_to.window(br.window_handles[1]) # popup window should be 2nd
        br.close()
        br.switch_to.window(br.window_handles[0]) # back to parent

    def loadPortlet(self, portlet):
        br=self.driver
        rfsElem = br.find_elements_by_xpath("//*[contains(text(), 'RFS')]")[0]
        #time.sleep(1)
        ActionChains(br).move_to_element(rfsElem).perform()
        #actions.click(portlet)
        #actions.perform()
        #time.sleep(1)
        self.driver.find_element_by_partial_link_text(portlet).click()

    def test_singleFamily(self):
        br = self.driver
        PrdTest.loadPortlet('Exception Feedback')
        assert br.find_element_by_id('paef_portlet').text == 'Exception Feedback'
        #br.find_element_by_xpath('//a[contains(text(), "RFS")]')

    def test_IOPP(self):
        br = self.driver
        PrdTest.loadPortlet(self,'IOPP')
        time.sleep(3) #replace with WebDriverWait...TBD
        br.switch_to.window(br.window_handles[1]) # popup window should be 2nd
        assert br.title == 'Home'
        assert br.find_element_by_xpath("//span[@class='x264']").text == \
            "ISSUER OPERATIONAL PERFORMANCE PROFILE"
        #time.sleep(2)
        br.find_element_by_id('T:oc_5796965954region1:dc0:it1::content').send_keys('3355')
        br.find_element_by_id('T:oc_5796965954region1:dc0:searchBtn').click()
        time.sleep(2)
        br.find_element_by_link_text('3355').click()
        # need to pause to visually validate?
        #wait = WebDriverWait(br, 60)
        #elem = wait.until(EC.presence_of_element_located((By.ID,'SWF_MyXCelsius')))
        time.sleep(1)
        br.switch_to.frame(br.find_elements_by_xpath("//iframe")[1])
        elem = WebDriverWait(br,60).until(EC.presence_of_element_located((By.XPATH, "//body[@class='yui-skin-sam']")))
        #elem = br.find_element_by_xpath("//body[@class='yui-skin-sam']")
        input('IOPP Summary tab?')
        br.find_element_by_link_text('Issuances Profile').click()
        elem = WebDriverWait(br, 60).until(
            EC.presence_of_element_located(
                (By.XPATH, "//span[@class=' nwt db']")))
        input('IOPP Issuances Profile?')

        assert "Wells Fargo" in br.find_element_by_xpath(
            '//span[@class=" nwt db"]').text
        br.find_element_by_link_text('Custom Settings').click()
        input('IOPP Custom Settings?')
        #assert br.find_element_by_xpath("//span[@class='x265']").text == \
        #    "My Portfolio"
        br.close()
        br.switch_to.window(br.window_handles[0])  # back to parent


class DisclosureTests(unittest.TestCase):
    logging.basicConfig(filename='disclosure_test.log', level=logging.INFO,
        format='%(asctime)s %(message)s')

    @classmethod
    def setUpClass(self):
        #self.driver = webdriver.Ie('c:\\local\\bin\\IEDriverServer.exe')
        #self.driver = webdriver.Chrome('c:\\local\\bin\\chromedriver.exe')
        self.driver = webdriver.Firefox(firefox_profile=fp)
        self.driver.get('http://duckduckgo.com')

    def setUp(self):
        self.startTime = time.time()

    @classmethod
    def tearDownClass(self):
        self.driver.close()
        self.driver.quit()

    def tearDown(self):
        if self._resultForDoCleanups.errors:
            status = "Error(s)"
        elif self._resultForDoCleanups.failures:
            status = "Failure(s)"
        elif self._resultForDoCleanups.wasSuccessful:
            status = "Success"
        logging.info('%s: %.2f %s' % (self.id()[9:],
                time.time() - self.startTime, status))

    def waitAndClick(self, elem):
        WebDriverWait(self.driver,5).until(EC.presence_of_element_located((By.LINK_TEXT, elem)))
        self.driver.find_element_by_link_text(elem).click()

    def test_simple(self):
        br = self.driver
        br.get('http://www.ginniemae.gov')
        #DisclosureTests.waitAndClick(self, 'Doing Business with Ginnie Mae')
	#br.find_element_by_link_text('Doing Business with Ginnie Mae').click()
	#ActionChains(br).move_to_element(elem).perform()
	elem = br.find_element_by_link_text('Doing Business with Ginnie Mae')
        print(elem.text)
        elem.click()
	ActionChains(br).move_to_element(elem).perform()
        ActionChains(br).move_to_element(elem).perform()
        DisclosureTests.waitAndClick(self, 'Investor Resources')
	time.sleep(3)

    def xtest_Search(self):
        br = self.driver
        br.get('http://www.ginniemae.gov')
        assert br.title == 'Ginnie Mae'
        #DisclosureTests.waitAndClick(self, 'Doing Business with Ginnie Mae')
        br.find_element_by_link_text('Doing Business with Ginnie Mae').click()
	DisclosureTests.waitAndClick(self, 'Investor Resources')
        DisclosureTests.waitAndClick(self, 'Ginnie Mae MBS Disclosure Data')
        DisclosureTests.waitAndClick(self, 'MBS Disclosure Data Search')
        br.find_element_by_id('searchInput').send_keys('138613')
        br.find_element_by_name('buttonSubmit').click()
        assert br.find_element_by_xpath("//td[contains(.,'Wells Fargo')]")
        DisclosureTests.waitAndClick(self, 'Home')
        assert br.find_element_by_xpath("//td[contains(.,'Who we are. What we do.')]")

    def xtest_BulkDownload(self):
        br = self.driver
        br.get('http://www.ginniemae.gov')
        assert br.title == 'Ginnie Mae'
        DisclosureTests.waitAndClick(self, 'Home')
        DisclosureTests.waitAndClick(self, 'Doing Business with Ginnie Mae')
        DisclosureTests.waitAndClick(self, 'Investor Resources')
        DisclosureTests.waitAndClick(self, 'Ginnie Mae MBS Disclosure Data')
        DisclosureTests.waitAndClick(self, 'Disclosure Data Download')
        br.find_element_by_id('ctl00_m_g_0617d90c_80f4_4a8c_9b51_989a75ad0a8a_ctl00_tbEmailAddress').send_keys('cwolske@deloitte.com')
        br.find_element_by_name('ctl00$m$g_0617d90c_80f4_4a8c_9b51_989a75ad0a8a$ctl00$btnQueryEmail').click()
        br.find_element_by_id('ctl00_m_g_0617d90c_80f4_4a8c_9b51_989a75ad0a8a_ctl00_tbAnswer').send_keys('Breck')
        br.find_element_by_id('ctl00_m_g_0617d90c_80f4_4a8c_9b51_989a75ad0a8a_ctl00_btnAnswerSecret').click()
        DisclosureTests.waitAndClick(self, 'daily.txt')
        DisclosureTests.waitAndClick(self, 'Home')
        assert br.find_element_by_xpath("//td[contains(.,'Who we are. What we do.')]")

if __name__ == '__main__':
    unittest.main()
