import pickle
from selenium import webdriver
import selenium.webdriver.support.wait as WA
import pandas as pd
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains

import re

#scraping weibo content according to the url including key word

#all_weibo typeall=1
#hot_weibo xsort=hot
#time_range 'timescope=custom:2020-10-06-10:2020-10-06-11'

class OriginalWeibo:
    def __init__(self,driver,baseurl):
        # driver: chrome driver obtained in run.py
        # users_path: a url including the key word, example: https://s.weibo.com/weibo/%25E9%25AB%2598%25E7%25BA%25A7%25E6%2590%259C%25E7%25B4%25A2?q=%E8%82%96%E6%88%98&typeall=1&suball=1&
        self.driver=driver
        self.baseurl=baseurl

    def spider(self,hour1,hour2):
        # hour1: start_time (hour)
        # hour2: end_time (hour)
        self.links=[]
        self.weibo=pd.DataFrame()
        line=0
        for hour in range(hour1,hour2):
            # change the day here
            bburl=self.baseurl+'timescope=custom:2020-10-06-'+str(hour)+':2020-10-06-'+str(hour+1)+'&Refer=g'
            print('hour:',hour)
            for j in range(1,51): # for history weibo, user can only get 50 pages
                url=bburl+'&page='+str(j)
                self.driver.get(url)
                wait = WA.WebdriverWait(self.driver, poll_frequency=0.5, timeout=10)
                ct = wait.until(lambda w: w.find_element_by_css_selector('.card-wrap'))
                for item in self.driver.find_elements_by_css_selector('.card-wrap'):
                    try:
                        # a lot of weibo is reposting others's weibo instead of original, here find the original weibo link
                        if len(item.find_elements_by_css_selector('div.content > div.card-comment')) !=0:

                            orin_comment_link=item.find_element_by_css_selector('div > div.card-feed > div.content > div.card-comment > div.con > div > div.func > ul > li:nth-child(2) > a').get_attribute('href')
                            if orin_comment_link not in self.links:
                                self.links.append(orin_comment_link)

                        else:
                        # weibo content
                            user_link=item.find_element_by_css_selector('div > div.card-feed > div.content > div.info > div:nth-child(2) > a.name').get_attribute('href')
                            context=item.find_element_by_css_selector('div > div.card-feed > div.content > p.txt').text
                            time=item.find_element_by_css_selector('div > div.card-feed > div.content > p.from > a:nth-child(1)').text
                            like_num=item.find_element_by_css_selector('div > div.card-act > ul > li:nth-child(4) > a > em').text
            #                 context=item.select('div.content > p.txt')[0].text.strip()
            #                 time=item.select('div.content > p.from > a')[0].text.strip()
                            self.weibo.loc[line,'user_link']=user_link
                            self.weibo.loc[line,'context']=context
                            self.weibo.loc[line,'time']=time
                            self.weibo.loc[line,'like_num']=like_num
                            line+=1
                    except:
                        continue
    def save(self,links_path):
        f=open(links_path,'wb')
        pickle.dump(self.links,f) # record link
        f.close()
        self.weibo.drop_duplicates()
        # save weibo content
        self.weibo.to_csv('static/weibo.csv')
