import os
import time
from .es.ES_kws_retrieve import KeywordRetrieveES
from .es.ES_term_recommend import TermRecommendES
from .es.ES_doc_retrieve import DocRetireveES


# ******************* 处理命令行 ***************** #


class NohupProcess(object):

    def execCmd(self, cmd):
        r = os.popen(cmd)
        text = r.read()
        r.close()
        return text

# ******************* 处理关键词 ***************** #


class ExtractAndRecommend(object):

    def __init__(self):
        # ES术语索引地址
        self.index = 'cnki_term_simple'
        self.ip = '127.0.0.1'

        # 词表地址
        os.chdir('./backdoor/corpus')
        self.stop = 'stopwords.txt'
        self.range = 'range_words.txt'

        self.extr_kws = []
        self.recom_kws = []

    def extract_kws(self, raw_dict):

        # extract keywords
        if raw_dict['subject'] == '关键词':
            kwss = raw_dict['body']
            kws_li = kwss.split('，')
            try:
                if kws_li is not None:
                    for kws in kws_li:
                        self.extr_kws.append(kws)
                    return self.extr_kws
            except Exception as e:
                print(e)

        elif raw_dict['subject'] == '标题':
            await_title = raw_dict['body']

            sp = KeywordRetrieveES(self.index, self.ip)
            parsed_sent = sp.parse(await_title)
            parsed_sent1 = [await_title, parsed_sent]
            kws_li = sp.get_all_property(parsed_sent1, self.stop, self.range)
            try:
                if kws_li is not None:
                    for kws in kws_li:
                        self.extr_kws.append(kws)
                    return self.extr_kws
            except Exception as e:
                print(e)

    # 用于论文搜索推荐
    def recommend_kws(self, raw_dict):
        extr_kws = self.extract_kws(raw_dict)
        # recommed keywords
        for keyword in extr_kws:
            retri = TermRecommendES(self.index, self.ip)
            kws_li = retri.filter(keyword)
            print(kws_li)
            try:
                if kws_li is not None:
                    self.recom_kws.extend(kws_li)
                    return self.recom_kws

            except Exception as e:
                return '暂无推荐'

    # 用于词表搜索推荐
    def recommend_upload_kws(self, upload_kws):
        # recommed keywords
        for keyword in upload_kws:
            retri = TermRecommendES(self.index, self.ip)
            kws_li = retri.filter(keyword)
            print(kws_li)
            try:
                if kws_li is not None:
                    self.recom_kws.extend(kws_li)
                    return self.recom_kws

            except Exception as e:
                return '暂无推荐'

# ******************* 获取粗搜数据 ***************** #


class GetRawResult(object):

    def __init__(self):
        # ES文档索引地址
        self.index = 'cnki_doc'  # 预先存储，后续更改index
        self.ip = '127.0.0.1'

    def get_raw_result(self, multi_kws):
        doc = DocRetireveES(self.index, self.ip)
        multi_fields = ['abstract', 'kws', 'title', 'info', 'fund', 'source']  # 查询所有包含kws的字段
        results = doc.basic_search(multi_fields, multi_kws)
        query = results[0]
        counts = results[1]
        docs = results[2]
        return query, counts, docs


# ******************* 通过表达式获取精搜数据 ***************** #


class GetDetailResult(object):

    def __init__(self):
        # ES文档索引地址
        self.index = 'cnki_doc'  # 预先存储，后续更改index
        self.ip = '127.0.0.1'

    # ************** 无日期筛选 ************* #
    # (1).有且仅有一个表达式 --- 1.1 只有必填项: 单关键词+单字段
    def get_only_expression(self, single_field, single_kws):
        # 1.1.1 无正则匹配: 使用简单搜索
        doc = DocRetireveES(self.index, self.ip)
        # 既然无日期要求，则时间设置成无限长
        start_date = "1900-01-01"
        end_date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
        date = "date"
        in_method = "2"
        exclude_fields = [""]
        exclude_kws = ""
        results = doc.advance_search(single_field, single_kws, exclude_fields, exclude_kws, date, start_date,
                                                 end_date, in_method)
        query = results[0]
        counts = results[1]
        docs = results[2]
        return query, counts, docs

    def get_only_expression_with_regexp(self, inreg_fields, in_reg):
        # 1.1.2 正则匹配: 使用正则搜索
        doc = DocRetireveES(self.index, self.ip)
        # 既然无日期要求，则时间设置成无限长
        start_reg = "1900-01-01"
        end_reg = time.strftime('%Y-%m-%d',time.localtime(time.time()))
        date_reg = "date"
        in_method_reg = "2"
        exreg_fields = [""]
        ex_reg = ""
        results = doc.advance_search_with_regexp(inreg_fields, in_reg, exreg_fields, ex_reg, date_reg, start_reg, end_reg, in_method_reg)
        query = results[0]
        counts = results[1]
        docs = results[2]
        return query, counts, docs

    # (1).有且仅有一个表达式 --- 1.2 不止必填项: 多关键词+单字段+关系
    # '与或'关系通过in_method设置, '非'关系由exclude_fields,exclude_kws设置
    # 单字段: 此时include_fields 与 exclude_fields 应设置成一致
    def get_only_relation_expression(self, include_fields, include_kws, exclude_fields, exclude_kws, in_method):
        # 1.2.1 无正则匹配: 使用高级搜索
        doc = DocRetireveES(self.index, self.ip)
        # 既然无日期要求, 则时间设置成无限长
        start_date = "1900-01-01"
        end_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        date = "date"
        results = doc.advance_search(include_fields, include_kws, exclude_fields, exclude_kws, date, start_date, end_date, in_method)
        query = results[0]
        counts = results[1]
        docs = results[2]
        return query, counts, docs

    # 单字段: 此时include_fields 与 exclude_fields 应设置成一致
    def get_only_relation_expression_with_regexp(self, inreg_fields, in_reg, exreg_fields, ex_reg, in_method_reg):
        # 1.2.2 正则匹配: 使用正则搜索
        doc = DocRetireveES(self.index, self.ip)
        # 既然无日期要求，则时间设置成无限长
        start_reg = "1900-01-01"
        end_reg = time.strftime('%Y-%m-%d',time.localtime(time.time()))
        date_reg = "date"
        results = doc.advance_search_with_regexp(inreg_fields, in_reg, exreg_fields, ex_reg, date_reg, start_reg, end_reg, in_method_reg)
        query = results[0]
        counts = results[1]
        docs = results[2]
        return query, counts, docs

    # (2).多个表达式 --- 2.1 只有必填项: 多关键词+单/多单字段+相邻关系
    # note: 注意include_fields与exclude_fields重复的情况
    def get_multiple_expression(self, raw_expression_group):
        doc = DocRetireveES(self.index, self.ip)
        # 既然无日期要求, 则时间设置成无限长
        start_date = "1900-01-01"
        end_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        date = "date"
        results = doc.wrapped_advance_search(raw_expression_group, date, start_date, end_date)
        query = results[0]
        counts = results[1]
        docs = results[2]
        return query, counts, docs

    # ************** 有日期筛选 ************* #
    # (1).有且仅有一个表达式 --- 1.1 只有必填项: 单关键词+单字段
    def get_only_expression_with_date(self, single_field, single_kws, start_date, end_date):
        # 1.1.1 无正则匹配: 使用简单搜索
        doc = DocRetireveES(self.index, self.ip)
        date = "date"
        in_method = "2"
        exclude_fields = [""]
        exclude_kws = ""
        results = doc.advance_search_with_regexp(single_field, single_kws, exclude_fields, exclude_kws, date, start_date,
                                                 end_date, in_method)
        query = results[0]
        counts = results[1]
        docs = results[2]
        return query, counts, docs

    def get_only_expression_with_regexp_and_date(self, inreg_fields, in_reg, start_reg, end_reg):
        # 1.1.2 正则匹配: 使用正则搜索
        doc = DocRetireveES(self.index, self.ip)
        date_reg = "date"
        in_method_reg = "2"
        exreg_fields = [""]
        ex_reg = ""
        results = doc.advance_search_with_regexp(inreg_fields, in_reg, exreg_fields, ex_reg, date_reg, start_reg, end_reg, in_method_reg)
        query = results[0]
        counts = results[1]
        docs = results[2]
        return query, counts, docs

    # (1).有且仅有一个表达式 --- 1.2 不止必填项: 多关键词+单字段+关系
    # '与或'关系通过in_method设置, '非'关系由exclude_fields,exclude_kws设置
    # 单字段: 此时include_fields 与 exclude_fields 应设置成一致
    def get_only_relation_expression_with_date(self, include_fields, include_kws, exclude_fields, exclude_kws, start_date, end_date, in_method):
        # 1.2.1 无正则匹配: 使用高级搜索
        doc = DocRetireveES(self.index, self.ip)
        date = "date"
        results = doc.advance_search(include_fields, include_kws, exclude_fields, exclude_kws, date, start_date, end_date, in_method)
        query = results[0]
        counts = results[1]
        docs = results[2]
        return query, counts, docs

    # 单字段: 此时include_fields 与 exclude_fields 应设置成一致
    def get_only_relation_expression_with_regexp_and_date(self, inreg_fields, in_reg, exreg_fields, ex_reg, start_reg, end_reg, in_method_reg):
        # 1.2.2 正则匹配: 使用正则搜索
        doc = DocRetireveES(self.index, self.ip)
        date_reg = "date"
        results = doc.advance_search_with_regexp(inreg_fields, in_reg, exreg_fields, ex_reg, date_reg, start_reg, end_reg, in_method_reg)
        query = results[0]
        counts = results[1]
        docs = results[2]
        return query, counts, docs

    # (2).多个表达式 --- 2.1 只有必填项: 多关键词+单/多单字段+相邻关系
    # note: 注意include_fields与exclude_fields重复的情况
    def get_multiple_expression_with_date(self, raw_expression_group, start_date, end_date):
        doc = DocRetireveES(self.index, self.ip)
        date = "date"
        results = doc.wrapped_advance_search(raw_expression_group, date, start_date, end_date)
        query = results[0]
        counts = results[1]
        docs = results[2]
        return query, counts, docs
