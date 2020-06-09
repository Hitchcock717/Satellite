# -*- coding: utf-8 -*-
'''
    SSRP推荐平台之作者合作关系 --- 作者两两合作
'''
import re
from SSRP_recommend_data import *
from backdoor.analysis.SSRP_cooperation_analysis import CooperateAnalysis


class AuthorRecommend(object):

    def __init__(self, region):
        self.data = GetRecommendResult().get_recom_result(region)

    def filter_data(self):
        recom_data = self.data[2]  # spider_data中的日期格式不统一
        oldest, latest = [], []
        for data in recom_data:
            if re.search('^2019|^2020', data['date']):
                latest.append(data['author'])
            else:
                oldest.append(data['author'])
        return oldest, latest

    def build_oldest_data(self):
        old_author = self.filter_data()[0]
        two_aus, more_aus = [], []
        for old in old_author:
            if len(old.split(' ')) == 2:
                two_aus.append(old)
            elif len(old.split(' ')) > 2:
                more_aus.append(old)
            else:
                continue
        return two_aus, more_aus

    def build_latest_data(self):
        new_author = self.filter_data()[1]
        two_aus, more_aus = [], []
        for new in new_author:
            if len(new.split(' ')) == 2:
                two_aus.append(new)
            elif len(new.split(' ')) > 2:
                more_aus.append(new)
            else:
                continue
        return two_aus, more_aus

    def build_oldest_relation(self):
        two_aus, more_aus = self.build_oldest_data()
        cooper = CooperateAnalysis()
        cooper_data = cooper.prepare_data(two_aus, more_aus)
        # print(cooper_data)
        return cooper_data

    def build_latest_relation(self):
        two_aus, more_aus = self.build_latest_data()
        cooper = CooperateAnalysis()
        cooper_data = cooper.prepare_data(two_aus, more_aus)
        # print(cooper_data)
        return cooper_data

    def monitor_new_relation(self):
        old_relation = self.build_oldest_relation()
        late_relation = self.build_latest_relation()
        new_cooperation = set()

        import time
        start = time.time()
        for new in late_relation:
            for old in old_relation:
                if new[0] == old[0] and new[1] != old[1]:
                    new_cooperation.add(new)
                else:
                    continue
        end = time.time()
        # print(new_cooperation)
        # print('监测合作关系变化耗费时长为%s' % (end - start))
        return new_cooperation

    def recommend(self):
        authors = list(self.monitor_new_relation())
        recom_data = self.data[2]
        recommend = []

        import time
        start = time.time()
        for au in authors:
            for data in recom_data:
                if au[0] and au[1] in data['author'].split(' '):
                    recommend.append(data)
                else:
                    continue

        recommend = GetRecommendResult().drop_duplicates(recommend)
        # print(recommend)
        end = time.time()
        print('推荐方法一耗费时长为%s' % (end - start))
        return recommend


if __name__ == '__main__':
    au = AuthorRecommend()
    au.recommend()
