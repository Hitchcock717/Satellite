# -*- coding: utf-8 -*-
'''
    SSRP推荐平台之获取公共推荐数据
'''

from backdoor.es.ES_doc_retrieve import DocRetireveES


# ******************* 获取推荐参数 ***************** #

def get_params():
    import sqlite3
    file_path = 'db.sqlite3'
    backdoor = sqlite3.connect(file_path)
    cursor = backdoor.cursor()
    backdoor.row_factory = sqlite3.Row
    cursor.execute('select job, email from backdoor_personal')
    rows = cursor.fetchall()
    region = rows[-1][0]
    email = rows[-1][1]
    return region, email

# ******************* 获取推荐数据 ***************** #


class GetRecommendResult(object):

    def __init__(self):
        # ES文档索引地址
        self.index = 'spider_data'  # 预先存储，后续更改index
        self.ip = '127.0.0.1'
        # self.region = '氨基酸'  # 暂定推荐领域

    def get_recom_result(self, multi_kws):
        doc = DocRetireveES(self.index, self.ip)
        multi_fields = ['abstract', 'kws', 'title', 'info', 'fund', 'source']  # 查询所有包含kws的字段
        results = doc.basic_search(multi_fields, multi_kws)
        query = results[0]
        counts = results[1]
        docs = results[2]
        return query, counts, docs

    def drop_duplicates(self, recommend):
        import operator
        for i in recommend:
            for j in recommend:
                if operator.eq(i,j):
                    recommend.remove(i)
                else:
                    continue
        return recommend

    # 日常在个人中心处随机推荐5篇
    def get_daily_recommend(self, region):
        data = self.get_recom_result(region)[2]
        import random
        choice = random.sample(data, 5)
        return choice


if __name__ == '__main__':
    get_params()
