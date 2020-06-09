# -*- coding: utf-8 -*-
'''
    SSRP推荐平台之后台持续运行主函数
'''

from SSRP_send_mail import YagSendMail
from SSRP_recommend_data import get_params


class ForeverRun(object):

    def run(self):  # 长间隔入口
        YagSendMail(get_params()[0]).long_interval_send_mail(get_params()[1])

    def run2(self):  # 短间隔入口
        YagSendMail(get_params()[0]).short_interval_send_mail(get_params()[1])


if __name__ == '__main__':
    ForeverRun().run()

