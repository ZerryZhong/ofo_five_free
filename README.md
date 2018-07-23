这里主要使用python刷ofo 5天免费骑行券，练习python多进程/线程和操作数据库。</br>
参考项目  https://github.com/linlin1988/ofo_five_free</br>

# 运行方式
1. 有mysql服务器</br>
2. 在mysql服务器中创建3张表</br>
```
CREATE TABLE `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(64) DEFAULT NULL,
  `inviteKey` varchar(64) DEFAULT NULL,
  `status` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `inviteKey` (`inviteKey`)
);

CREATE TABLE `phone` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `phone_number` char(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `phone_number` (`phone_number`)
);

CREATE TABLE `phone_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT NULL,
  `phone_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `phone_id` (`phone_id`),
  CONSTRAINT `phone_user_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`),
  CONSTRAINT `phone_user_ibfk_2` FOREIGN KEY (`phone_id`) REFERENCES `phone` (`id`)
);
```

3. 往user表中插入用户名和对应的inviteKey。用户名随意，inviteKey必须是正确的。</br>
   比如  insert into user(username,inviteKey) values('xx','xxxxxxxx');  </br>

4.更改ofo.py文件，将mysql服务器改为真实的信息</br>

            conn = MySQLdb.Connect(
                host="192.168.120.200",
                port=3306,
                user="root",
                passwd="123456",
                db="ofo",
                charset="utf8"
            )

5. python  ofo.py  执行脚本
```
xx1 18947365840 发送邀请成功
xx1 13240308641 发送邀请成功
xx2 18552465435 发送邀请成功
```

# 打开APP查看
我的钱包-优惠券
![优惠券](https://github.com/ZerryZhong/ofo_five_free/blob/master/ofo.jpg)

# 如何获得自己的invitekey

1. 电脑网页版打开  https://ofo-misc.ofo.com/pay/index.html#/ 进行登录 </br>
2. 登录后访问 https://ofo-misc.ofo.com/invite/index.html#/</br>
3. 打开浏览器开发者模式</br>
4. f5刷新页面</br>
5. 找到请求列表里的 inviteConfig 这一条，查看响应结果中的inviteKey</br>

如
```
{"errorCode":200,"msg":"操作成功","values":{"inviterName":"","inviteKey":"xxxxxxxx","isInviteGroup":0,"invitedNum":113252,"invitedPacketNum":56}}

```
