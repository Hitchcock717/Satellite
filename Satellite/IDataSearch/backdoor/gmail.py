# -*- coding: utf-8 -*-
'''
    SSRP演示平台之邮件提醒
'''

import yagmail


class SendMail(object):

    def __init__(self):
        self.to_email = '************'
        self.from_email = '************'
        self.password = '************'
        self.back1 = '************'
        self.group = []

    def automatic_send_email(self, project, keywords):
        yag = yagmail.SMTP(user=self.from_email, password=self.password, host="*************")
        title = '项目【' + project + '】爬取任务已完成, 请登录平台开始检索'
        piece = '项目爬虫目标词为: ' + ','.join(keywords)
        content = [piece, '找到项目仓库---待办项目可一键发起检索', '祝好, from SSRP平台']
        try:
            yag.send(self.to_email, title, content)
            print("邮件发送成功")
        except Exception as e:
            print(e)
