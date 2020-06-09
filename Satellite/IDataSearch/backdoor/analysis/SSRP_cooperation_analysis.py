# -*- coding: utf-8 -*-
'''
    SSRP分析平台之关系图分析 --- 作者两两合作
    tips: 数据过载问题
'''

import itertools
from .SSRP_convert2num import *


class CooperateAnalysis(object):

    def __init__(self):
        self.search = SearchDictBuild()

    def build_two_authors(self, two_aus):
        two_aus_data = []
        two_aus_list = [aus.split(' ') for aus in two_aus]
        for au in two_aus_list:
            aus_combi = list(itertools.combinations(au, 2))
            two_aus_data.extend(aus_combi)

        return two_aus_data

    def build_more_authors(self, more_aus):
        more_aus_data = []
        more_aus_list = [aus.split(' ') for aus in more_aus]
        for au in more_aus_list:
            aus_combi = list(itertools.combinations(au, 2))
            more_aus_data.extend(aus_combi)

        return more_aus_data

    def prepare_data(self, two_aus, more_aus):
        data = []
        two_aus = self.build_two_authors(two_aus)
        more_aus = self.build_more_authors(more_aus)
        data.extend(two_aus)
        data.extend(more_aus)

        # 清洗,删去无用关系
        for aus in data:
            aus_check = aus[1]
            if aus_check == '':
                data.remove(aus)

        # print(data)
        return data

    def build_au_id(self, two_aus, more_aus):
        data = self.prepare_data(two_aus, more_aus)
        s_li = self.search.aus_build(data)
        aus_li = self.search.de_duplication(s_li)
        ids_li = self.search.ids_build(aus_li)
        au_id_dict = self.search.dict_build(aus_li, ids_li)

        return au_id_dict

    def build_au_relation(self, two_aus, more_aus):
        relations = []
        for k in self.prepare_data(two_aus, more_aus):
            relation = {}
            p_au1, q_au2 = k[0], k[1]
            p = self.build_au_id(two_aus, more_aus).get(p_au1)
            q = self.build_au_id(two_aus, more_aus).get(q_au2)
            relation['from'] = str(p)
            relation['to'] = str(q)
            relations.append(relation)
        print(relations)

        ids = []
        for k,v in zip(list(self.build_au_id(two_aus, more_aus).keys()), list(self.build_au_id(two_aus, more_aus).values())):
            id = {}
            id['id'] = int(v)
            id['label'] = str(k)
            ids.append(id)
        print(ids)
        return ids, relations


if __name__ == '__main__':
    cooper = CooperateAnalysis()
    cooper.build_au_relation(two_aus, more_aus)
