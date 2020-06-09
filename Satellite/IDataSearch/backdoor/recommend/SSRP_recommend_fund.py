# -*- coding: utf-8 -*-
'''
    SSRP推荐平台之按基金项目推荐
'''
import re
from SSRP_recommend_data import *


class FundRecommend(object):

    def __init__(self, region):
        self.data = GetRecommendResult().get_recom_result(region)

    def filter_data(self):
        recom_data = self.data[2]  # spider_data中的日期格式不统一
        oldest, latest = [], []
        for data in recom_data:
            if re.search('^2019|^2020', data['date']):
                if data['fund'] == 'nan':
                    continue
                else:
                    latest.append(data['fund'])
            else:
                if data['fund'] == 'nan':
                    continue
                else:
                    oldest.append(data['fund'])
        return oldest, latest

    def recommend(self):
        old, new = self.filter_data()
        recom_data = self.data[2]
        repeat_fund = list(set(old).intersection(set(new)))
        recommend = []
        import time
        start = time.time()
        for fund in repeat_fund:
            for data in recom_data:
                if fund == data['fund']:
                    recommend.append(data)
                else:
                    continue

        recommend = GetRecommendResult().drop_duplicates(recommend)
        # print(recommend)
        end = time.time()
        print('推荐方法二耗费时长为%s' % (end - start))
        return recommend


if __name__ == '__main__':
    fu = FundRecommend()
    fu.recommend()
