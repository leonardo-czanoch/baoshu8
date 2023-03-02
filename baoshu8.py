import threading
import logging
import random
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located

# rules:
#   only one reply allowed for every 1 minute
#   only 9 replies allowed for every 1 hour
class Baoshu8(threading.Thread):
    def __init__(self, param, msg_array):
        super(Baoshu8, self).__init__()

        self.POST_STR_LIMIT = 10
        self.POST_INTERVAL  = 60 * 7

        self.TIME_LONG = 15
        self.TIME_NORM = 3

        self.ADDR_HOME        = "http://www.baoshu8.com"
        self.ADDR_GOSSIP      = "https://www.baoshu8.com/forum-56-1.html"
        self.ADDR_EA_SERIE    = "https://www.baoshu8.com/forum-289-1.html"
        self.ADDR_CHECK_IN    = "https://www.baoshu8.com/dsu_paulsign-sign.html"
        self.SECTION_ADDR = {
            "baidupan_movie": "https://www.baoshu8.com/forum-260-1.html",  #baidu pan movie
            "baidupan_series": "https://www.baoshu8.com/forum-265-1.html",  #baidu pan series
            "baidupan_comic": "https://www.baoshu8.com/forum-267-1.html",  #baidu pan comic
            "baidupan_documentary": "https://www.baoshu8.com/forum-268-1.html",  #baidu pan documentary
            "baidupan_classic": "https://www.baoshu8.com/forum-279-1.html"   #baidu pan classic movie
        }
        self.REPLY_STRS = [
        "这个资源我找很长时间了,真不错在抱书吧百度云论坛找到了,谢谢分享!",
        "难得这么快就有了,期待很长时间了.",
        "抱书吧百度云资源真不错,分享的资源又快又完整,继续保持啦!",
        "我的天,这么快就有了,抱书吧百度网盘论坛真的名副其实.",
        "资源更新真是快啊，其他网站都没有，抱书吧云论坛就有了,真不错.",
        "谢谢亲的分享，这个资源很不错，我挺喜欢的，在这里我找到不少好东西。",
        "还不错，资源很完整，没想到这么快就有资源下载了，抱走先。",
        "谢谢大大的分享,我等穷人就全靠你了，现在很难有这么好的网盘资源下载了。",
        "3Q，太好了，终于找到这个资源了，话说我找了很久，抱书吧资源真丰富。",
        "非常感谢，这个资源很难找,没想到这里就有，速度下载。"
        ]
        self.XPATH_LOGGED_INFO         = f"//div[@id='um']//a[text()='{self.USERNAME}']"
        self.XPATH_CREDIT              = "//a[@id='extcreditmenu']"
        self.XPATH_COIN                = "//div[@id='extcreditmenu_menu']//span[@id='hcredit_2']"
        self.XPATH_ALERT               = "//div[@id='messagetext']/p"

        self.XPATH_SECTION_THREAD_LIST = "//tbody[contains(@id, 'normalthread')]"
        self.XPATH_SECTION_NEXTPAGE    = "//span[@id='fd_page_bottom']//a[@class='nxt']"

        self.XPATH_THREAD_SECTION      = "//div[@id='ct']/div[2]/div[1]/div[1]/h1/a"
        self.XPATH_THREAD_POST_LIST    = "//div[@id='postlist']"
        self.XPATH_THREAD_FORM           = "//form[@id='fastpostform']"
        self.XPATH_THREAD_POSTAREA     = "//textarea[@id='fastpostmessage']"
        self.XPATH_THREAD_SUBMIT       = "//button[@id='fastpostsubmit']"

        self.XPATH_CHECK_IN_FORM       = "//form[@id='qiandao']"
        self.XPATH_CHECK_IN_MOODS      = "//input[@name='qdxq']/../li"
        self.XPATH_CHECK_IN_SAY        = "//input[@id='todaysay']"
        self.XPATH_CHECK_IN_MSG        = "//div[@id='ct']/div/h1"

        # configuring each autopost thread
        self.msg_array = msg_array
        self.USERNAME = param["userId"]
        self.PASSWORD = param["password"]
        self.POST_NUM_LIMIT = int(param["numOfPost"])
        self.SECTIONS = [self.SECTION_ADDR[section] for section in param["sections"] if param["sections"][section]]
        self.ALGORITHM = param["algorithm"]
        self.NEED_CHECKIN = param["checkin"]

        self.number_of_replied_posts = 0

        self.logger = logging.getLogger(self.USERNAME)
        logging.basicConfig(level=logging.INFO, format="%(asctime)s: %(name)s: %(levelname)s: %(message)s")

        chrome_options = Options()
        chrome_options.headless = True
        service = Service(executable_path="./chromedriver")
        self.driver = webdriver.Chrome(options=chrome_options, service=service)

    def __del__(self):
        if self.driver:
            self.driver.close()

    def __send_msg(self, msg):
        self.msg_array.append({ "id": len(self.msg_array), "msg": f"{time.strftime('%Y-%m-%d %X')} - {msg}" })
        self.logger.info(msg)

    def __waitFor(self, xpath, time=None):
        return WebDriverWait(self.driver, timeout=time if time else self.TIME_NORM).until(presence_of_element_located((By.XPATH, xpath)))

    def __get_coin_number(self):
        creditElem = self.driver.find_element(By.XPATH, self.XPATH_CREDIT)
        ActionChains(self.driver).move_to_element(creditElem).perform()

        self.__waitFor(self.XPATH_COIN)
        coins = int(self.driver.find_element(By.XPATH, self.XPATH_COIN).text)
        self.logger.info(f"current coin # is :{coins}")
        return coins

    def __logPost(self, post):
        self.logger.info(f"{post['section']} - {post['tar']}{post['subject']} - {post['author']} {'replied' if post['replied'] else 'unreplied'}")

    def __getPosts(self):
        posts = []
        threads = self.driver.find_elements(By.XPATH, self.XPATH_SECTION_THREAD_LIST)
        for thread in threads:
            post = {}
            post["section"]    = self.driver.find_element(By.XPATH, self.XPATH_THREAD_SECTION).text

            tars = thread.find_elements(By.XPATH, "./tr/th/em")
            post["tar"] = tars[0].text if len(tars) > 0 else ""

            elem               = thread.find_element(By.XPATH, "./tr/th/a[3]")
            post["subject"]    = elem.text
            post["link"]       = elem.get_attribute("href")

            post["author"]     = thread.find_element(By.XPATH, "./tr/td[2]/cite").text
            post["lastPoster"] = thread.find_element(By.XPATH, "./tr/td[4]/cite").text
            post["replied"]    = False
            
            posts.append(post)
        return posts
    
    def __reply_to_post(self, post):
        isSuccess = False
        self.driver.get(f"{post['link']}")

        coinsBeforePost = self.__get_coin_number()

        self.__waitFor(self.XPATH_THREAD_POST_LIST)
        form =  self.driver.find_element(By.XPATH, self.XPATH_THREAD_FORM)
        form.find_element(By.XPATH, self.XPATH_THREAD_POSTAREA).send_keys(self.REPLY_STRS[((self.number_of_replied_posts + 1) % self.POST_STR_LIMIT)])
        form.find_element(By.XPATH, self.XPATH_THREAD_SUBMIT).click()

        coinsAfterPost = self.__get_coin_number()
        isSuccess = coinsBeforePost < coinsAfterPost

        if isSuccess:
            post["replied"] = True
            self.number_of_replied_posts += 1
        else:
            alert = self.driver.find_elements(By.XPATH, self.XPATH_ALERT)
            if len(alert) > 0:
                self.__send_msg(alert[0].text)

        self.__send_msg(f"posting {'success' if isSuccess else 'failure'}: {post['section']} {post['author']} {post['subject']}")
        return isSuccess

    def login(self):
        self.driver.get(self.ADDR_HOME)
        self.driver.find_element(By.ID, "ls_username").send_keys(self.USERNAME)
        self.driver.find_element(By.ID, "ls_password").send_keys(self.PASSWORD)
        self.driver.find_element(By.XPATH, "//button[@type='submit']").submit()
        self.__waitFor(self.XPATH_LOGGED_INFO)
        self.__send_msg(f"{self.USERNAME} has successfully logged in")
    
    def get_posts_by_section(self, url, threshold):
        self.driver.get(url)

        postsToReply = []
        while len(postsToReply) < threshold:
            self.__waitFor(self.XPATH_THREAD_SECTION)
            posts = self.__getPosts()
            postsToReply.extend([p for p in posts if p["lastPoster"] != self.USERNAME][:threshold - len(postsToReply)])
            self.driver.find_element(By.XPATH, self.XPATH_SECTION_NEXTPAGE).click()

        return postsToReply

    def get_posts(self, threshold):
        postsToReply = []
        for url in self.SECTIONS:
            postsToReply.extend(self.get_posts_by_section(url, int(threshold / len(self.SECTIONS))))
        
        postsToReply.extend(self.get_posts_by_section(self.ADDR_EA_SERIE, int(threshold % len(self.SECTIONS))))

        return postsToReply
    
    def autopost(self):
        self.number_of_replied_posts = 0

        postsToReply = self.get_posts(self.POST_NUM_LIMIT)
        for post in postsToReply:
            # self.__logPost(post)
            self.__reply_to_post(post)
            time.sleep(self.POST_INTERVAL)
    
        self.__send_msg(f"autoposting for {self.USERNAME} succeeded!")

    def check_in(self):
        self.driver.get(self.ADDR_CHECK_IN)
    
        checkInMsg = self.driver.find_elements(By.XPATH, self.XPATH_CHECK_IN_MSG)[0].text
        if ("已经签到过了" in checkInMsg):
            self.__send_msg(f"{self.USERNAME} has already checked in.")
        else:
            coins_before_checkin = self.__get_coin_number()

            moods = self.driver.find_elements(By.XPATH, self.XPATH_CHECK_IN_MOODS)
            moods[random.randint(0, len(moods)-1)].click()

            self.driver.find_element(By.XPATH, self.XPATH_CHECK_IN_SAY).send_keys("大家好")
    
            checkInForm = self.__waitFor(self.XPATH_CHECK_IN_FORM)
            checkInForm.submit()

            coins_after_checkin = self.__get_coin_number()
            succeeded = True if coins_after_checkin > coins_before_checkin else False
            self.__send_msg(f"checking for {self.USERNAME} {'succeeded' if succeeded else 'failed'}!")

    def get_progress(self):
        progress = int(self.number_of_replied_posts / self.POST_NUM_LIMIT * 100)
        return progress

    def print_state(self):
        state = []
        state.append(f"user_name={self.USERNAME}")
        state.append(f"num_limit={self.POST_NUM_LIMIT}")
        state.append(f"sections={self.SECTIONS}")
        state.append(f"algorithm={self.ALGORITHM}")
        state.append(f"need_checkin={self.NEED_CHECKIN}")
        state.append(f"")
        return state

    def run(self):
        try:
            self.login()

            if self.NEED_CHECKIN:
                self.check_in()

            self.autopost()
        except Exception as e:
            self.logger.error(e.with_traceback())
            self.__send_msg("Something wrong!")