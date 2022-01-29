import threading
import logging
import random
import re
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located

class Baoshu8(threading.Thread):
    def __init__(self, param, msg_array):
        super(Baoshu8, self).__init__()

        self.POST_STR_LIMIT = 10
        self.POST_INTERVAL  = 60

        self.TIME_LONG = 15
        self.TIME_NORM = 3

        self.ADDR_HOME        = "http://www.baoshu8.com"
        self.ADDR_GOSSIP      = "http://www.baoshu8.com/t56"
        self.ADDR_EA_SERIE    = "http://www.baoshu8.com/t289"
        self.ADDR_CHECK_IN    = "http://www.baoshu8.com/hack.php?H_name=xqqiandao"
        self.SECTION_ADDR = {
            "baidupan_movie": "http://www.baoshu8.com/t260",  #baidu pan movie
            "baidupan_series": "http://www.baoshu8.com/t265",  #baidu pan series
            "baidupan_comic": "http://www.baoshu8.com/t267",  #baidu pan comic
            "baidupan_documentary": "http://www.baoshu8.com/t268",  #baidu pan documentary
            "baidupan_classic": "http://www.baoshu8.com/t279"   #baidu pan classic movie
        }
        self.POSTS = [
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
        self.XPATH_POST_NUM         = "//div[@id='pw_box']//ul[@class='menu-half cc']/li[3]"
        self.XPATH_SECTION          = "//div[@id='sidebar']//h2"
        self.XPATH_POST_THREADS     = "//tbody[@id='threadlist']/tr[td[1][a[@title]] and td[2][a] and td[3][a] and td[5][a]]"
        self.XPATH_SUBJECT_HEADER   = "//h1[@id='subject_tpc']"
        self.XPATH_NEXTPAGE         = "//div[@id='tabA']//a[@class='pages_next']"
        self.XPATH_POSTAREA         = "//textarea[@id='textarea']"
        self.XPATH_POST_SUBMIT      = "//button[@name='Submit']"
        self.XPATH_POST_FORM        = "//form[@id='anchor']"
        self.XPATH_CHECK_IN_FORM    = "//form[@action='hack.php?H_name=xqqiandao']"
        self.XPATH_CHECK_IN_MOODS   = "//input[@name='qdxq']"
        self.XPATH_CHECK_IN_STAT    = "//tbody/tr[2][count(td)=1]/td/b"
        self.XPATH_CHECK_IN_COUNT   = "//tbody/tr[2][count(td)=1]/td/b[5]"
        self.XPATH_WARN_MSG         = "//div[@class='regIgnore']/p[1]"

        # configuring each autopost thread
        self.msg_array = msg_array
        self.USERNAME = param["userId"]
        self.PASSWORD = param["password"]
        self.POST_NUM_LIMIT = int(param["numOfPost"])
        self.SECTIONS = [self.SECTION_ADDR[section] for section in param["sections"] if param["sections"][section]]
        self.ALGORITHM = param["algorithm"]
        self.NEED_CHECKIN = param["checkin"]

        self.logger = logging.getLogger(self.USERNAME)
        logging.basicConfig(level=logging.INFO, format="%(asctime)s: %(name)s: %(levelname)s: %(message)s")

        self.XPATH_LOGGED_INFO      = f"//span[@id='td_userinfomore']/a/span[text()='{self.USERNAME}']"

        chrome_options = Options()
        chrome_options.headless = True
        self.driver = webdriver.Chrome(options=chrome_options)

    def __del__(self):
        if self.driver:
            self.driver.close()

    def __waitFor(self, xpath, time=None):
        return WebDriverWait(self.driver, timeout=time if time else self.TIME_NORM).until(presence_of_element_located((By.XPATH, xpath)))

    def __printWarning(self):
        result = None

        warns = self.driver.find_elements_by_xpath(self.XPATH_WARN_MSG)
        if (len(warns) > 0):
            result = warns[0].text

        return result

    def __getPostNumber(self):
        self.__waitFor(self.XPATH_LOGGED_INFO)
        ActionChains(self.driver).move_to_element(self.driver.find_element_by_xpath(self.XPATH_LOGGED_INFO)).perform()
        return int(re.search(r"\d+", self.driver.find_element_by_xpath(self.XPATH_POST_NUM).text).group(0))

    def __getPosts(self):
        posts = []
        threads = self.driver.find_elements_by_xpath(self.XPATH_POST_THREADS)
        for thread in threads:
            post = {}
            post["section"]    = self.driver.find_element_by_xpath("//div[@id='sidebar']//h2").text
            post["tar"]        = thread.find_element_by_xpath("./td[1]/a[1]").get_attribute("title")

            elems              = thread.find_elements_by_xpath("./td[2]/a")
            if len(elems) == 1:
                post["subject"] = elems[0].text
                post["link"]    = elems[0].get_attribute("href")
            else:
                post["subject"] = elems[0].text + elems[1].text
                post["link"]    = elems[1].get_attribute("href")

            post["author"]     = thread.find_element_by_xpath("./td[3]/a[1]").text
            post["lastPoster"] = thread.find_element_by_xpath("./td[5]/a[1]").text
            posts.append(post)
        return posts
    
    def __replyToPost(self, post, replyIndex):
        result = False
        self.driver.get(f"{post['link']}")
        self.__waitFor(self.XPATH_SUBJECT_HEADER).text
        numBefore = self.__getPostNumber()

        form =  self.driver.find_element_by_xpath(self.XPATH_POST_FORM)
        form.find_element_by_xpath(self.XPATH_POSTAREA).send_keys(self.POSTS[replyIndex])
        form.find_element_by_xpath(self.XPATH_POST_SUBMIT).click()

        numAfter = self.__getPostNumber()
        result = numAfter > numBefore
        self.__send_msg(f"posting {'success' if result else 'failure'}: {post['section']} {post['author']} {post['subject']}")

        return result

    def login(self):
        self.driver.get(self.ADDR_HOME)
        self.driver.find_element_by_id("nav_pwuser").send_keys(self.USERNAME)
        self.driver.find_element_by_id("showpwd").send_keys(self.PASSWORD)
        self.driver.find_element_by_name("login_FORM").submit()
        self.__waitFor(self.XPATH_LOGGED_INFO)
        self.__send_msg(f"{self.USERNAME} has successfully logged in")
    
    def getPosts_bySection(self, url, threshold):
        self.driver.get(url)

        postsToReply = []
        while len(postsToReply) < threshold:
            self.__waitFor(self.XPATH_SECTION)
            posts = self.__getPosts()
            postsToReply.extend([p for p in posts if p["lastPoster"] != self.USERNAME][:threshold - len(postsToReply)])
            self.driver.find_element_by_xpath(self.XPATH_NEXTPAGE).click()

        return postsToReply

    def getPosts_distributed(self, threshold):
        postsToReply = []
        for url in self.SECTIONS:
            postsToReply.extend(self.getPosts_bySection(url, int(threshold / len(self.SECTIONS))))
        
        postsToReply.extend(self.getPosts_bySection(self.ADDR_EA_SERIE, int(threshold % len(self.SECTIONS))))

        return postsToReply
    
    def autopost(self):
        num = self.__getPostNumber()
        if (num >= self.POST_NUM_LIMIT):
            self.__send_msg(f"{self.USERNAME} has already posted {num} times today! No more posting.")
        else:
            #postsToReply = self.__getPosts_bySection(self.SECTION_NAME_BAIDUPAN, self.POST_NUM_LIMIT)
            postsToReply = self.getPosts_distributed(self.POST_NUM_LIMIT - num)
        
            replyIndex = 0
            for post in postsToReply:
                self.__replyToPost(post, replyIndex)
                replyIndex = (replyIndex + 1) % self.POST_STR_LIMIT
                time.sleep(self.POST_INTERVAL)
        
            self.__send_msg(f"autoposting for {self.USERNAME} succeeded!")

    def check_in(self):
        self.driver.get(self.ADDR_CHECK_IN)
        checkInForm = self.__waitFor(self.XPATH_CHECK_IN_FORM)
    
        checkInStat = self.driver.find_elements_by_xpath(self.XPATH_CHECK_IN_STAT)
        if (len(checkInStat) > 4):
            self.__send_msg(f"{self.USERNAME} has already checked in.")
        else:
            moods = self.driver.find_elements_by_xpath(self.XPATH_CHECK_IN_MOODS)
            moods[random.randint(0, len(moods)-1)].click()
    
            checkInForm.submit()
    
            checkInCount = self.__waitFor(self.XPATH_CHECK_IN_COUNT, self.TIME_LONG)
            self.__send_msg(f"checking for {self.USERNAME} {'succeeded' if (checkInCount.text == '1') else 'Failed'}!")

    def __send_msg(self, msg):
        self.msg_array.append({ "id": len(self.msg_array), "msg": f"{time.strftime('%Y-%m-%d %X')} - {msg}" })
        self.logger.info(msg)

    def get_progress(self):
        post_num = self.__getPostNumber()
        progress = int(post_num / self.POST_NUM_LIMIT * 100)
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

            # while len(self.msg_array) < self.POST_NUM_LIMIT:
            #     self.__send_msg("test msg")
            #     time.sleep(10)

            if self.NEED_CHECKIN:
                self.check_in()

            self.autopost()
        except:
            self.__send_msg(self.__printWarning())

