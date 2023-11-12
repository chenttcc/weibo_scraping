# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymysql
import re
import datetime


db_password = '111'
def parse_time(collect_time,str):
    if len(re.findall('秒',str)) > 0 :
        inttime=int(re.findall('(\d+)秒',str)[0])
        time=collect_time+datetime.timedelta(seconds=(-1*inttime))
    elif len(re.findall('分钟',str)) > 0:
        inttime=int(re.findall('(\d+)分钟',str)[0])
        time=collect_time+datetime.timedelta(minutes=(-1*inttime))
    elif len(re.findall('今天',str)) > 0:
        hour,minute = re.findall('(\d+):(\d+)',str)[0]
        time=datetime.datetime.combine(collect_time.date(),datetime.time(int(hour),int(minute),0,0))
    elif len(re.findall('(\d+)月(\d+)日',str)) > 0:
        month,day= re.findall('(\d+)月(\d+)日',str)[0]
        hour,minute = re.findall('(\d+):(\d+)',str)[0]
        time = datetime.datetime(collect_time.year(),int(month),int(day),int(hour),int(minute),0)
    else:
        raise Exception("The error about time type")
    return time.strftime("%Y-%m-%d %H:%M:%S")

class WeiboscrapyPipeline:
    def __init__(self):
        self.db = pymysql.connect(host='localhost',
                     user='root',
                     password=db_password,
                     database='weibo')
        self.cursor = self.db.cursor()
        self.insert_num = 0
    def process_item(self, item, spider):
        collect_time=datetime.datetime.strptime(item['spidertime'],"%Y-%m-%d %H:%M:%S")
        time=parse_time(collect_time,item['sendtime'])
        sql='''insert into xiaozhanweibo (ttime,user_link,
            user_name,content)
            values(%s,%s,%s,%s)'''% ('"'+time+'"',
        '"'+item['user_link']+'"','"'+item['user_name']+'"',
        '"'+item['content']+'"')
        try:
            self.cursor.execute(sql)
            self.insert_num += 1
            self.db.commit()
            # When the numbers of new records achieve 100, the sql below will be executed to delete the duplicated weibo content
            if self.insert_num == 100:
                self.cursor.execute('set @maxid := (select max(id) from `xiaozhanweibo`)')
                sql = '''
                    delete from `xiaozhanweibo`
                    where id between greatest(0,@maxid-100) and @maxid
                    and (user_name,content) in
                    (select t1.user_name,t1.content from
                    (select user_name,content from `xiaozhanweibo` where id between greatest(0,@maxid-100) and @maxid group by user_name,content having count(*)>1) t1)
                    and id not in
                    (select t2.id from (select min(id) as id from `xiaozhanweibo` where id between greatest(0,@maxid-100) and @maxid group by user_name,content having count(*)>1) t2);
                  '''
                self.cursor.execute(sql)
                self.db.commit()
                # self.cursor.execute('ALTER  TABLE  `xiaozhanweibo` DROP id')
                # self.cursor.execute('ALTER  TABLE  `xiaozhanweibo` ADD id int PRIMARY KEY NOT NULL AUTO_INCREMENT FIRST')
                # self.db.commit()
                self.insert_num = 0
        except Exception as e:
            print('There is error in datebase execution', e)
            self.db.rollback()
        return item

    def close_spider(self,spider):
        self.db.close()
