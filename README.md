# weibo_scraping
Using Selenium and Scrapy to collect comprehensive data from Weibo (user, weibo, comment, repost)

## *** Selenium
* Because Weibo website is a dynamic web, using selenium package can skip many verification steps and decrease many risk of expose.
* This script collect weibo data comprehensively, and use weibo_id, user_id to connect those collected csv. First collect weibo content based on parsed url of keyword, save the url link and original weibo link. Then given those links, collect data about users, comments and reposts under the given weibo link.

### run.py
  * initiate cookies_pool and driver
  * execute class `original weibo`, `user`, `weibo comment`, `weibo repost`
  * save file

### original_weibo.py
* collect weibo information based on parse_url of key word
* save the original_weibo link
* save the weibo content under the given url
  * adjust the history time range
  * collect 50-page data


### user.py
* collect user information based on url of users
* `self introduction` `following information` `weibo this user liked` `weibo this user published`


### weibo_comment.py
* collect comment content under the specific weibo

### weibo_repost.py
* collect repost content under the specific weibo

