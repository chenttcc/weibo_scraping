import time
import pandas as pd
import pickle
from selenium import webdriver
import selenium.webdriver.support.wait as WA
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains

# obtain 5-page repost content
class WeiboRepost:
    def __init__(self,driver,links_path):
        self.driver=driver
        f=open(links_path,'rb')
        self.links=pickle.load(f)
        f.close()

    def spider(self):
        self.original_weibo=pd.DataFrame()
        self.reposts=pd.DataFrame()
        lo=0
        lr=0
        for idx in range(len(self.links)):
            url=self.links[idx]
            url=url+'&type=repost'
            try:
                self.driver.get(url)
                wait = WA.WebDriverWait(self.driver, poll_frequency=0.5, timeout=10)
                ct = wait.until(lambda w: w.find_element_by_css_selector('div.WB_feed_detail.clearfix'))
            except:
                break

            js="var q=document.documentElement.scrollTop=100000"
            for i in range(2):
                time.sleep(0.5)
                self.driver.execute_script(js)
            try:
                original_context=self.driver.find_element_by_css_selector('div.WB_feed_detail.clearfix > div.WB_detail > div.WB_text.W_f14').text
                original_user_link=self.driver.find_element_by_css_selector('div.WB_feed_detail.clearfix > div.WB_detail > div.WB_info > a.W_f14.W_fb.S_txt1').get_attribute('href')
                original_time=self.driver.find_element_by_css_selector('div.WB_feed_detail.clearfix > div.WB_detail > div.WB_from.S_txt2 > a:nth-child(1)').text
                self.original_weibo.loc[lo,'original_user_link']=original_user_link
                self.original_weibo.loc[lo,'original_context']=original_context
                self.original_weibo.loc[lo,'original_time']=original_time
                lo+=1
            except:
                pass

            try:
                 num=0
                 # obtain 5-page repost content
                 while self.driver.find_element_by_css_selector('a.page.next.S_txt1.S_line1') and num<=5:
                    time.sleep(1)
                    sc_reposts=self.driver.find_elements_by_css_selector('div.repeat_list > div.list_box > div > div.list_li.S_line1.clearfix')
                    for i in sc_reposts:
                        try:
                            sc_user=i.find_element_by_css_selector('div.list_con > div.WB_text > a').get_attribute('href')
                            sc_repost=i.find_element_by_css_selector('div.list_con > div.WB_text').text
                            sc_time=i.find_element_by_css_selector('div.list_con > div.WB_func.clearfix > div.WB_from.S_txt2 > a').text
                            try:
                                repost_num=i.find_element_by_css_selector('div.list_con > div.WB_func.clearfix > div.WB_handle.W_fr > ul > li:nth-child(2) > span > a').text
                                like_num=i.find_element_by_css_selector('div.list_con > div.WB_func.clearfix > div.WB_handle.W_fr > ul > li:nth-child(3) > span > a > span > em:nth-child(2)').text
                            except:
                                repost_num=' '
                                like_num=' '
                            self.reposts.loc[lr,'sc_user']=sc_user
                            self.reposts.loc[lr,'sc_repost']=sc_repost
                            self.reposts.loc[lr,'sc_time']=sc_time
                            self.reposts.loc[lr,'repost_num']=repost_num
                            self.reposts.loc[lr,'like_num']=like_num
                            self.reposts.loc[lr,'original_weibo']=(lo-1)
                            lr+=1
                        except:
                            pass
                    self.driver.execute_script(js)
                    menu=self.driver.find_element_by_css_selector('a.page.next.S_txt1.S_line1')
                    hidden=menu.find_element_by_css_selector('span')
                    ActionChains(self.driver).move_to_element(menu).click(hidden).perform()
                    num+=1
            except:
                pass
            if idx%10==0:
                f=open('log_reposts.txt','w')
                f.write(str(idx))
                f.close()
                self.save()
    def save(self):
        self.original_weibo.to_csv('static/original_weibo_repost.csv')
        self.reposts.to_csv('static/reposts.csv')
