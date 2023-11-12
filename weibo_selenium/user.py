import pandas as pd
import time
import numpy as np
import pickle
from selenium import webdriver
import selenium.webdriver.support.wait as WA
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains


# get the user information according to user's url
    # user demographic
    # the weibo content published/liked by this user
class User:

    def __init__(self,driver,users_path):
        # driver: chrome driver obtained in run.py
        # users_path: a csv file including a column named 'original_user_link' which is the url of weibo user
        self.driver=driver
        self.user_urls=list(pd.read_csv(users_path)['original_user_link'])


    def spider(self,num,idxlist):
        self.user_info_df=pd.DataFrame()
        li=0
        self.user_original_weibo_df=pd.DataFrame()
        lw=0
        self.user_like_weibo_df=pd.DataFrame()
        ll=0
        print('Tthe total number：',len(self.user_urls))
        self.links=[]
        for user_idx in idxlist:
        #for user_idx in np.random.randint(0,1996,5):
        #for idx in range(len(self.user_urls)):
            user_url=self.user_urls[user_idx]
            if user_url not in self.links:
                self.links.append(user_url)
            else:
                continue
            self.driver.get(user_url)
            wait = WA.WebDriverWait(self.driver, poll_frequency=0.5, timeout=5)
            ct = wait.until(lambda w: w.find_element_by_css_selector('div.WB_frame'))

            try:
                time.sleep(2)
                # self_ introduction
                tag=self.driver.find_element_by_css_selector('div.pf_intro').text
                # url
                self.user_info_df.loc[li,'href']=user_url
                # self-designed tag
                self.user_info_df.loc[li,'tag']=tag
            except:
                pass
            try:
                # following number
                attention_num=self.driver.find_element_by_css_selector('div.WB_cardwrap.S_bg2 > div > div > table > tbody > tr > td:nth-child(1)').text
                # follower number
                fans_num=self.driver.find_element_by_css_selector('div.WB_cardwrap.S_bg2 > div > div > table > tbody > tr > td:nth-child(2)').text
                # weibo number
                weibo_num=self.driver.find_element_by_css_selector('div.WB_cardwrap.S_bg2 > div > div > table > tbody > tr > td:nth-child(3)').text
                self.user_info_df.loc[li,'attention_num']=attention_num
                self.user_info_df.loc[li,'fans_num']=fans_num
                self.user_info_df.loc[li,'weibo_num']=weibo_num
            except Exception as e:
                print(e)
                print(user_url)
                pass

            try:
                time.sleep(1)

                inf_href=self.driver.find_element_by_css_selector('div.WB_cardwrap.S_bg2 > div > a.WB_cardmore.S_txt1.S_line1.clearfix').get_attribute('href')

                #self information
                self.driver.get(inf_href)
                wait = WA.WebDriverWait(self.driver, poll_frequency=0.5, timeout=10)
                ct = wait.until(lambda w: w.find_element_by_css_selector('div.WB_frame'))
                time.sleep(1)
                #Pl_Official_PersonalInfo__57 > div > div > div.WB_innerwrap
                user_info=self.driver.find_elements_by_css_selector('div.WB_innerwrap > div.m_wrap.clearfix')
                self.user_info_df.loc[li,'user_info']='\n'.join([info.text for info in user_info])
                li+=1
            except Exception as e:
                print(e)
                li+=1
                print(user_url)
                pass

            # get all the weibo that this user like
            try:
                self.driver.get(user_url)
                wait = WA.WebDriverWait(self.driver, poll_frequency=0.5, timeout=5)
                ct = wait.until(lambda w: w.find_element_by_css_selector('div.WB_frame'))

                js="var q=document.documentElement.scrollTop=100000"
                time.sleep(1)
                self.driver.execute_script(js)
                time.sleep(1)

                like_href=self.driver.find_element_by_css_selector('#Pl_Official_LikeMerge__15 > div > div > a').get_attribute('href')
                #Liked weibo
                self.driver.get(like_href)
                wait = WA.WebDriverWait(self.driver, poll_frequency=0.5, timeout=10)
                ct = wait.until(lambda w: w.find_element_by_css_selector('#Pl_Core_LikesFeedV6__68'))
                like_weibo=self.driver.find_elements_by_css_selector('#Pl_Core_LikesFeedV6__68 > div:nth-child(2) > div.WB_feed.WB_feed_v3.WB_feed_v4 > div')

                js="var q=document.documentElement.scrollTop=100000"
                for i in range(2):
                    time.sleep(2.5)
                    self.driver.execute_script(js)

                for idx in range(len(like_weibo)):
                    i=like_weibo[idx]
                    try:

                        context=i.find_element_by_css_selector('div.WB_feed_detail.clearfix > div.WB_detail > div.WB_text.W_f14').text
                        self.user_like_weibo_df.loc[ll,'context']=context
                        self.user_like_weibo_df.loc[ll,'user']=li-1
                        ll+=1
                    except:
                        pass
            except Exception as e :
                print(e)
                pass

            # get all the weibo information this user published
            try:
                self.driver.get(user_url+'?profile_ftype=1&is_ori=1#_0')
                wait = WA.WebDriverWait(self.driver, poll_frequency=0.5, timeout=10)
                ct = wait.until(lambda w: w.find_element_by_css_selector('#plc_frame'))

                # refresh until all weibo content in the page
                js="var q=document.documentElement.scrollTop=100000"
                for i in range(3):
                    time.sleep(2)
                    self.driver.execute_script(js)

                try:
                    #Pl_Official_MyProfileFeed__21 > div > div:nth-child(2)
                    # weibo content
                    user_weibo=self.driver.find_elements_by_css_selector('div.WB_cardwrap.WB_feed_type.S_bg2.WB_feed_like')
                    print('length',len(user_weibo))
                    for i in user_weibo:
                        # text
                        weibo_context=i.find_element_by_css_selector('div.WB_feed_detail.clearfix > div.WB_detail > div.WB_text.W_f14').text
                        # time
                        weibo_time=i.find_element_by_css_selector('div.WB_feed_detail.clearfix > div.WB_detail > div.WB_from.S_txt2 > a').text
                        # the number of like
                        like_num=i.find_element_by_css_selector('div.WB_feed_handle > div > ul > li:nth-child(4) > a > span > span > span > em:nth-child(2)').text
                        self.user_original_weibo_df.loc[lw,'weibo_context']=weibo_context
                        self.user_original_weibo_df.loc[lw,'weibo_time']=weibo_time
                        self.user_original_weibo_df.loc[lw,'like_num']=like_num
                        self.user_original_weibo_df.loc[lw,'user']=li-1
                        lw+=1
                except Exception as e:
                    print(e)
                    print(user_url)
                    pass

            except Exception as e:
                print(e)
                print(user_url)
                pass

            print(user_idx)
            #if user_idx%10==0:
            self.save(num)
    def save(self,num):
        # save user demographic
        self.user_info_df.to_csv('static/user_info'+str(num)+'.csv')
        # save the weibo users published
        self.user_original_weibo_df.to_csv('static/user_original'+str(num)+'.csv')
        # save the weibo users liked
        self.user_like_weibo_df.to_csv('static/user_like_weibo.csv')
        # this three table use user_id to connect with each other



