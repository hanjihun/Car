from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

from scrapy.http import TextResponse
from scrapy.exceptions import CloseSpider
from scrapy import signals
import time

from selenium.webdriver.chrome.options import Options

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class SeleniumMiddleware(object):

    def __init__(self, s):
        self.exec_path = s.get('PHANTOMJS_PATH', './phantomjs.exe')

###########################################################

    @classmethod
    def from_crawler(cls, crawler):
        obj = cls(crawler.settings)

        crawler.signals.connect(obj.spider_opened,
                                signal=signals.spider_opened)
        crawler.signals.connect(obj.spider_closed,
                                signal=signals.spider_closed)
        return obj

###########################################################

    def spider_opened(self, spider):
        # try:
        #     self.d = init_driver(self.exec_path)
        # except TimeoutException:
        #     CloseSpider('PhantomJS Timeout Error!!!')
        pass
###########################################################

    def spider_closed(self, spider):
        #self.d.quit()
        pass
###########################################################
    def process_request(self, request, spider):
        if spider.use_selenium:
            try:
                self.d = init_driver(self.exec_path)
            except TimeoutException:
                CloseSpider('PhantomJS Timeout Error!!!')

            print "############################ Received url request from scrapy #####"
            print request.url
            try:        
                self.d.get(request.url)
                #self.d.refresh()
            except TimeoutException as e:
                print "Timeout Error"

            start_time = time.time()

            while time.time() < start_time + 15:
                try:
                    prices = self.d.find_elements_by_xpath('//*[@class="grid_block"]/div')
                except:
                    print "Not found DIV ++++++++++++++++++++++++++++++++"
                    time.sleep(0.5)
                    continue

                try:
                    values = self.d.find_elements_by_xpath('//*[@class="grid_block"]/div/ul/li//*[@class="price ng-binding"]')
                    print "Waiting to load page.."
                    #print len(values)
                    print values[0].text
                    bFound = False
                    for value in values:
                        if value.text and not value.text is "$ 0":
                            print ">>>>>>>>>>>>>>>>>>>>>>>>>>>"
                            bFound = True
                            break
                    if bFound:
                        break
                except:
                    print "Not found VALUE --------------------------------"
                    pass
                
                time.sleep(0.5)                    

                #raise CloseSpider('TIMEOUT ERROR')
            
            # wait = WebDriverWait(self.d, 30)
            # wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".category-breadcrumbs")))
            
            resp = TextResponse(url=self.d.current_url,
                                body=self.d.page_source,
                                encoding='utf-8')
            resp.request = request.copy()
            self.d.quit()
            return resp

###########################################################
###########################################################

def init_driver(path):
    # d = webdriver.PhantomJS(executable_path=path)
    # d.set_page_load_timeout(30)

    chrome_options = Options()
    #chrome_options.add_argument("window-size=1,1")
    #chrome_options.add_argument("window-position=-500,0")
    chrome_path = "../chromedriver.exe"
    d = webdriver.Chrome(chrome_path, chrome_options=chrome_options)
    d.set_page_load_timeout(30)

    
    return d
            
            