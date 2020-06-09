# -*- coding: utf-8 -*-
'''
    SSRP推荐平台之按历史研究主题推荐
    tips: 作者同名问题, 需构建知识图谱
'''
import re
from SSRP_recommend_data import *


class TopicRecommend(object):

    def __init__(self, region):
        self.data = GetRecommendResult().get_recom_result(region)
        self.pickle_path = './filter.pickle'
        self.term_filter = './backdoor/corpus/term_filters.txt'

    def filter_data(self):
        recom_data = self.data[2]  # spider_data中的日期格式不统一
        oldest, latest = [], []
        for data in recom_data:
            if re.search('^2019|^2020', data['date']):
                latest.append(data['title'])
            else:
                oldest.append(data['title'])
        return oldest, latest

    def build_topic_model(self):
        old, new = self.filter_data()
        from analysis.SSRP_classify_analysis import ClassifyAnalysis
        import time
        start = time.time()
        old_topics = ClassifyAnalysis().build_topics_model(old)
        new_topics = ClassifyAnalysis().build_topics_model(new)
        # print(old_topics)
        # print(new_topics)
        end = time.time()
        # print('主题模型构建耗时为%s' % (end - start))
        return old_topics, new_topics

    def get_topics(self):
        old_topics, new_topics = self.build_topic_model()
        old_topic_words, new_topic_words = [], []
        for old in old_topics:
            for word in old[1].split('+'):
                topic_word = word.strip().split('*')[1].strip('"')
                old_topic_words.append(topic_word)
        for new in new_topics:
            for word in new[1].split('+'):
                topic_word = word.strip().split('*')[1].strip('"')
                new_topic_words.append(topic_word)

        # print(old_topic_words)
        # print(new_topic_words)
        return old_topic_words, new_topic_words

    def get_recommend_data(self):
        old_topic_words, new_topic_words = self.get_topics()
        raw_candidates = list(set(new_topic_words).difference(set(old_topic_words)))
        # print('未筛选结果为%s' % raw_candidates)

        # 未筛选结果列表长度由主题模型的自定义参数决定, 上限为主题数*主题词数(目前设置的是5*10）
        import pickle
        fin = open(self.pickle_path, 'rb')
        filters = pickle.load(fin)

        if filters:
            # 自动筛选
            candidates = list(set(raw_candidates).difference(set(filters)))
            # print('自动筛选后结果为%s' % candidates)
        else:
            candidates = raw_candidates
            # print('过滤词表为空')

        finn = open(self.term_filter, 'r', encoding='utf-8').read()
        remove = []
        for candi in candidates:
            if candi not in finn.split('\n'):
                remove.append(candi)
                candidates.remove(candi)

        # 将剩余淘汰词加入过滤词表
        fw = open(self.pickle_path, 'ab')
        pickle.dump(remove, fw)
        fw.close()

        return candidates

    def recommend(self):
        proper = self.get_recommend_data()
        recom_data = self.data[2]
        recommend = []
        import time
        start = time.time()
        for pro in proper:
            for data in recom_data:
                if re.search(pro, data['kws']):
                    recommend.append(data)
                else:
                    continue

        recommend = GetRecommendResult().drop_duplicates(recommend)
        # print(recommend)
        end = time.time()
        print('推荐方法三耗费时长为%s' % (end - start))
        return recommend


if __name__ == '__main__':
    to = TopicRecommend()
    to.recommend()
