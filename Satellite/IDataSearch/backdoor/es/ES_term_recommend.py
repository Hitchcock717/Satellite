#!/usr/bin/env python
# -*-coding:utf-8-*-
'''
    目的：ES关键词检索----切分关键词后匹配 [prerequisite：Keyword不在ES中存储]

                    ----直接搜索对应索引 [prerequiste: Keyword在ES中存储]

'''
import time
import random
from elasticsearch import Elasticsearch
from elasticsearch import helpers


class TermRecommendES(object):

    def __init__(self, index_name, ip):
        self.index_name = index_name
        # 无用户名密码状态
        self.es = Elasticsearch([ip])

    # 测试index中文档情况
    def paraSearch(self):
        search = self.es.search(
                                index=self.index_name,
                                body={
                                        "query": {
                                                 "match_all":{}
                                        }
                                 }
        )
        print('\n查询所有文档\n', search)

    # 使用es.search
    def commonSearch(self, keywords1):
        search = {
                "query": {
                    "match": {
                        "name": keywords1
                    }
                }
            }
        '''
        Note：在这里返回的检索结果数量有两种设置方式：
        1.在es.search()中指定size参数值
        2.在search{}中的size对应字段
        '''
        start = time.time()
        searched = self.es.search(index=self.index_name, body=search, size=20)
        res = searched["hits"]["hits"]

        answers = []
        for hit in res:
            answer_dict = {}
            answer_dict['score'] = hit['_score'] / 100
            answer_dict['sim_term'] = hit['_source']['name']
            answer_dict['sim_subject'] = hit['_source']['subject']
            answers.append(answer_dict)

        end = time.time()
        print("Time cost:{0}".format(end - start))
        print(answers)
        return answers

    # 使用helpers查询
    def keywordSearch(self, keyword):
        # 根据keywords1来查找，倒排索引
        search = {
                "query": {
                    "match": {
                        "name": keyword
                    }
                },
                "sort": {
                    "_score": {"order":"desc"}
                }
            }

        start = time.time()

        es_result = helpers.scan(
            client=self.es,
            query=search,
            scroll='10m',
            index=self.index_name,
            timeout='10m'
        )
        es_result = [item for item in es_result]
        search_res = []
        for item in es_result:
            tmp = item['_source']
            search_res.append((tmp['name'], tmp['subject']))
        print("共查询到%d条数据" % len(es_result))

        end = time.time()
        print("Time cost:{0}".format(end - start))
        # print(search_res)
        return search_res

    def build_dict(self, keyword):
        res = self.keywordSearch(keyword)
        res_dict = {}
        for r in res:
            key = r[0]
            res_dict[key] = r[1]

        return res_dict

    def filter(self, keyword):
        res_dict = self.build_dict(keyword)
        kgroup = res_dict.keys()
        choice = []
        val = []

        for k in kgroup:
            if keyword == k:  # 目标词命中的情况----优先输出匹配词；根据匹配词的学科，继续推荐
                subj = res_dict[k]  # only
                val.append(subj)

                for k_, v_ in res_dict.items():
                    if v_ == val[0]:
                        choice.append(k_)

                for cho in choice:
                    if cho == keyword:
                        choice.remove(cho)
                        return choice
            else:  # 未命中的情况----随机抽取
                alternate = random.sample(list(set(kgroup)), min(len(kgroup), 10))
                return alternate

    def pick_or_drop(self, keyword):
        res_dict = self.build_dict(keyword)
        kgroup = res_dict.keys()

        choice = self.filter(keyword)
        if len(choice) > 10:
            choice = random.sample(list(set(choice)), 10)
            return choice

        else:  # 候选词个数过少
            add = random.sample(list(set(kgroup)), min(len(kgroup), 10))
            choice.extend(add)
            return choice

    def getZuhe(self, keyword):
        # 全切分 效果不好
        res1 = []
        length = len(keyword)
        for i in range(length):
            for j in range(i + 1, length + 1):
                res1.append(keyword[i:j])
        res1 = " ".join(res1)
        return res1

    def main(self):
        kws = '晶体'

        # 对关键词进行切分再搜索（查找相关词的位置）
        # kws1 = self.getZuhe(kws)
        # print(kws1)
        # self.commonSearch(kws1)
        recommend = self.filter(kws)
        if recommend is not None:
            return recommend
        else:
            recommend.append('后续会扩充词表')
            return recommend


if __name__ == "__main__":
    index = 'cnki_term_simple'
    ip = '127.0.0.1'
    retri = TermRecommendES(index,ip)
    retri.main()

