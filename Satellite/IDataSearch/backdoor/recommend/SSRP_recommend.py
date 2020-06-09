# -*- coding: utf-8 -*-
'''
    SSRP推荐平台之汇总推荐结果
    tips: 筛选权重确定问题
'''
from SSRP_recomemnd_relation import *
from SSRP_recommend_fund import *
from SSRP_recommend_topic import *
from SSRP_recommend_data import *


class SSRPRecommend(object):

    def __init__(self, region):
        self.au = AuthorRecommend(region)
        self.fu = FundRecommend(region)
        self.to = TopicRecommend(region)
        self.get = GetRecommendResult()
        self.csvname = './backdoor/recommend/recommend_data.csv'

    def pool_recommend_data(self):
        import time
        start = time.time()
        rec1 = self.au.recommend()
        rec2 = self.fu.recommend()
        rec3 = self.to.recommend()

        rec1.extend(rec2)
        rec1.extend(rec3)

        rec = self.get.drop_duplicates(rec1)
        end = time.time()
        print(len(rec))
        print('推荐文章总耗时时长为%s' % (end - start))

        # 权重靠人工经验确定
        # 三种方法按照实验结果好坏设置weight --- 3:6:1

        try:
            # 暂时随机抽取
            import random
            import pandas as pd
            choice = random.sample(rec, 10)
            dataframe = pd.DataFrame(choice)
            dataframe.drop(columns=['highlight'])
            print(dataframe)
            dataframe.to_csv(self.csvname, index=False, sep=',', encoding='utf-8')
            print('data saved')
        except Exception as e:
            print('存储推荐数据报错: %s' % e)
