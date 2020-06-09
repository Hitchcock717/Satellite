# -*- coding: utf-8 -*-
'''
    SSRP演示平台之公用付费代理ip
'''

import os
from urllib import request
import urllib.request
from .user_agent import *
import random


class AbuyunProxy(object):

    def urllib_proxy_settings(self):
        # 代理服务器
        proxyHost = "http-dyn.abuyun.com"
        proxyPort = "9020"

        # 代理隧道验证信息
        proxyUser = "HSX0Z57864C177MD"
        proxyPass = "DA051F1C3895DFF1"
        
        proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
            "host": proxyHost,
            "port": proxyPort,
            "user": proxyUser,
            "pass": proxyPass,
        }

        proxy_handler = urllib.request.ProxyHandler({
            "http": proxyMeta,
            "https": proxyMeta,
        })

        return proxyMeta, proxy_handler

    def requests_proxy_settings(self):
        proxyMeta = self.urllib_proxy_settings()
        proxies = {
            "http": proxyMeta,
            "https": proxyMeta
        }

        return proxies


class CommonSettings(object):

    def set_common_headers(self):

        # headers = {
        #     'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
        # }

        headers = {
            'User-Agent': random.choice(USER_AGENT)
        }

        return headers

    def set_common_keyword(self):

        keywords = '丙氨酸'

        # keywords = ['丙氨酸', '精氨酸', '天冬酰胺', '天冬氨酸', '半胱氨酸', '谷氨酸', '谷氨酰胺', '甘氨酸', '组氨酸', '羟（基）脯氨酸', '异亮氨酸']

        return keywords

    def set_common_pagesize(self):

        pagesize = 20

        return pagesize

    def set_common_output(self):

        os.chdir('/Users/felix_zhao/Desktop/sourcetree_file/SSRP-Dev/IData/IDataSearch/backdoor/data/spider_data')

        cnki_csv = 'cnki_data.csv'

        cqvip_csv = 'cqvip_data.csv'

        wf_csv = 'wanfang_data.csv'

        return cnki_csv, cqvip_csv, wf_csv

