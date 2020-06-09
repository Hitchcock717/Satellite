#！/usr/bin/env python
# _*_ coding:utf-8 _*_
'''
    目的: 训练论文标题中范畴词及其他停用词汇 + 手工筛选
    TODO: 更新——>StanfordCoreNLP, 替代jieba
    tips: 人工筛选策略----从泛化词表筛选出意义词汇，将其加入至术语过滤词表
    改进: 阈值依靠经验设定，过低将导致关键词噪声大，通常为100
'''

from nltk.parse import stanford
import codecs
import jieba
import jieba.posseg
import os
import re


    # ********************************** start train stopword ******************************** #


class StopwordsTrainES(object):

    # stanford parser环境准备
    def __init__(self):
        os.environ['STANFORD_PARSER'] = './stanford/stanford-parser.jar'
        os.environ['STANFORD_MODELS'] = './stanford/stanford-parser-3.9.1-models.jar'
        self.parser = stanford.StanfordParser(model_path="edu/stanford/nlp/models/lexparser/chinesePCFG.ser.gz")

    # 创建停用词表---*术语表成为停用词表*
    def stopterms(self, txt):
        stopterms = [line.strip() for line in codecs.open(txt, 'r', encoding='utf-8').readlines()]
        return stopterms

    def seg(self, file, file3):
        jieba.load_userdict(file3)
        fin = codecs.open(file, 'r', encoding='utf-8').read()
        words = jieba.cut(fin)

        # ************* 以下为基于词性位置的改进版 ************** #
        # 使用时无需对照术语过滤表，直接输出即可
        # 阈值设置不变

        content = ','.join(words)
        content1 = re.sub(', ,', '', content)
        content2 = content1.strip()
        content3 = re.sub(' ,','', content2)
        content4 = re.sub(',\n,', '\n', content3)
        content5 = content4.split('\n')
        # 基于经验，泛化词最常出现的位置为首尾部【首部: 基于/针对/关于 尾部: 观察/作用/影响/分析/功能/情况...】
        general = []
        for cont in content5:
            cont_li = cont.split(',')
            head = cont_li[0]
            tail = cont_li[-2]
            general.append(head)
            general.append(tail)

        for g in general:
            if re.search(r'[0-9]+|\(|\)|[a-zA-Z]+|[0a-zA-Z-9]*', g):
                general.remove(g)
        # print(general)
        return general

        # ************* 以上为基于词性位置的改进版 ************** #

    # 词频统计
    def tf_count(self, file, txt, num):
        data = self.seg(file, txt)
        counts = {}
        for word in data:
            if len(word) == 1:
                continue
            else:
                counts[word] = counts.get(word, 0) + 1  # dict.get(key, default=None) get()方法返回指定键的值

        items = list(counts.items())
        items.sort(key=lambda x: x[1], reverse=True)  # key=lambda 元素: 元素[字段索引] 这里表示对元素第二个字段（频次）进行排序

        candidate = []  # 高频词
        for i in range(len(items)):
            word, count = items[i]
            # print('{0:<10}{1:>5}'.format(word, count))
            if count >= num:
                candidate.append(word)
        # print(candidate)
        return candidate

    def tag(self, file, txt, num):
        raw_words = self.tf_count(file, txt, num)
        word_n = []
        for word in raw_words:
            tag = jieba.posseg.cut(word)
            for w in tag:
                if w.flag == 'NN' or 'NP' or 'VN' or 'AN':
                    word_n.append(w.word)
        print(word_n)
        return word_n

    def filter(self, file, txt, num):
        nouns = self.tag(file, txt, num)
        stops = self.stopterms(txt)
        filters = []
        for n in nouns:
            if n not in stops:
                filters.append(n)
        print(filters)
        return filters

    def output(self, file,  file2, txt, num):
        filters = self.filter(file, txt, num)
        fin = codecs.open(file2, 'r', encoding='utf-8')
        fout = codecs.open(file2, 'a+', encoding='utf-8')
        for fi in fin.readlines():
            for f in filters:
                if f != fi:
                    fout.write(f + '\n')
        fout.flush()
        fout.close()

    # ************* 以下为基于词性位置的改进版 ************** #

    def output_2(self, file,  file2, txt, num):
        filters = self.tag(file, txt, num)
        fin = codecs.open(file2, 'r', encoding='utf-8')
        fout = codecs.open(file2, 'a+', encoding='utf-8')
        # **** 初始化 *** #
        for f in filters:
            fout.write(f + '\n')
        fout.flush()
        fout.close()

    # ************* 以上为基于词性位置的改进版 ************** #

    # ********************************** end train stopword ******************************** #


if __name__ == "__main__":
    st = StopwordsTrainES()
    file = '标题测试集.txt'
    file2 = '泛化词表.txt'
    file3 = '自定义分词词表.txt'
    txt = '术语过滤词表.txt'
    st.output_2(file, file2, txt, 100)
