#!/usr/bin/env python
# -*-coding:utf-8-*-
'''
    目的: 公用类----连接ES
'''

from elasticsearch import Elasticsearch


class Connect2ES(object):

    def __init__(self, index_name, ip):
        """
        :param index_name: 索引名称
        :param index_type: 索引类型
        """
        self.index_name = index_name
        # self.index_type = index_type ES7已经移除type

        # 无用户名密码状态
        self.es = Elasticsearch([ip])

        # 用户名密码状态
        # self.es = Elasticsearch([ip],http_auth('elastic','password',port=9200)
