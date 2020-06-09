# -*- coding: utf-8 -*-
'''
    SSRP分析平台之主题分布分析 --- 中文文档分类[摘要]
'''

import jieba
from gensim import corpora, models


class ClassifyAnalysis(object):

    def __init__(self):
        self.stop_path = '/Users/felix_zhao/Desktop/sourcetree_file/SSRP-Dev/IData/IDataSearch/backdoor/corpus/stopwords.txt'
        # self.num_topics = 5  # 主题数
        # self.num_words = 10  # 各主题下显示词数

        self.texts = [
                        '美国教练坦言，没输给中国女排，是输给了郎平',
                        '美国无缘四强，听听主教练的评价',
                        '中国女排晋级世锦赛四强，全面解析主教练郎平的执教艺术',
                        '为什么越来越多的人买MPV，而放弃SUV？跑一趟长途就知道了',
                        '跑了长途才知道，SUV和轿车之间的差距',
                        '家用的轿车买什么好'
                     ]

    def get_stopwords(self):
        stopwords = []
        with open(self.stop_path, 'r', encoding="utf8") as f:
            for line in f.readlines():
                stopwords.append(line.strip())

        import string
        punctuations = [i for i in string.punctuation]
        alphabet = [chr(i) for i in range(97, 123)]
        capital = [chr(i) for i in range(65, 91)]
        setStopwords = set(punctuations + stopwords + alphabet + capital)

        return setStopwords

    def prepare_data(self, texts):
        stopwords = self.get_stopwords()
        data = [[word for word in jieba.lcut(text) if word not in stopwords and word != ' '] for text in texts]
        # print(data)
        return data

    def build_topics_model(self, texts, num_topics, num_words):
        words = self.prepare_data(texts)
        dictionary = corpora.Dictionary(words)
        corpus = [dictionary.doc2bow(word) for word in words]
        lda = models.ldamodel.LdaModel(corpus=corpus, id2word=dictionary, num_topics=num_topics)
        topics = [topic for topic in lda.print_topics(num_words=num_words)]
        # print('简单LDA分析后显示的主题分布为: %s' % topics)
        # print('主题推断为: %s' % lda.inference(corpus))
        return topics

    def simple_LDA_analysis(self, texts, num_topics, num_words):
        topics = self.build_topics_model(texts, num_topics, num_words)
        lda = []
        for topic in topics:
            chart_data = {}
            chart_data['columns'] = ['主题词', '出现频次']
            lda_topic = []
            for top in topic[1].split('+'):
                data = {}
                data['出现频次'] = float(top.strip().split('*')[0])
                data['主题词'] = top.strip().split('*')[1].strip('"')

                bin = ['ï', '¿']
                import re
                if data['主题词'] not in bin and not re.search(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])", data['主题词']):
                    lda_topic.append(data)
                else:
                    print('主题词格式不符合')
            chart_data['rows'] = lda_topic
            lda.append(chart_data)
        print(lda)
        return lda
