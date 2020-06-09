# -*- coding: utf-8 -*-
'''
    SSRP分析平台之词云分析 --- 过滤高频关键词
'''

import codecs
import jieba.analyse
import jieba


class CloudAnalysis(object):

    def __init__(self):

        self.stop_path = './backdoor/corpus/stopwords.txt'
        self.num = 20

    def keyword_count(self, words):
        # 获取高频词
        counts = {}
        for word in words:
            if word not in counts:
                counts[word] = 1
            else:
                counts[word] += 1

        items = list(counts.items())

        items.sort(key=lambda x: x[1], reverse=True)  # key=lambda 元素: 元素[字段索引] 这里表示对元素第二个字段（频次）进行排序

        frequent = []

        if self.num > len(items):
            for i in range(len(items)):
                frequency = {}
                frequency['word'], frequency['count'] = items[i]
                print('{0:<10}{1:>5}'.format(frequency['word'], frequency['count']))
                frequent.append(frequency)
        else:
            for i in range(self.num):
                frequency = {}
                frequency['word'], frequency['count'] = items[i]
                print('{0:<10}{1:>5}'.format(frequency['word'], frequency['count']))
                frequent.append(frequency)

        return frequent

    def title_or_abstract_count(self, words):
        raw_words = ','.join(words)
        # 设置停用词
        jieba.analyse.set_stop_words(self.stop_path)
        # 获取关键词频率
        tags = jieba.analyse.extract_tags(raw_words, topK=self.num, withWeight=True)

        frequent = []

        for i in range(self.num):
            frequency = {}
            frequency['word'] = tags[i][0]
            frequency['count'] = round(tags[i][1]*100)
            import re
            if re.search('^[0-9]*$|^([0-9]{1,}[.][0-9]*)$', frequency['word']):
                print('No Number!')
            else:
                print('{0:<10}{1:>5}'.format(frequency['word'], frequency['count']))
                frequent.append(frequency)
        return frequent



