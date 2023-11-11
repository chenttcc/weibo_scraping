import pickle
import pandas as pd
from selenium import webdriver
import selenium.webdriver.support.wait as WA
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains

import threading
from threading import Lock,Thread
import time,os
from original_weibo import OriginalWeibo
from user import User
from weibo_repost import WeiboRepost
from weibo_comment import WeiboComment

# using cookies to keep the Chrome driver login and get the data we want, ensure multiple cookies in pool in decrease the risk of exposed
cookies_pool=[]
# Chrome_driver path, which needs to be consistent with Chrome driver version
path=r"C:\Users\HUAWEI\AppData\Local\Google\Chrome\Application\chromedriver.exe"
drivers_num = 1
drivers=[]
for num in range(drivers_num):
    driver = webdriver.Chrome(executable_path=path)
    url='https://s.weibo.com/weibo/%25E9%25AB%2598%25E7%25BA%25A7%25E6%2590%259C%25E7%25B4%25A2?q=%E8%82%96%E6%88%98&typeall=1&suball=1&timescope=custom:2020-10-06-0:2020-10-06-1&Refer=g'
    # first let the driver visit the original web
    driver.get(url)
    driver.delete_all_cookies()
    for i in cookies_pool[num].split(';'):
        name=i.split('=')[0]
        value=i.split('=')[1]
        dict={}
        dict['domain']='.weibo.com'
        dict['name']=name.strip()
        dict['value']=value.strip()
        dict['path']='/'
        dict['expires']=""
        dict['httpOnly']=False
        dict['HostOnly']=False
        dict['Secure']=False
        driver.add_cookie(cookie_dict=dict)
    driver.get(url)
    drivers.append(driver)
#
#use first driver as an example
driver = drivers[0]
baseurl = 'https://s.weibo.com/weibo/%25E9%25AB%2598%25E7%25BA%25A7%25E6%2590%259C%25E7%25B4%25A2?q=%E8%82%96%E6%88%98&typeall=1&suball=1&'
original = OriginalWeibo(driver,baseurl)
original.spider()
original.save('static/links.pkl')


repost=WeiboRepost(driver,'static/links.pkl')
repost.spider()

comment = WeiboComment(driver,'static/links.pkl')
comment.save()

user=User(driver,'static/original_weibo.csv')
user.spider()


# using multi threading to accelerate, use multiple drivers at the same time
for j in range(drivers_num):
    user=User(drivers[j],'static/original_weibo.csv')
    idxlist=[]
    idxlist.extend(range(490,500))
    idxlist.extend(range(990,1000))
    idxlist.extend(range(1490,1500))
    idxlist.extend(range(1990,1997))
    t=threading.Thread(target=user.spider,args=(4,idxlist))
    t.start()
    time.sleep(1)