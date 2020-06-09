#！/usr/bin/env python
# _*_ coding:utf-8 _*_
'''
    目的: 从用户输入的论文标题提取相应位置上的关键名词，过滤后送入ES查询（规则为"与"）
    tips: 1.分词边界【加入自定义词表】
          2.过滤无意义名词
         TODO: 扩充专利型论文停用词表
    分词词表：粗粒度----电镜关键词词表
    停用词生成过滤词表：细粒度----科技术语词表（16w）
    停用词词表：包含哈工大、百度等停用词词表
    范畴词词表：自动筛选 + 人工过滤
'''


import os
import codecs
from nltk.tokenize import TweetTokenizer
from nltk.parse import stanford
from elasticsearch import Elasticsearch
import jieba


class KeywordRetrieveES(object):

    # **********************************start extract keyword******************************** #

    # stanford parser环境准备
    def __init__(self, index_name, ip):
        os.environ['STANFORD_PARSER'] = './stanford/stanford-parser.jar'
        os.environ['STANFORD_MODELS'] = './stanford/stanford-parser-3.9.1-models.jar'
        self.parser = stanford.StanfordParser(model_path="edu/stanford/nlp/models/lexparser/chinesePCFG.ser.gz")
        self.index_name = index_name
        # 无用户名密码状态
        self.es = Elasticsearch([ip])


    # 创建停用词表
    def stopwords(self, txt1):
        stopwords = [line.strip() for line in codecs.open(txt1, 'r', encoding='utf-8').readlines()]
        return stopwords

    # 创建过滤词表
    def filterwords(self, txt2):
        filterwords = [line.strip() for line in codecs.open(txt2, 'r', encoding='utf-8').readlines()]
        return filterwords

    # 导入自定义词表
    def seg_by_jieba(self, sentence):
        jieba.load_userdict("自定义分词词表.txt")
        seg = jieba.cut(sentence.strip(), cut_all=False)  # 精确模式
        return seg

    def test(self, sentence):
        tknzr = TweetTokenizer()
        sent = [tknzr.tokenize(sentence)]
        return sent

    def parse(self, sentence):
        sent = self.seg_by_jieba(sentence)
        res = self.parser.parse(sent)  # tree structure
        return res

    # 依存树可视化
    def draw(self, sentence):
        res = self.parse(sentence)
        for elem in res:
            elem.draw()

    def get_leave_structrue(self, sent):
        res_sentence = self.parse(sent)
        leaves_strucs = []
        for elem in res_sentence:
            for pos in elem.treepositions('leaves'):
                strucs = []
                pos_len = len(pos)
                for i in range(1, pos_len):
                    struc = elem[pos[:-i]].label()  # 逆序标注词性
                    strucs.append(struc)
                leaves_strucs.append(strucs)
        return leaves_strucs

    def get_leave_pos(self, res_sentence):
        words_pos = []
        for elem in res_sentence:
            for _, word_pos in elem.pos():
                words_pos.append(word_pos)
        return words_pos

    def get_all_property(self, sent, txt1, txt2):  # 获取单词，词性，结构
        src = sent[0]
        tar = list(sent[1])

        words = self.seg_by_jieba(src)
        words_pos = self.get_leave_pos(tar)

        words_NN_raw = []
        for word, word_pos in zip(words, words_pos):
            if word_pos == 'NN':
                words_NN_raw.append(word)

        stop = self.stopwords(txt1)
        filters = self.filterwords(txt2)
        words_NN = []
        for n in words_NN_raw:
            if n not in stop and filters:
                words_NN.append(n)
        print(words_NN)
        return words_NN

    # **********************************end extract keyword******************************** #


if __name__ == '__main__':
    index = 'cnki_term'
    ip = '127.0.0.1'
    sp = KeywordRetrieveES(index, ip)
    sentence = "管氏肿腿蜂产卵器感器的扫描电子显微镜观察"
    os.chdir('') # 自定义路径
    txt1 = '中文停用词表.txt'
    txt2 = '泛化词表.txt'
    parsed_sent = sp.parse(sentence)
    parsed_sent1 = [sentence, parsed_sent]
    sp.get_all_property(parsed_sent1, txt1, txt2)

