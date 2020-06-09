# -*- coding: utf-8 -*-
'''
    SSRP分析平台之文献分析自定义参数及测试运行主函数
'''
from SSRP_cooperation_analysis import *
from SSRP_classify_analysis import *
from SSRP_network_analysis import *
from SSRP_cloud_analysis import *


def parameter():
    # classify analysis
    num_topics = 5  # 主题数
    num_words = 10  # 各主题下显示词数

    # cloud analysis
    num_cloud = 20  # 词云显示次数

    # network analysis
    min_count = 1  # 最小词频
    window_size = 5
    word_demension = 10

    return num_topics, num_words, num_cloud, min_count, window_size, word_demension


def main():
    """
    test function for each analysis platform
    :param:
        two_aus, more_aus ---> author couple (2 or more)
        texts ----> abstract doc array
        words ----> 1. keyword array; 2. title or abstract doc array
    :return:
        list[dict{}]
    """
    CooperateAnalysis().build_au_relation(two_aus, more_aus)
    ClassifyAnalysis().simple_LDA_analysis(texts, num_topics, num_words)
    WordVector().build_network_scipy_data()
    CloudAnalysis().keyword_count(words)
    CloudAnalysis().title_or_abstract_count(words)
