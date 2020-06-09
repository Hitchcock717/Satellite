#!/usr/bin/env python
# -*-coding:utf-8-*-
'''
    目的：ES文档检索----简单检索（单个或多个搜索词）
                  ----高级检索（与或非组合表达式）
    BUG: es.search() 报错TypeError: multiple values for argument 'body'
'''

import json
import re
# from ES_ct import *
from elasticsearch import Elasticsearch
from elasticsearch import helpers


class DocRetireveES(object):

    def __init__(self, index_name, ip):
        # self.conn = Connect2ES(index_name, ip)
        self.index_name = index_name
        # 无用户名密码状态
        self.es = Elasticsearch([ip])

    # **********************************start basic query******************************** #

    # 单字段搜索
    def single_query(self, search_field, kws, match_method='match'):
        query = ''
        if type(search_field) == str:
            query = '{"query":' \
                       '{"%s":{"%s":"%s"}' \
                       '}' \
                       '}' % (match_method, search_field, kws)

        body = json.loads(query)
        # print(body)
        return body

    # 多字段搜索
    def multi_query(self, search_field, kws):

        # Note: multi_match eg.json
        # {
        #  "query": {
        #  "multi_match" : {
        #       "query":    "this is a test",
        #       "fields": [ "subject", "message" ]
        #       }
        #   }
        # }

        if type(search_field) == list:
            field_li = []  # 字段列表, 相当于mysql中的column
            for single_field in search_field:
                single_field = '"' + single_field + '"'
                field_li.append(single_field)

            field = ','.join(field_li)
            field1 = '[' + field + ']'
            query = '{"query":' \
                               '{"multi_match":' \
                               '{"query": "%s",' \
                               '"fields":%s}' \
                               '}' \
                               '}' % (kws, field1)

            body = json.loads(query)
            # print(body)
            return body

    # 搜索结果高亮显示
    def highlight(self, res, search_field):
        """
        :param res: result after query
        :param search_field:
        :return:
        """
        parse_body = [item for item in res]
        # print(parse_body)
        count = len(parse_body)
        result = []

        for hit in parse_body:
            key = hit['_source']

            if type(search_field) == str:  # single query
                key['highlight'] = key[search_field]

            elif type(search_field) == list:  # multi query
                highlight = []
                for field in search_field:
                    highlight.append(key[field])
                key['highlight'] = highlight
            result.append(key)

        return count, result

    # 搜索结果--单字段
    def single_result(self, search_field, kws):
        if type(search_field) == str:
            body = self.single_query(search_field, kws)
            # res = self.es.search(self.index_name, body=body)
            res = helpers.scan(client=self.es,
                               query=body,
                               index=self.index_name)
            count, result = self.highlight(res, search_field)

            if count == 0:  # 若搜索结果为空，则改用短语前缀搜索
                body = self.single_query(search_field, kws, match_method='match_phrase_prefix')
                # res = self.es.search(self.index_name, body=body)
                res = helpers.scan(client=self.es,
                                   query=body,
                                   index=self.index_name)
                count, result = self.highlight(res, search_field)

            return body, count, result

    # 简单搜索（同时包含单字段和多字段）
    def basic_search(self, search_field, kws):

        if type(search_field) == list:
            body = self.multi_query(search_field, kws)
            # res = self.es.search(self.index_name, body=body)
            res = helpers.scan(client=self.es,
                               query=body,
                               index=self.index_name)
            counts, results = self.highlight(res, search_field)
            # print(counts, results)

            if counts == 0:  # 若搜索结果为空，则改用短语前缀搜索[区别：对每个字段分别搜索，而不是整体]
                for field in search_field:
                    body = self.single_query(field, kws, match_method='match_phrase_prefix')
                    # res = self.es.search(self.index_name, body=body)
                    res = helpers.scan(client=self.es,
                                       query=body,
                                       index=self.index_name)
                    count, result = self.highlight(res, search_field)
                    counts += count
                    results += result

                # 根据字段id去重
                tmp = []
                result_ids = set()
                for res in results:
                    result_ids.add(res['id'])  # 构造id集合

                for id in result_ids:
                    for res in results:
                        if res['id'] == id:
                            tmp.append(res)  # 若单个搜索结果的字段id出现在集合中，即跳出内循环，保证不重复性
                            break

                results = tmp
                counts = len(results)

            # print(counts, results)
            # print(counts)
            return body, counts, results

        elif type(search_field) == str:
            results = self.single_result(search_field, kws)
            body = results[0]
            counts = results[1]
            doc = results[2]

            # print(counts, results)
            # print(counts)
            return body, counts, doc

    # **********************************end basic query******************************** #

    # ES 高级查询
    # 使用Query DSL：bool 查询 & range 查询 [ 同时使用：filter 关键词 ]
    # bool 查询：
    #  - - - - - - - - - - -
    # | must ---- 与操作    |
    # | should ---- 或操作  |
    # | must_not ---- 非操作|
    #  - - - - - - - - - - -

    # range 查询：
    #  - - - - - - - -
    # | lte ---- < =  |
    # | lt ---- <     |
    # | gte ---- > =  |
    # | gt ---- >     |
    #  - - - - - - - -

    # **********************************start advance query******************************** #

    # 高级检索体
    def advance_query(self, in_fields, in_kws, ex_fields, ex_kws, date_field, start, end, in_method):

        # *************预期构造格式************* #
        # {"query": {
        #    "bool": {
        #       "must": [
        #            {"prefix": {"title": "test"}},
        #            {"prefix": {"content": "test"}}
        #        ],
        #        "must_not": [
        #            {"prefix": {"content": "0"}}
        #        ],
        #        "filter": [
        #            {"range":
        #                 {"createdate":
        #                      {"gte": "1900-01-01",
        #                       "lte": "2020-01-01"
        #                       }
        #                  }
        #             }
        #        ]
        #    }
        # }
        # }

        # *************构造检索规则************* #

        query = '{"query":{' \
                   '"bool":{'

        if in_method == '1':  # in_method 区分 "与"|"或"
            in_clause = '"must":[ %s ]'
        else:
            in_clause = '"should":[ %s ]'

        ex_clause = '"must_not":[ %s ]'

        match_clause = '{ "prefix": { "%s":"%s" } }'  # 此处可切换wildcard，regexp两种低级别的词条检索方式. 如使用正则，需注意修改分词条件为
                                                      # analyzer: not analyzed, 否则自带ik_max_word #

        range_clause = '"filter":[ { "range": { "%s" :{ "gte":"%s","lte":"%s" } } } ]'  # range查询用于日期过滤

        # *************根据构造规则获取局部匹配格式************* #

        in_kws_li = []  # 包含搜索词列表
        ex_kws_li = []  # 不包含搜索词列表

        # 预处理搜索词列表
        if in_kws != '':
            in_kws_li = in_kws.split(',')
        if ex_kws != '':
            ex_kws_li = ex_kws.split(',')

        in_match = ''  # 全部包含搜索词匹配格式
        ex_match = ''  # 全部不包含搜索词匹配格式

        if len(in_fields) > 0:  # must/should
            for in_field in in_fields:
                for in_kw in in_kws_li:
                    if in_match != '':  # 存在匹配格式
                        in_match += ','  # 逗号分隔
                    tmp_match_clause = match_clause % (in_field, in_kw)  # 前缀匹配
                    in_match += tmp_match_clause

        if len(ex_fields) > 0:  # must_not 同理
            for ex_field in ex_fields:
                for ex_kw in ex_kws_li:
                    if ex_match != '':
                        ex_match += ','
                    tmp_match_clause = match_clause % (ex_field, ex_kw)
                    ex_match += tmp_match_clause

        range_clause_body = range_clause % (date_field, start, end)  # 过滤规则:日期

        # *************根据局部匹配格式构造完整检索体************* #

        in_clause_body = ""  # 与、或检索体
        ex_clause_body = ""  # 非检索体

        if in_match != "":
            in_clause_body = in_clause % in_match
            # print(in_clause_body)
        if ex_match != "":
            ex_clause_body = ex_clause % ex_match
        if ex_clause_body != "":
            query = query + in_clause_body + "," + ex_clause_body + "}}}"
            # print(query)
        else:
            query = query + in_clause_body + "," + range_clause_body + "}}}"
            # print(query)

        body = json.loads(query)
        return body

    # ES查询
    def advance_search(self, in_fields, in_kws, ex_fields, ex_kws, date_field, start, end, in_method):
        query = self.advance_query(in_fields, in_kws, ex_fields, ex_kws, date_field, start, end, in_method)
        # print(type(query))
        # res = self.es.search(self.index_name, body=query)
        res = helpers.scan(client=self.es,
                           query=query,
                           index=self.index_name)
        counts, results = self.highlight(res, in_fields)
        # print(counts)
        return query, counts, results

    # **********************************end advance query******************************** #

    # **********************************start regexp query******************************** #

    # 高级检索体
    def advance_query_with_regexp(self, in_fields, in_reg, ex_fields, ex_reg, date_field, start, end, in_method):

        # *************预期构造格式************* #
        # {"query": {
        #    "bool": {
        #       "must": [
        #            {"regexp": {"title": "t.*t"}},
        #            {"regexp": {"content": "te?"}}
        #        ],
        #        "must_not": [
        #            {"regexp": {"content": "0"}}
        #        ],
        #        "filter": [
        #            {"range":
        #                 {"createdate":
        #                      {"gte": "1900-01-01",
        #                       "lte": "2020-01-01"
        #                       }
        #                  }
        #             }
        #        ]
        #    }
        # }
        # }

        # *************构造检索规则************* #

        query = '{"query":{' \
                '"bool":{'

        if in_method == '1':  # in_method 区分 "与"|"或"
            in_clause = '"must":[ %s ]'
        else:
            in_clause = '"should":[ %s ]'

        ex_clause = '"must_not":[ %s ]'

        match_clause = '{ "regexp": { "%s":"%s" } }'

        range_clause = '"filter":[ { "range": { "%s" :{ "gte":"%s","lte":"%s" } } } ]'  # range查询用于日期过滤

        # *************根据构造规则获取局部匹配格式************* #

        in_reg_li = []  # 包含搜索词列表
        ex_reg_li = []  # 不包含搜索词列表

        # 预处理搜索词列表
        if in_reg != '':
            in_reg_li = in_reg.split(',')
        if ex_reg != '':
            ex_reg_li = ex_reg.split(',')

        in_match = ''  # 全部包含搜索词匹配格式
        ex_match = ''  # 全部不包含搜索词匹配格式

        if len(in_fields) > 0:  # must/should
            for in_field in in_fields:
                for inreg in in_reg_li:
                    if in_match != '':  # 存在匹配格式
                        in_match += ','  # 逗号分隔
                    tmp_match_clause = match_clause % (in_field, inreg)  # 前缀匹配
                    in_match += tmp_match_clause

        if len(ex_fields) > 0:  # must_not 同理
            for ex_field in ex_fields:
                for exreg in ex_reg_li:
                    if ex_match != '':
                        ex_match += ','
                    tmp_match_clause = match_clause % (ex_field, exreg)
                    ex_match += tmp_match_clause

        range_clause_body = range_clause % (date_field, start, end)  # 过滤规则:日期

        # *************根据局部匹配格式构造完整检索体************* #

        in_clause_body = ''  # 与、或检索体
        ex_clause_body = ''  # 非检索体

        if in_match != '':
            in_clause_body = in_clause % in_match
        if ex_match != '':
            ex_clause_body = ex_clause % ex_match

        if ex_clause_body != '':
            query = query + in_clause_body + ',' + ex_clause_body + '}}}'
        else:
            query = query + in_clause_body + ',' + range_clause_body + '}}}'

        body = json.loads(query)
        return body

    # ES查询
    def advance_search_with_regexp(self, in_fields, in_reg, ex_fields, ex_reg, date_field, start, end, in_method):
        query = self.advance_query_with_regexp(in_fields, in_reg, ex_fields, ex_reg, date_field, start, end, in_method)
        # res = self.es.search(self.index_name, body=query)
        res = helpers.scan(client=self.es,
                           query=query,
                           index=self.index_name)
        counts, results = self.highlight(res, in_fields)
        # print(counts)
        return query, counts, results

    # **********************************end regexp query******************************** #

    # **********************************start nested advance query******************************** #

    # 内部嵌套高级检索体
    def nested_advance_query(self, in_fields, in_kws, ex_fields, ex_kws, in_method):
        # *************预期构造格式************* #
        # {
        #    "query": {
        #        "bool": {
        #            "should": [
        #                {"prefix": {"age": 40}},
        #                {"bool": {"must": [
        #                    {"prefix": {"address": "mill"}},
        #                    {"prefix": {"address": "lane"}}
        #                   ]
        #                 }}
        #                ],
        #                "filter": [
        #                   {"range":
        #                       {"createdate":
        #                           {"gte": "1900-01-01",
        #                            "lte": "2020-01-01"
        #                           }
        #                       }
        #                   }
        #               ]
        #        }
        #    }
        # }

        # *************构造内部检索规则************* #
        if in_method == '1':  # inside_method 区分 "与"|"或"
            in_clause = '{"bool":{"must":[ %s ]'
        else:
            in_clause = '{"bool":{"should":[ %s ]'

        ex_clause = '"must_not":[ %s ]'

        match_clause = '{ "prefix": { "%s":"%s" } }'

        # *************根据构造规则获取局部匹配格式************* #

        in_kws_li = []  # 包含搜索词列表
        ex_kws_li = []  # 不包含搜索词列表


        # 预处理搜索词列表
        if in_kws != '':
            in_kws_li = in_kws.split(',')
        if ex_kws != '':
            ex_kws_li =  ex_kws.split(',')

        in_match = ''  # 全部包含搜索词匹配格式
        ex_match = ''  # 全部不包含搜索词匹配格式

        if len(in_fields) > 0:  # must/should
            for in_field in in_fields:
                for in_kw in in_kws_li:
                    if in_match != '':  # 存在匹配格式
                        in_match += ','  # 逗号分隔
                    tmp_match_clause = match_clause % (in_field, in_kw)  # 前缀匹配
                    in_match += tmp_match_clause

        if len(ex_fields) > 0:  # must_not 同理
            for ex_field in ex_fields:
                for ex_kw in ex_kws_li:
                    if ex_match != '':
                        ex_match += ','
                    tmp_match_clause = match_clause % (ex_field, ex_kw)
                    ex_match += tmp_match_clause

        # *************内部嵌套检索体结构************* #

        in_clause_body = ""  # 与、或检索体
        ex_clause_body = ""  # 非检索体

        if in_match != "":
            in_clause_body = in_clause % in_match
        if ex_match != "":
            ex_clause_body = ex_clause % ex_match
        if ex_clause_body != "":
            query = in_clause_body + "," + ex_clause_body + "}}"
        else:
            query = in_clause_body + "}}"

        body = json.loads(query)
        return body

    # 内部嵌套高级检索体
    def nested_advance_query_with_regexp(self, in_fields, in_kws, ex_fields, ex_kws, in_method):
        # *************预期构造格式************* #
        # {
        #    "query": {
        #        "bool": {
        #            "should": [
        #                {"regexp": {"age": 40}},
        #                {"bool": {"must": [
        #                    {"regexp": {"address": "mill"}},
        #                    {"regexp": {"address": "lane"}}
        #                   ]
        #                 }}
        #                ],
        #                "filter": [
        #                   {"range":
        #                       {"createdate":
        #                           {"gte": "1900-01-01",
        #                            "lte": "2020-01-01"
        #                           }
        #                       }
        #                   }
        #               ]
        #        }
        #    }
        # }

        # *************构造内部检索规则************* #
        if in_method == '1':  # inside_method 区分 "与"|"或"
            in_clause = '{"bool":{"must":[ %s ]'
        else:
            in_clause = '{"bool":{"should":[ %s ]'

        ex_clause = '"must_not":[ %s ]'

        match_clause = '{ "regexp": { "%s":"%s" } }'

        # *************根据构造规则获取局部匹配格式************* #

        in_kws_li = []  # 包含搜索词列表
        ex_kws_li = []  # 不包含搜索词列表

        # 预处理搜索词列表
        if in_kws != '':
            in_kws_li = in_kws.split(',')
        if ex_kws != '':
            ex_kws_li = ex_kws.split(',')

        in_match = ''  # 全部包含搜索词匹配格式
        ex_match = ''  # 全部不包含搜索词匹配格式

        if len(in_fields) > 0:  # must/should
            for in_field in in_fields:
                for in_kw in in_kws_li:
                    if in_match != '':  # 存在匹配格式
                        in_match += ','  # 逗号分隔
                    tmp_match_clause = match_clause % (in_field, in_kw)  # 前缀匹配
                    in_match += tmp_match_clause

        if len(ex_fields) > 0:  # must_not 同理
            for ex_field in ex_fields:
                for ex_kw in ex_kws_li:
                    if ex_match != '':
                        ex_match += ','
                    tmp_match_clause = match_clause % (ex_field, ex_kw)
                    ex_match += tmp_match_clause

        # *************内部嵌套检索体结构************* #

        in_clause_body = ""  # 与、或检索体
        ex_clause_body = ""  # 非检索体

        if in_match != "":
            in_clause_body = in_clause % in_match
            # print(in_clause_body)
        if ex_match != "":
            ex_clause_body = ex_clause % ex_match
        if ex_clause_body != "":
            query = in_clause_body + "," + ex_clause_body + "}}"
            # print(query)
        else:
            query = in_clause_body + "}}"
            # print(query)

        body = json.loads(query)
        return body

    # **********************************start wrapped advance query******************************** #
    # 构建内部嵌套高级检索体
    def build_nested_advance_query(self, raw_expression_group):
        query_collection = []
        query_content = []
        for raw_expression_dict in raw_expression_group:

            each_nested_query_with_relation = []  # 注意该列表应处于循环内
            # print(raw_expression_dict)
            in_field = raw_expression_dict['type'].split()
            query_content.append(in_field)
            in_kws = raw_expression_dict['info']
            regex_flag = raw_expression_dict['regex']
            next_relation = raw_expression_dict['nextrelation']

            # 相邻关系 --- 4种
            global x
            if next_relation == '并且':
                x = '1'
            elif next_relation == '或者':
                x = '2'
            elif next_relation == '不含':
                x = '0'
            else:
                x = ''

            # 无正则 --- 4种
            if regex_flag == '否':
                # 不止必填项
                if raw_expression_dict.get('relation') and raw_expression_dict.get('otherinfo'):
                    in_relation = raw_expression_dict['relation']
                    other_in_kws = raw_expression_dict['otherinfo']
                    if in_relation == '并含':
                        in_method = '1'
                        in_kws = in_kws + ',' + other_in_kws
                        ex_field = []
                        ex_kws = ''
                        query_content.append(in_kws)
                        query_content.append(ex_field)
                        query_content.append(ex_kws)
                        query_content.append(in_method)
                        each_nested_query = self.nested_advance_query(query_content[0], query_content[1], query_content[2],
                                                                      query_content[3], query_content[4])
                        each_nested_query_with_relation.append(each_nested_query)
                        each_nested_query_with_relation.append(x)
                        query_collection.append(each_nested_query_with_relation)
                        query_content.clear()

                    elif in_relation == '或含':
                        in_method = '2'
                        in_kws = in_kws + ',' + other_in_kws
                        ex_field = []
                        ex_kws = ''
                        query_content.append(in_kws)
                        query_content.append(ex_field)
                        query_content.append(ex_kws)
                        query_content.append(in_method)
                        each_nested_query = self.nested_advance_query(query_content[0], query_content[1], query_content[2],
                                                                  query_content[3], query_content[4])
                        each_nested_query_with_relation.append(each_nested_query)
                        each_nested_query_with_relation.append(x)
                        query_collection.append(each_nested_query_with_relation)
                        query_content.clear()

                    else:
                        in_method = '2'  # default
                        ex_field = in_field
                        ex_kws = other_in_kws
                        in_kws = in_kws
                        query_content.append(in_kws)
                        query_content.append(ex_field)
                        query_content.append(ex_kws)
                        query_content.append(in_method)
                        each_nested_query = self.nested_advance_query(query_content[0], query_content[1], query_content[2],
                                                                      query_content[3], query_content[4])
                        each_nested_query_with_relation.append(each_nested_query)
                        each_nested_query_with_relation.append(x)
                        query_collection.append(each_nested_query_with_relation)
                        query_content.clear()

                # 有且仅有必填项
                else:
                    in_method = '2'  # default
                    ex_field = []
                    ex_kws = ''
                    in_kws = in_kws
                    query_content.append(in_kws)
                    query_content.append(ex_field)
                    query_content.append(ex_kws)
                    query_content.append(in_method)
                    each_nested_query = self.nested_advance_query(query_content[0], query_content[1], query_content[2], query_content[3], query_content[4])
                    each_nested_query_with_relation.append(each_nested_query)
                    each_nested_query_with_relation.append(x)
                    query_collection.append(each_nested_query_with_relation)
                    query_content.clear()

            # 有正则 --- 4种
            else:
                # 不止必填项
                if raw_expression_dict.get('relation') and raw_expression_dict.get('otherinfo'):
                    in_relation = raw_expression_dict['relation']
                    other_in_kws = raw_expression_dict['otherinfo']
                    if in_relation == '并含':
                        in_method = '1'
                        in_kws = in_kws + ',' + other_in_kws
                        ex_field = []
                        ex_kws = ''
                        query_content.append(in_kws)
                        query_content.append(ex_field)
                        query_content.append(ex_kws)
                        query_content.append(in_method)
                        each_nested_query = self.nested_advance_query_with_regexp(query_content[0], query_content[1],
                                                                      query_content[2], query_content[3], query_content[4])
                        each_nested_query_with_relation.append(each_nested_query)
                        each_nested_query_with_relation.append(x)
                        query_collection.append(each_nested_query_with_relation)
                        query_content.clear()

                    elif in_relation == '或含':
                        in_method = '2'
                        in_kws = in_kws + ',' + other_in_kws
                        ex_field = []
                        ex_kws = ''
                        query_content.append(in_kws)
                        query_content.append(ex_field)
                        query_content.append(ex_kws)
                        query_content.append(in_method)
                        each_nested_query = self.nested_advance_query_with_regexp(query_content[0], query_content[1],
                                                                      query_content[2], query_content[3], query_content[4])
                        each_nested_query_with_relation.append(each_nested_query)
                        each_nested_query_with_relation.append(x)
                        query_collection.append(each_nested_query_with_relation)
                        query_content.clear()

                    else:
                        in_method = '2'  # default
                        ex_field = in_field
                        ex_kws = other_in_kws
                        in_kws = in_kws
                        query_content.append(in_kws)
                        query_content.append(ex_field)
                        query_content.append(ex_kws)
                        query_content.append(in_method)
                        each_nested_query = self.nested_advance_query_with_regexp(query_content[0], query_content[1],
                                                                      query_content[2], query_content[3], query_content[4])
                        each_nested_query_with_relation.append(each_nested_query)
                        each_nested_query_with_relation.append(x)
                        query_collection.append(each_nested_query_with_relation)
                        query_content.clear()

                # 有且仅有必填项
                else:
                    in_method = '2'  # default
                    ex_field = []
                    ex_kws = ''
                    in_kws = in_kws
                    query_content.append(in_kws)
                    query_content.append(ex_field)
                    query_content.append(ex_kws)
                    query_content.append(in_method)
                    each_nested_query = self.nested_advance_query_with_regexp(query_content[0], query_content[1], query_content[2],
                                                                  query_content[3], query_content[4])
                    each_nested_query_with_relation.append(each_nested_query)
                    each_nested_query_with_relation.append(x)
                    query_collection.append(each_nested_query_with_relation)
                    query_content.clear()

        return query_collection

    # 构建外部嵌套高级检索体
    def wrapped_advance_query(self, raw_expression_group, date_field, start, end):
        query_groups = self.build_nested_advance_query(raw_expression_group)  # [[''],['']]
        # print(query_groups)

        range_clause = '"filter":[ { "range": { "%s" :{ "gte":"%s","lte":"%s" } } } ]'  # range查询用于日期过滤

        # 有且仅有两个检索体
        if len(query_groups) == 2:
            in_method = query_groups[0][1]
            # print(in_method)
            front_query = query_groups[0][0]
            # print(front_query)
            back_query = query_groups[1][0]
            # print(back_query)
            in_match = str(front_query) + ',' + str(back_query)

            # *************构造检索规则************* #

            query = '{"query":{' \
                    '"bool":{'
            range_clause_body = range_clause % (date_field, start, end)  # 过滤规则:日期

            if in_method == '1':  # in_method 区分 "与"|"或"
                in_clause = '"must":[ %s ]'
                in_clause_body = in_clause % in_match
                query_body = query + in_clause_body + ',' + range_clause_body + '}}}'

                query_body = query_body.replace('\'', '\"')
                # print(query_body)

                body = json.loads(query_body)
                return body

            if in_method == '2':
                in_clause = '"should":[ %s ]'
                in_clause_body = in_clause % in_match
                query_body = query + in_clause_body + ',' + range_clause_body + '}}}'

                query_body = query_body.replace('\'', '\"')
                # print(query_body)

                body = json.loads(query_body)
                return body

            if in_method == '0':
                in_clause = '"should":[ %s ]'
                ex_clause = '"must_not":[ %s ]'
                in_match = front_query
                in_clause_body = in_clause % in_match
                ex_match = back_query
                ex_clause_body = ex_clause % ex_match
                query_body = query + in_clause_body + ',' + ex_clause_body + ',' + range_clause_body + '}}}'

                query_body = query_body.replace('\'', '\"')
                # print(query_body)

                body = json.loads(query_body)
                return body

        else:  # 大于两个检索体
            top_two_query = query_groups[:2]
            # print(top_two_query)
            in_method = top_two_query[0][1]
            front_query = top_two_query[0][0]
            # print(front_query)
            back_query = top_two_query[1][0]
            # print(back_query)
            in_match = str(front_query) + ',' + str(back_query)

            # *************构造前两个检索规则************* #

            top_two_query_body = []
            query = '"bool":{'

            if in_method == '1':  # in_method 区分 "与"|"或"
                in_clause = '"must":[ %s ]'
                in_clause_body = in_clause % in_match
                query_body = query + in_clause_body + '}'
                top_two_query_body.append(query_body)

            if in_method == '2':
                in_clause = '"should":[ %s ]'
                in_clause_body = in_clause % in_match
                query_body = query + in_clause_body + '}'
                top_two_query_body.append(query_body)

            if in_method == '0':
                in_clause = '"should":[ %s ]'
                ex_clause = '"must_not":[ %s ]'
                in_match = front_query
                in_clause_body = in_clause % in_match
                ex_match = back_query
                ex_clause_body = ex_clause % ex_match
                query_body = query + in_clause_body + ',' + ex_clause_body + '}'
                top_two_query_body.append(query_body)

            # print(top_two_query_body)
            base_query_body = top_two_query_body[0]

            # 有且仅有三个检索体
            if len(query_groups) == 3:
                in_method = query_groups[1][1]
                front_query = query_groups[2][0]
                back_query = base_query_body

                # *************构造检索规则************* #
                query = '{"query":{' \
                        '"bool":{'

                range_clause_body = range_clause % (date_field, start, end)  # 过滤规则:日期

                if in_method == '1':  # in_method 区分 "与"|"或"
                    in_clause = '"must":[ %s ]'
                    in_clause_body = in_clause % in_match
                    query_body = query + in_clause_body + ',' + range_clause_body + '}}}'

                    query_body = query_body.replace('\'', '\"')
                    # print(query_body)

                    body = json.loads(query_body)
                    return body

                if in_method == '2':
                    in_clause = '"should":[ %s ]'
                    in_clause_body = in_clause % in_match
                    query_body = query + in_clause_body + ',' + range_clause_body + '}}}'

                    query_body = query_body.replace('\'', '\"')
                    # print(query_body)

                    body = json.loads(query_body)
                    return body

                if in_method == '0':
                    in_clause = '"should":[ %s ]'
                    ex_clause = '"must_not":[ %s ]'
                    in_match = front_query
                    in_clause_body = in_clause % in_match
                    ex_match = back_query
                    ex_clause_body = ex_clause % ex_match
                    query_body = query + in_clause_body + ',' + ex_clause_body + ',' + range_clause_body + '}}}'

                    query_body = query_body.replace('\'', '\"')
                    # print(query_body)

                    body = json.loads(query_body)
                    return body

            else:
                # 从第三个列表开始, 继续嵌套, 此时列表>=4
                other_query = []

                for i in range(2, len(query_groups)-1):
                    if query_groups[i][1] != '':

                        in_method = query_groups[i-1][1]
                        add_query = query_groups[i][0]

                        if i == 2:
                            in_match = add_query + ',' + base_query_body  # 仅适用于第三个列表
                        else:
                            in_match = add_query + ',' + other_query[0]
                            other_query.clear()

                        # *************构造检索规则************* #

                        query = '"bool":{'

                        if in_method == '1':  # in_method 区分 "与"|"或"
                            in_clause = '"must":[ %s ]'
                            in_clause_body = in_clause % in_match
                            other_query_body = query + in_clause_body + '}'
                            # print(other_query_body)
                            other_query.append(other_query_body)

                        if in_method == '2':
                            in_clause = '"should":[ %s ]'
                            in_clause_body = in_clause % in_match
                            other_query_body = query + in_clause_body + '}'
                            # print(other_query_body)
                            other_query.append(other_query_body)

                        if in_method == '0':
                            in_clause = '"should":[ %s ]'
                            ex_clause = '"must_not":[ %s ]'
                            in_match = add_query
                            in_clause_body = in_clause % in_match
                            ex_match = base_query_body
                            ex_clause_body = ex_clause % ex_match
                            other_query_body = query + in_clause_body + ',' + ex_clause_body + '}'
                            # print(other_query_body)
                            other_query.append(other_query_body)

                    else:  # 最后一个检索体: 需要修改检索头部 + 添加日期范围

                        in_method = query_groups[i-1][1]
                        add_query = query_groups[i][0]

                        in_match = add_query + ',' + other_query[0]  # 预想other_query最后剩下除末尾元素以外的检索体
                        # *************构造检索规则************* #

                        query = '{"query":{' \
                                '"bool":{'
                        range_clause_body = range_clause % (date_field, start, end)  # 过滤规则:日期

                        if in_method == '1':  # in_method 区分 "与"|"或"
                            in_clause = '"must":[ %s ]'
                            in_clause_body = in_clause % in_match
                            query_body = query + in_clause_body + ',' + range_clause_body + '}}}'

                            query_body = query_body.replace('\'', '\"')
                            # print(query_body)

                            body = json.loads(query_body)
                            return body

                        if in_method == '2':
                            in_clause = '"should":[ %s ]'
                            in_clause_body = in_clause % in_match
                            query_body = query + in_clause_body + ',' + range_clause_body + '}}}'

                            query_body = query_body.replace('\'', '\"')
                            # print(query_body)

                            body = json.loads(query_body)
                            return body

                        if in_method == '0':
                            in_clause = '"should":[ %s ]'
                            ex_clause = '"must_not":[ %s ]'
                            in_match = front_query
                            in_clause_body = in_clause % in_match
                            ex_match = back_query
                            ex_clause_body = ex_clause % ex_match
                            query_body = query + in_clause_body + ',' + ex_clause_body + ',' + range_clause_body + '}}}'

                            query_body = query_body.replace('\'', '\"')
                            # print(query_body)

                            body = json.loads(query_body)
                            return body

    # ES查询
    def wrapped_advance_search(self, raw_expression_group, date_field, start, end):
        query = self.wrapped_advance_query(raw_expression_group, date_field, start, end)
        # res = self.es.search(self.index_name, body=query)

        # print(type(query))
        in_fields = []
        for raw_expression_dict in raw_expression_group:
            in_field = raw_expression_dict['type']
            in_fields.append(in_field)

        res = helpers.scan(client=self.es,
                           query=query,
                           index=self.index_name)
        counts, results = self.highlight(res, in_fields)
        # print(counts)
        return query, counts, results


if __name__ == "__main__":
    index = 'cnki_doc'
    localhost = '127.0.0.1'
    doc = DocRetireveES(index, localhost)

    # ***************** 测试简单搜索[单字段] ***************** #
    basic_field = 'kws'
    basic_kws = '电镜'
    # doc.basic_search(basic_field, basic_kws)

    # ***************** 测试简单搜索[多字段] ***************** #
    multi_fields = ['abstract', 'kws', 'title', 'info', 'fund', 'source']
    multi_kws = '氨基酸'
    # doc.basic_search(multi_fields, multi_kws)

    # ***************** 测试高级搜索[与或非] ***************** #
    #  -------------------------------------------------
    # | fields: list                                    |
    # | kws: str                                        |
    # | date: str                                       |
    # | start, end: YYYY-MM-DD                          |
    # | in_method: "1"->must; other(default 2)->should  |
    #  -------------------------------------------------

    include_fields = ["kws"]
    include_kws = "氨基酸, 电镜"
    exclude_fields = ['kws']
    exclude_kws = "大鼠"
    date = "date"
    start = "1900-01-01"
    end = "2020-01-01"
    in_method = "2"
    doc.advance_search(include_fields, include_kws, exclude_fields, exclude_kws, date, start, end, in_method)

    # ***************** 测试高级搜索[正则] ***************** #
    #  -------------------------------------------------
    # | fields: list                                    |
    # | reg: regexp                                        |
    # | date: str                                       |
    # | start, end: YYYY-MM-DD                          |
    # | in_method: "1"->must; other(default 2)->should  |
    #  -------------------------------------------------

    inreg_fields = ["kws"]
    in_reg = ".*酸"
    exreg_fields = [""]
    ex_reg = ""
    date_reg = "date"
    start_reg = "1900-01-01"
    end_reg = "2020-01-01"
    in_method_reg = "2"
    # doc.advance_search_with_regexp(inreg_fields, in_reg, exreg_fields, ex_reg, date_reg, start_reg, end_reg, in_method_reg)

    # ***************** 测试内部嵌套高级搜索 ***************** #

    nested_in_fields = ["kws"]
    nested_in_kws = "氨基酸"
    nested_exclude_fields = []
    nested_exclude_kws = ""
    nested_in_method = "2"
    # doc.nested_advance_query(nested_include_fields, nested_include_kws, nested_exclude_fields, nested_exclude_kws, nested_in_method)

    # ***************** 测试内部嵌套高级搜索[正则] ***************** #

    nested_inreg_fields = ["kws"]
    nested_inreg_kws = "氨基酸"
    nested_exreg_fields = []
    nested_exreg_kws = ""
    nested_inreg_method = "2"
    # doc.nested_advance_query(nested_inreg_fields, nested_inreg_kws, nested_exreg_fields, nested_exreg_kws, nested_inreg_method)

    # ***************** 测试构建内部嵌套高级搜索 ***************** #
    raw_expression_group = [{"type":"来源","info":"驱蚊器·","regex":"是","nextrelation":"或者"},{"type":"来源","info":"确认","regex":"是","nextrelation":"不含"},{"type":"关键词","info":"人情味·","relation":"或含","regex":"否","nextrelation":"无"}]
    # doc.build_nested_advance_query(raw_expression_group)

    # ***************** 测试外部嵌套高级搜索 ***************** #
    raw_expression_group1 = [{"type": "来源", "info": "驱蚊器·", "regex": "是", "nextrelation": "或者"},
                             {"type": "来源", "info": "确认", "regex": "是", "nextrelation": "不含"},
                             {"type": "关键词", "info": "人情味·", "relation": "或含", "regex": "否", "nextrelation": "无"}]
    wrapped_date = "date"
    wrapped_start = "1900-01-01"
    wrapped_end = "2020-01-01"

    # doc.wrapped_advance_query(raw_expression_group1, wrapped_date, wrapped_start, wrapped_end)

    # ***************** 测试嵌套高级搜索 ***************** #
    #  -------------------------------------------------
    # | fields: list                                    |
    # | kws: str                                        |
    # | date: str                                       |
    # | start, end: YYYY-MM-DD                          |
    # | in_method: "1"->must; other(default 2)->should  |
    #  -------------------------------------------------
    raw_expression_group2 = [{"type":"来源","info":"驱蚊器·","regex":"是","nextrelation":"或者"},{"type":"来源","info":"确认","regex":"是","nextrelation":"不含"},{"type":"关键词","info":"人情味·","relation":"或含","regex":"否","nextrelation":"无"}]
    wrapped_date2 = "date"
    wrapped_start2 = "1900-01-01"
    wrapped_end2 = "2020-01-01"
    # doc.wrapped_advance_search(raw_expression_group2, wrapped_date2, wrapped_start2, wrapped_end2)

