# -*- coding: utf-8 -*-
'''
    SSRP推荐平台之自动发送邮件
'''
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import yagmail
from SSRP_recommend import SSRPRecommend
from SSRP_recommend_data import get_params


class YagSendMail(object):

    def __init__(self, region):
        self.csvname = SSRPRecommend(region).csvname
        self.main_email = '*************'
        self.back1 = '*************'
        self.group = [self.main_email, self.back1]

    def automatic_send_mail(self, email):
        yag = yagmail.SMTP(user="*************", password="*************", host="*************")
        content = ['自动邮件发送测试']
        try:
            yag.send(email, 'subject', content)
            print("邮件发送成功")
        except Exception as e:
            print(e)

    def automatic_send_group(self):
        yag = yagmail.SMTP(user="*************", password="*************", host="*************")
        content = ['自动邮件发送测试']
        try:
            yag.send(self.group, 'subject', content)
            print("邮件发送成功")
        except Exception as e:
            print(e)

    def automatic_send_attachment(self, email):
        yag = yagmail.SMTP(user="*************", password="*************", host="*************")
        import datetime
        today = datetime.date.today()
        title = '【' + str(today) + '】' + '每日推荐论文速递'
        content = ['详情请见附件']
        try:
            yag.send(email, title, content, [self.csvname])
            print("邮件发送成功")
        except Exception as e:
            print(e)

    def long_interval_send_mail(self, email):
        import time
        print('现在时间时间是：\n' + time.strftime('%H:%M:%S', time.localtime()))
        # 默认每天早上10点10分定时推送
        hour = 10
        minute = 25
        second = 00
        while True:
            current_time = time.localtime(time.time())
            if (current_time.tm_hour == hour) and (current_time.tm_min == minute) and (current_time.tm_sec == second):
                # SSRPRecommend(get_params()[0]).pool_recommend_data()
                print('时间到，开始自动发送邮件')
                time.sleep(1)
                self.automatic_send_attachment(email)

    # 每隔5分钟推荐
    def short_interval_send_mail(self, email):
        import time
        time_intvl = 1 * 60
        start_time = int(time.time())
        print(start_time)
        while True:
            end_time = int(time.time())
            cost_time = end_time - start_time
            # print(cost_time)
            if cost_time == time_intvl:
                SSRPRecommend(get_params()[0]).pool_recommend_data()
                print('时间到，开始自动发送邮件')
                time.sleep(1)
                self.automatic_send_attachment(email)
                start_time = end_time
                print('regular send email....%s' % time.ctime(start_time))


class SMTPSendMail(object):

    def automatic_send_mail(self):
        # 第三方 SMTP 服务
        mail_host = "*************"  # 设置服务器
        mail_user = "*************"  # 用户名
        mail_pass = "*************"  # 口令

        sender = '*************'
        receivers = ['*************']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱

        message = MIMEText('Python 邮件发送测试...', 'plain', 'utf-8')
        message['From'] = Header("菜鸟教程", 'utf-8')
        message['To'] = Header("测试", 'utf-8')

        subject = 'Python SMTP 邮件测试'
        message['Subject'] = Header(subject, 'utf-8')

        try:
            smtpObj = smtplib.SMTP()
            smtpObj.connect(mail_host, 465)  # 25 为 SMTP 端口号
            smtpObj.login(mail_user, mail_pass)
            smtpObj.sendmail(sender, receivers, message.as_string())
            print("邮件发送成功")
        except smtplib.SMTPException as e:
            print(e)
            print("Error: 无法发送邮件")


if __name__ == '__main__':
    yag = YagSendMail()
    yag.automatic_send_attachment()
    # smtp = SMTPSendMail()
    # smtp.automatic_send_mail()
