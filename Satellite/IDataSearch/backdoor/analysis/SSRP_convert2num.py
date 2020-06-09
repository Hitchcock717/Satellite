# -*- coding: utf-8 -*-
"""
将作者数据中的列表字符映射为数字
"""
import codecs
import ast


class SearchDictBuild(object):

    # 构建aus列表
    def aus_build(self, raw_list):
        str_list = []
        for tup in raw_list:
            for s in tup:
                str_list.append(s)
        return str_list

    # aus列表去重
    def de_duplication(self, raw_aus):
        aus_list = []
        for word in raw_aus:
            if not word in aus_list:
                aus_list.append(word)

        return aus_list

    # 构建ids列表
    def ids_build(self, clean_aus):
        ids_list = []
        for i in range(1, len(clean_aus)+1):
            ids_list.append(i)
        return ids_list

    # 构建{au：id}字典
    def dict_build(self, aus_li, ids_li):
        au_id_dict = dict(zip(aus_li, ids_li))

        return au_id_dict























