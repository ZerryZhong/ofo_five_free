这里主要使用python刷ofo 5天免费骑行券，练习python多进程/线程和操作数据库。
参考项目  https://github.com/linlin1988/ofo_five_free


![优惠券](https://github.com/liuhuakun/BrushShots/blob/master/1.PNG)

如何获得自己的invitekey
电脑网页版打开 https://ofo-misc.ofo.com/pay/index.html#/ 进行登录 
登录后访问 https://ofo-misc.ofo.com/invite/index.html#/
打开浏览器开发者模式
f5刷新页面
找到请求列表里的 inviteConfig 这一条，查看响应结果中的inviteKey
如

{"errorCode":200,"msg":"操作成功","values":{"inviterName":"","inviteKey":"xxxxxxxx","isInviteGroup":0,"invitedNum":113252,"invitedPacketNum":56}}
