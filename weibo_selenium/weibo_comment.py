import time
import pandas as pd
import pickle
from selenium import webdriver
import selenium.webdriver.support.wait as WA
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains

# given the weibo link, get the corresponding comment content
class WeiboComment:
    def __init__(self,driver,links_path):
        self.driver=driver
        f=open(links_path,'rb')
        self.links=pickle.load(f)
        f.close()

    def spider(self):
        self.original_weibo=pd.DataFrame()
        self.comments=pd.DataFrame()
        lo=0
        lc=0
        for idx in range(len(self.links)):
            url=self.links[idx]
            try:
                self.driver.get(url)
                wait = WA.WebDriverWait(self.driver, poll_frequency=0.5, timeout=10)
                ct = wait.until(lambda w: w.find_element_by_css_selector('div.WB_feed_detail.clearfix'))
            except:
                pass
        
            js="var q=document.documentElement.scrollTop=100000"
            for i in range(3):
                time.sleep(2)
                self.driver.execute_script(js)
        
            num=0
            try:
                while self.driver.find_element_by_css_selector('div.WB_feed_repeat.S_bg1.WB_feed_repeat_v3\
                > div > div.repeat_list > div:nth-child(2) > div > div > a') and num<=20:
                    num+=1
                    time.sleep(0.5)
                    self.driver.execute_script(js)
                    menu=self.driver.find_element_by_css_selector('div.WB_feed_repeat.S_bg1.WB_feed_repeat_v3\
                > div > div.repeat_list > div:nth-child(2) > div > div > a')
                    hidden=menu.find_element_by_css_selector('span')
                    ActionChains(self.driver).move_to_element(menu).click(hidden).perform()
            except:
                pass
        
            try:
                original_context=self.driver.find_element_by_css_selector('div.WB_feed_detail.clearfix > div.WB_detail > div.WB_text.W_f14').text
                original_user_link=self.driver.find_element_by_css_selector('div.WB_feed_detail.clearfix > div.WB_detail > div.WB_info > a.W_f14.W_fb.S_txt1').get_attribute('href')
                original_time=self.driver.find_element_by_css_selector('div.WB_feed_detail.clearfix > div.WB_detail > div.WB_from.S_txt2 > a:nth-child(1)').text
                self.original_weibo.loc[lo,'original_user_link']=original_user_link
                self.original_weibo.loc[lo,'original_context']=original_context
                self.original_weibo.loc[lo,'original_time']=original_time
                lo+=1
        
                sc_comments=self.driver.find_elements_by_css_selector('div.WB_feed_repeat.S_bg1.WB_feed_repeat_v3 > div > div.repeat_list > div:nth-child(2) > div > div > div')
                for i in sc_comments:
                    try:
                        sc_user=i.find_element_by_css_selector('div.list_con > div.WB_text > a').get_attribute('href')
                        sc_comment=i.find_element_by_css_selector('div.list_con > div.WB_text').text
                        sc_time=i.find_element_by_css_selector('div.list_con > div.WB_func.clearfix > div.WB_from.S_txt2').text
                        like_num=i.find_element_by_css_selector('div.list_con > div.WB_func.clearfix > div.WB_handle.W_fr > ul > li:nth-child(4) > span > a > span > em:nth-child(2)').text
                        self.comments.loc[lc,'sc_user']=sc_user
                        self.comments.loc[lc,'sc_comment']=sc_comment
                        self.comments.loc[lc,'sc_time']=sc_time
                        self.comments.loc[lc,'like_num']=like_num
                        self.comments.loc[lc,'self.original_weibo']=(lo-1)
                        lc+=1
                    except:
                        continue
                if idx%10==0:
                    f=open('log_comments.txt','w')
                    f.write(str(idx))
                    f.close()
                    self.save()
            except:
                pass
    def save(self):
        self.original_weibo.to_csv('static/original_weibo.csv')
        self.comments.to_csv('static/comments.csv')