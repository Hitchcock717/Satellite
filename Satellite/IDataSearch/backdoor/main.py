# -*- coding: utf-8 -*-
'''
    SSRP演示平台之爬虫文件导出 + ESjson格式转换 + ES数据插入全流程主运行函数
    tips: 暂时只有cnki爬虫测试过
'''

import sys
import os
import sqlite3
from scrapy.cmdline import execute


# 使用scrapy爬虫时的运行命令(暂时移除)
def execute_spider(name, word):
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    execute(["scrapy", "crawl", name, '-a', 'keyword='+word])


# 主函数
def cnki_main(search_word):
    es = ESConnect2Data()
    es.execute_cnki_spider(search_word)
    es.export2csv()
    es.cnki_convert2json()
    es.cnki_insert2data()


def cqvip_main(search_word):
    es = ESConnect2Data()
    es.execute_cqvip_spider(search_word)
    es.cqvip_convert2json()
    es.cqvip_insert2data()


def wf_main(search_word):
    es = ESConnect2Data()
    es.execute_wf_spider(search_word)
    es.wf_convert2json()
    es.wf_insert2data()


class ESConnect2Data(object):

    # 数据模块自定义设置中心
    def __init__(self):
        # ****** 文件设置 ****** #
        self.sqldb_path = './data/spider_data/spider_data.sqlite'
        self.cnki_csv_path = './data/spider_data/spider_data.csv'
        self.cqvip_csv_path = './data/spider_data/cqvip_data.csv'
        self.wf_csv_path = './data/spider_data/wanfang_data.csv'
        self.cnki_json_path = './data/spider_data/doc_json.txt'
        self.cqvip_json_path = './data/spider_data/cqvip_json.txt'
        self.wf_json_path = './data/spider_data/wanfang_json.txt'

        # ****** 数据表设置 ****** #
        self.table_name = 'cnki'

        # ****** ES设置 ****** #
        self.index = 'spider_data'  # new index
        self.ip = '127.0.0.1'

    def execute_cnki_spider(self, search_word):
        from .data.SSRP_CNKIspider import CnkispaceSpider
        CnkispaceSpider().get_candidate_words(search_word)
        print('***************** 知网数据已存入爬虫sqlite数据库! *****************')

    def execute_cqvip_spider(self, search_word):
        from .data.SSRP_CQVIPspider import CqvipSpider
        CqvipSpider().pandas_save_data(search_word)
        print('***************** 维普数据已存入爬虫csv文件! *****************')

    def execute_wf_spider(self, search_word):
        from .data.SSRP_WFspider import WFdataspider
        WFdataspider().pandas_save_data(search_word)
        print('***************** 万方数据已存入爬虫csv文件! *****************')

    def export2csv(self):
        try:
            import pandas as pd
            con = sqlite3.connect(self.sqldb_path)
            table = pd.read_sql('select * from ' + self.table_name, con)
            table.to_csv(self.cnki_csv_path)
            con.close()
            print('***************** 知网爬虫sqlite数据库已完成文件导出! *****************')
        except Exception as e:
            print(e)

    def cnki_convert2json(self):
        from data.ES_doc_convert import ESDocConvert
        ESDocConvert().convert2json(self.cnki_csv_path, self.cnki_json_path)
        print('***************** 知网爬虫csv文件已转换成json格式! *****************')

    def cqvip_convert2json(self):
        from data.ES_doc_convert import ESDocConvert
        ESDocConvert().convert2json(self.cqvip_csv_path, self.cqvip_json_path)
        print('***************** 维普爬虫csv文件已转换成json格式! *****************')

    def wf_convert2json(self):
        from data.ES_doc_convert import ESDocConvert
        ESDocConvert().convert2json(self.wf_csv_path, self.wf_json_path)
        print('***************** 万方爬虫csv文件已转换成json格式! *****************')

    def cnki_insert2data(self):
        from es.ES_insert_data import Insert2ES
        Insert2ES(self.index, self.ip).insert_data(self.cnki_json_path)
        print('***************** 知网爬虫json文件已插入ES中! *****************')

    def cqvip_insert2data(self):
        from es.ES_insert_data import Insert2ES
        Insert2ES(self.index, self.ip).insert_data(self.cqvip_json_path)
        print('***************** 维普爬虫json文件已插入ES中! *****************')

    def wf_insert2data(self):
        from es.ES_insert_data import Insert2ES
        Insert2ES(self.index, self.ip).insert_data(self.wf_json_path)
        print('***************** 万方爬虫json文件已插入ES中! *****************')


if __name__ == '__main__':
    main()

