#!/usr/bin/env /python
# -*- coding:utf-8 -*-
# Author:ZerryZhong

"""
假设有两个用户，存放在表user中
每隔5s随机生成一个11位的电话号码，开始判断
  1. 如果该用户之前没有使用过该电话号码，则输出该用户名和电话号码  print username,phonenumber
  2. 如果该用户之前使用过该电话号码,则跳过，开始下次循环

因为只有两个用户，我想启动多进程模式，启动两个进程，每个进程跑一个用户的这种循环

设计表，有三张表，user表存在用户名，phone表存放使用过的电话号码，phone_user表做user和phone之间的关联，类似于多对多的关系
CREATE TABLE `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(64) DEFAULT NULL,
  `inviteKey` varchar(64) DEFAULT NULL,
  `status` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `inviteKey` (`inviteKey`)
)

 select * from user ;
+----+--------------+-----------
| id | username | inviteKey   |
+----+--------------+
|  1 | yy1   |  *** |
|  2 | yy2  |  *** |

CREATE TABLE `phone` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `phone_number` char(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `phone_number` (`phone_number`)
)

CREATE TABLE `phone_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT NULL,
  `phone_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `phone_id` (`phone_id`),
  CONSTRAINT `phone_user_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`),
  CONSTRAINT `phone_user_ibfk_2` FOREIGN KEY (`phone_id`) REFERENCES `phone` (`id`)
)
"""

import requests
import random
import time
import MySQLdb
from multiprocessing.dummy import Pool

class OfoMysql(object):
    def __init__(self, user=None, phonenumber=None):
        self.user = user
        self.phone = phonenumber
        self.conn = None
        self.cursor = None
        self.phone_id = None
        self.user_id = None

    def connect(self):
        try:
            conn = MySQLdb.Connect(
                host="192.168.120.200",
                port=3306,
                user="root",
                passwd="123456",
                db="ofo",
                charset="utf8"
            )
            conn.autocommit(False)
            self.conn = conn
            self.cursor = self.conn.cursor()
        except Exception, e:
            print e
            exit(1)

    def close_conn(self):
        self.cursor.close()
        self.conn.close()

    def get_inviteKey(self):
        # 返回用户名和key
        sql_search_inviteKey = "select username,inviteKey from user where status=1;"
        self.cursor.execute(sql_search_inviteKey)
        return self.cursor.rowcount, self.cursor.fetchall()

    def check_exist_phone(self):
        sql_search_phone = "select count(1) from phone where phone_number='{0}';".format(self.phone)
        self.cursor.execute(sql_search_phone)
        # 注意，使用 count(*)时，影响的行数 cursor.rowcount 一直为1，不管是否有数据和有几行数据。
        # mysql > select count(*) from gg where xx = '11';
        # +----------+
        # | count(*) |
        # +----------+
        # | 0 |
        # +----------+
        # 1 row in set(0.00sec)
        #  或者
        # +----------+
        # | count(*) |
        # +----------+
        # | 3 |
        # +----------+
        # 1 row in set(0.02 sec)

        count = self.cursor.fetchall()[0][0]

        # 如果该号码已经在表phone中存在
        if count == 1:
            return True
        # 如果该号码在表phone中不存在
        if count == 0:
            return False

    def check_conn(self):
        import traceback
        try:
            self.cursor.execute("select 1 from dual;")
        except MySQLdb.OperationalError:
            # 因为长时间等待，mysql连接超时，需要重新连接
            self.connect()
        else:
            pass

    def add_phone(self):
        # 如果之前没有给该号码发送信息
        sql_add_phone = "insert into phone(phone_number) values('{0}');".format(self.phone)
        try:
            self.cursor.execute(sql_add_phone)
            self.conn.commit()
        except Exception, e:
            print e
        if self.cursor.rowcount != 1:
            print "table phone:  insert phone {0}fail".format(self.phone)

    def check_exist_phone_user_rel(self):
            sql_search_phone_id = "select id from phone where phone_number='{0}';".format(self.phone)
            sql_search_user_id = "select id from user where username='{0}';".format(self.user)
            self.cursor.execute(sql_search_phone_id)
            self.phone_id = self.cursor.fetchall()[0][0]
            self.cursor.execute(sql_search_user_id)
            self.user_id = self.cursor.fetchall()[0][0]

            # 判断是否在表phone_user中存在关联
            sql_search_phone_user = "select count(1) from phone_user where user_id={0} and phone_id={1};".\
                format(self.user_id, self.phone_id)
            self.cursor.execute(sql_search_phone_user)
            count = self.cursor.fetchall()[0][0]
            if count == 1:
                return True
                # print "{0}: {1}已经发送过".format(self.user, self.phone)
            # 如果该phone与user没有关联，表示之前该用户没有给该phone发送
            if count == 0:
                return False
                # self.add_user_phone_rel(user_id, phone_id)

    # 在phone_user表中添加记录
    def add_phone_user_rel(self):
        sql_add_phone_user = "insert into phone_user (user_id, phone_id) values({0},{1});"\
            .format(self.user_id, self.phone_id)
        self.cursor.execute(sql_add_phone_user)
        self.conn.commit()
        if self.cursor.rowcount != 1:
            print "table phone_user:  insert phone {0}  {1} fail".format(self.user, self.phone)


def ofo(username, inviteKey, phonenumber):
    """
    执行ofo邀请程序
    """
    ofo_url = "https://activity.api.ofo.com/ofo/Api/aff"
    data = {
        "inviteKey": inviteKey,
        "tel": phonenumber
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87\
                      Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded",
        "Connection": "Keep-Alive"
    }
    r = requests.post(ofo_url, data=data, headers=headers)

#    r.json的内容
#     {
#     "errorCode": 200,
#     "msg": "领取成功~请到【我的钱包】中查看~",
#     "values": {
#         "isNewuser": 1
#     }
# }

#    errorCode为50004时，提示 操作过于频繁

    if r.json().get('values').get('isNewuser') == 1:
        print "{0} {1} 发送邀请成功".format(username, phonenumber)
    elif r.json().get('errorCode') == 50004:
        print r.json().get('msg')
        time.sleep(3700)
    else:
        print "{0} {1}".format(username, phonenumber) + r.text

def phonenumber_random():
    # 生成电话号码
    num_start = ['134', '135', '136', '137', '138', '139', '150', '151', '152', '158', '159', '157', '182', '187',
                '188','147', '130', '131', '132', '155', '156', '185', '186', '133', '153', '180', '189']
    phonenumber = random.choice(num_start) + ''.join([str(random.randint(0, 9)) for _ in range(8)])
    return phonenumber

def do(username, inviteKey, phonenumber):

    ofomysql = OfoMysql(phonenumber=phonenumber)
    ofomysql.connect()

    # 如果该号码不在phone表中
    if not ofomysql.check_exist_phone():
        ofo(username, inviteKey, phonenumber)
        # 有时候长时间等待后，mysql连接会断开，此时需要检测mysql连接
        ofomysql.check_conn()
        ofomysql.user = username
        ofomysql.add_phone()
        ofomysql.check_exist_phone_user_rel()
        ofomysql.add_phone_user_rel()
    # 如果该号码在phone表中
    if ofomysql.check_exist_phone():
        ofomysql.user = username
        # 如果用户和该号码不存在关联
        if not ofomysql.check_exist_phone_user_rel():
            ofo(username, inviteKey, phonenumber)
            # 有时候长时间等待后，mysql连接会断开，此时需要检测mysql连接
            ofomysql.check_conn()
            ofomysql.add_phone_user_rel()
        # 如果用户和该号码存在关联
        if ofomysql.check_exist_phone_user_rel():
            pass

def main(username, inviteKey):
    while True:
        phonenumber = phonenumber_random()
        do(username, inviteKey, phonenumber)
        time.sleep(random.randint(65, 85))


if __name__ == '__main__':

    # 先查出user和inviteKey
    ofomysql = OfoMysql()
    ofomysql.connect()
    rownumber, user_key = ofomysql.get_inviteKey()
    ofomysql.close_conn()

    pool = Pool(rownumber)
    for username, inviteKey in user_key:
        pool.apply_async(main, (username, inviteKey, ))
        #pool.apply_async(main, (ofomysql1, 'xiaolingling', 'ca0e2a58032dbd7dc846ec58c7033206', phonenumber,))

    pool.close()
    pool.join()

