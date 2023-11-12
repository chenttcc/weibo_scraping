import scrapy
from scrapy import Request
from selenium import webdriver
from threading import Timer
import time
import re
from weiboscrapy.items import WeiboscrapyItem
import datetime
import random
import os


class ItcastSpider(scrapy.Spider):
    # Spider name
    name = 'itcast'
    # URL examples
    # example 1
    url = 'https://s.weibo.com/weibo?q=%E8%82%96%E6%88%98&Refer=g'
    # example 2
    # url = 'https://s.weibo.com/weibo/%25E4%25B8%25A5%25E6%25B5%25A9%25E7%25BF%2594'
    # example 3
    # url='https://s.weibo.com/weibo?q=%E8%B4%BA%E5%B3%BB%E9%9C%96&Refer=SWeibo_box'
    # example 4
    # url = 'https://s.weibo.com/weibo/%25E8%2592%25B2%25E7%2586%25A0%25E6%2598%259F?topnav=1&wvr=6&b=1'
    # List to store cookies
    cookies = []
    # Current working directory
    dirs = os.getcwd()

    # Read cookies from file and store in the 'cookies' list
    with open(os.path.join(dirs, 'cookies.txt'), 'r') as f:
        for line in f.readlines():
            line = line.strip()
            cookies.append(line)

    def change_cookie(self):
        # Change the user agent and use a randomly selected cookie
        cookie = random.sample(self.cookies, 1)[0]
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36 Edg/95.0.1020.30',
            'Cookie': cookie,
            'Host': 's.weibo.com',
            'sec-ch-ua': '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'Connection': 'keep-alive'
        }

    last_interval_time = 0
    interval_time = 0
    error = 300  # allow error can continue lasting for 5 minutes
    page = 2

    def monitor(self):
        # Reset cookies when the current time is 12:00
        curr_time = datetime.datetime.now()
        if curr_time.hour == 12:
            self.cookies = []
            with open(os.path.join(self.dirs, 'cookies.txt'), 'r') as f:
                for line in f.readlines():
                    line = line.strip()
                    self.cookies.append(line)

    def start_requests(self):
        # Schedule the monitor method to run every 1800 seconds
        t = Timer(1800, self.monitor())
        t.start()
        self.change_cookie()
        yield Request(self.url, headers=self.headers, callback=self.parse)

    def parse(self, response):
        # Get the current time
        pagetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        items = response.css('.card-wrap')

        for item in items:
            if item.css(
                    'div > div.card-feed > div.content > div.info > div:nth-child(2) > a.name::attr(href)').extract_first() is None:
                continue
            # Choose Non-hot weibo
            if item.css('div.card-top > h4 > a::text').extract_first() is None:
                user_link = item.css(
                    'div > div.card-feed > div.content > div.info > div:nth-child(2) > a.name::attr(href)').extract_first()
                user_name = item.css(
                    'div > div.card-feed > div.content > div.info > div:nth-child(2) > a.name::attr(nick-name)').extract_first()
                context = item.css('div > div.card-feed > div.content > p.txt::text').extract()
                sendtime = item.css('div > div.card-feed > div.content > p.from > a:nth-child(1)::text').extract_first()
                # like_num=item.css('div > div.card-act > ul > li:nth-child(4) > a > em::text').extract_first()
                if context:
                    context = ''.join(context)
                # Create a WeiboscrapyItem and yield the result
                pipe = WeiboscrapyItem()
                pipe['spidertime'] = pagetime
                pipe['user_link'] = user_link
                pipe['user_name'] = user_name
                pipe['content'] = context
                pipe['sendtime'] = sendtime
                yield pipe

        try:
            # Attempt to calculate sleep time and handle errors
            interval_time = self.parse_time(sendtime)
            print('-----sleep ' + str(interval_time) + ' seconds--------')

            # if the latest time of last data collecting minus this latest time is greater than error, that
            # means there might be some weibo content been missed, then keep collecting the previous weibo through
            # visiting the previous pages until the error has been fixed.
            if self.last_interval_time - interval_time > self.error:
                self.page = 2
                add_params = {}
                add_params['revoke_time'] = self.last_interval_time
                self.change_cookie()
                yield Request(self.url + '&page=' + str(self.page), headers=self.headers, callback=self.parse_remain,
                              cb_kwargs=add_params, dont_filter=True)
            
            self.last_interval_time = interval_time
            # if the lastest weibo is not earlier than 60 seconds ago, then sleep a while in case there are too many redundancy
            if interval_time > 60:
                time.sleep(interval_time)
            else:
                time.sleep(60)
            self.change_cookie()
            yield Request(self.url, headers=self.headers, callback=self.parse, dont_filter=True)
        except:
            print(pagetime, 'No content！')
            self.change_cookie()
            yield Request(self.url, headers=self.headers, callback=self.parse, dont_filter=True)

    def parse_time(self, str):
        # Parse the time information and return in seconds
        inttime = 0
        if len(re.findall('秒', str)) > 0:
            inttime = int(re.findall('(\d+)秒', str)[0])
        elif len(re.findall('分钟', str)) > 0:
            inttime = int(re.findall('(\d+)分钟', str)[0]) * 60
        else:
            inttime = 3600
        return inttime

    # Used to supplement crawling when there is a significant difference between the last crawl and the current one.
    def parse_remain(self, response, revoke_time):
        # keep scraping
        print('--keep scraping--')
        pagetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        items = response.css('.card-wrap')
        for item in items:
            if item.css(
                    'div > div.card-feed > div.content > div.info > div:nth-child(2) > a.name::attr(href)').extract_first() is None:
                continue
            if item.css('div.card-top > h4 > a::text').extract_first() is None:
                user_link = item.css(
                    'div > div.card-feed > div.content > div.info > div:nth-child(2) > a.name::attr(href)').extract_first()
                user_name = item.css(
                    'div > div.card-feed > div.content > div.info > div:nth-child(2) > a.name::attr(nick-name)').extract_first()
                context = item.css('div > div.card-feed > div.content > p.txt::text').extract()
                sendtime = item.css('div > div.card-feed > div.content > p.from > a:nth-child(1)::text').extract_first()
                # like_num=item.css('div > div.card-act > ul > li:nth-child(4) > a > em::text').extract_first()
                if context:
                    context = ''.join(context)
                pipe = WeiboscrapyItem()
                pipe['spidertime'] = pagetime
                pipe['user_link'] = user_link
                pipe['user_name'] = user_name
                pipe['content'] = context
                pipe['sendtime'] = sendtime
                yield pipe

        interval_time = self.parse_time(sendtime)
        if interval_time < revoke_time:
            add_params = {}
            add_params['revoke_time'] = revoke_time
            self.page += 1
            self.change_cookie()
            yield Request(self.url + '&page=' + str(self.page), headers=self.headers, callback=self.parse_remain,
                          cb_kwargs=add_params, dont_filter=True)
