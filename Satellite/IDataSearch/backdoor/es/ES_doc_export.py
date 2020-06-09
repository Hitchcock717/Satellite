#!/usr/bin/env python
# -*-coding:utf-8-*-
'''
    目的：清洗ES文档检索结果，并导出至.csv文件
    TODO: 为了达到每日推荐的目标，需要：
                                    收集前一周期（一般为7天）0：00 - 24：00的搜索数据，放入模型筛选推荐文章
                                    在翌日设置8：00定时推送推荐信息

    tips: 后续论文推荐方法: (1) 寻找新的连通分量；
                          (2) 寻找资助基金；
                          (3) 历史主题分布；
          数据源: (1) 用户历史搜索领域——>kws定位, 另爬取；
                （2) 用户历史搜索文章——>检索结果定位；
    改进: Num设置 根据数据爬取进度修改
'''
import os
import pandas as pd
from ES_doc_retrieve import *


class DocExportES(object):

    def __init__(self, index_name, ip):
        self.doc = DocRetireveES(index_name, ip)


    # 获取上周日期
    def get_week(self):
        import datetime
        today = datetime.date.today()
        sevenday = datetime.timedelta(days=7)
        lastweek = today - sevenday
        return lastweek

    # 获取上月日期
    def get_month(self):
        import datetime
        today = datetime.date.today()
        thirtyday = datetime.timedelta(days=30)
        lastmonth = today - thirtyday
        return lastmonth

    # 记录搜索时间
    def get_time(self):
        # from datetime import datetime
        # dt = datetime.now()
        # cur_time = dt.strftime('%Y-%m-%d %H:%M:%S')
        cur_time = ('%s 23:14:23' % self.get_week())  # 测试
        return cur_time

    # 简单搜索结果
    def get_data(self, search_field, kws, file):
        basic_data = self.doc.basic_search(search_field, kws)
        time = self.get_time()
        res = basic_data[1]
        df = pd.DataFrame(res)
        df['log'] = pd.to_datetime(time)
        print(df['log'])
        df.to_csv(file, mode='a+')

    # 高级搜索结果
    def get_more_data(self, in_fields, in_kws, ex_fields, ex_kws, date_field, start, end, in_method, file):
        advance_data = self.doc.advance_search(in_fields, in_kws, ex_fields, ex_kws, date_field, start, end, in_method)
        time = self.get_time()
        res = advance_data[1]
        df = pd.DataFrame(res)
        df['log'] = pd.to_datetime(time)
        df.to_csv(file, mode='a+')

    # 正则搜索结果
    def get_reg_data(self, in_fields, in_reg, ex_fields, ex_reg, date_field, start, end, in_method, file):
        regex_data = self.doc.advance_search_with_regexp(in_fields, in_reg, ex_fields, ex_reg, date_field, start, end, in_method)
        time = self.get_time()
        res = regex_data[1]
        df = pd.DataFrame(res)
        df['log'] = pd.to_datetime(time)
        df.to_csv(file, mode='a+')

    # 筛选出一个周期的数据 用作后续推荐
    def get_range_data(self, file, file2, num):
        search = pd.read_csv(file)
        search['log'] = pd.to_datetime(search['log'])
        last = self.get_week()

        from datetime import datetime
        dt = datetime.now()
        cur_time = dt.strftime('%Y-%m-%d')

        # 一周内的搜索结果汇总
        search = search[(search['log'] >= pd.to_datetime('%s 00:00:00' % last)) &
                        (search['log'] < pd.to_datetime('%s 00:00:00' % cur_time))]

        count = len(search.iloc[:, 0])-1  # index=0,列名
        if count > num:  # 设置最低推荐分析源数量: 大于则保存;小于则补充
            search.to_csv(file2)
        else:
            # 范围扩大至一个月
            last = self.get_month()
            search = search[(search['log'] >= pd.to_datetime('%s 00:00:00' % last)) &
                            (search['log'] < pd.to_datetime('%s 00:00:00' % cur_time))]
            search.to_csv(file2)


if __name__ == "__main__":
    index = 'cnki_doc'
    localhost = '127.0.0.1'
    os.chdir('/Users/felix_zhao/Desktop')
    file = 'cnki_doc1.csv'
    file2 = 'today.csv'
    doc = DocExportES(index, localhost)

    num = 100  # 根据数据爬取进度修改
    doc.get_range_data(file,file2,num)
    # ***************** 测试简单搜索[单字段] ***************** #
    basic_field = 'kws'
    basic_kws = '氨基酸'
    # doc.get_data(basic_field, basic_kws, file)

    # ***************** 测试简单搜索[多字段] ***************** #
    multi_fields = ['title', 'kws']
    multi_kws = '氨基酸'
    # doc.get_data(multi_fields, multi_kws, file)

    # ***************** 测试高级搜索[与或非] ***************** #
    #  -------------------------------------------------
    # | fields: list                                    |
    # | kws: str                                        |
    # | date: str                                       |
    # | start, end: YYYY-MM-DD                          |
    # | in_method: "1"->must; other(default 2)->should  |
    #  -------------------------------------------------

    include_fields = ["kws"]
    include_kws = "氨基酸"
    exclude_fields = [""]
    exclude_kws = ""
    date = "date"
    start = "1900-01-01"
    end = "2020-01-01"
    in_method = "2"
    # doc.get_more_data(include_fields, include_kws, exclude_fields, exclude_kws, date, start, end, in_method, file)

    # ***************** 测试高级搜索[正则] ***************** #
    #  -------------------------------------------------
    # | fields: list                                    |
    # | reg: regexp                                        |
    # | date: str                                       |
    # | start, end: YYYY-MM-DD                          |
    # | in_method: "1"->must; other(default 2)->should  |
    #  -------------------------------------------------

    inreg_fields = ["kws"]
    in_reg = ".*酸"
    exreg_fields = [""]
    ex_reg = ""
    date_reg = "date"
    start_reg = "1900-01-01"
    end_reg = "2020-01-01"
    in_method_reg = "2"
    # doc.get_reg_data(inreg_fields, in_reg, exreg_fields, ex_reg, date_reg, start_reg, end_reg, in_method_reg, file)