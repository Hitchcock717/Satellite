#!/usr/bin/env python
# -*-coding:utf-8-*-
'''
    目的: 向Elasticsearch插入json数据 （localhost:9200)
    打印插入成功信息：{'acknowledged': True, 'shards_acknowledged': True, 'index': 'cnki_term'}
    TODO:ik、pinyin分词器和stconvert繁简转换包版本已更新至7.6.1
'''

import os
import codecs
from elasticsearch.helpers import bulk
from ES_connect import *
from ES_build_mappings import *


class Insert2ES(object):

    def __init__(self, index_name, ip):
        self.conn = Connect2ES(index_name, ip)
        self.map = BuildMappings()

    def create_index(self):
        '''
        create index
        :param ex: Elasticsearch object
        :return:
        '''
        '''
        两种分词器使用的最佳实践是：索引时用ik_max_word，在搜索时用ik_smart。
        即：索引时最大化的将文章内容分词，搜索时更精确的搜索到想要的结果。
        '''
        # 选择插入数据源
        index_mappings = self.map.doc_map()
        # index_mappings = self.map.detail_map()
        # index_mappings = self.map.simple_map()

        if self.conn.es.indices.exists(index=self.conn.index_name) is not True:  # 无重复index
            self.conn.es.indices.create(index=self.conn.index_name, body=index_mappings, ignore=[400,409])
            print("Create {} mapping successfully.".format(self.conn.index_name))
        else:
            print("index({}) already exists.".format(self.conn.index_name))

    def get_folder(self, folder_path):

        files = os.listdir(folder_path)
        res = []
        for file in files:
            if not os.path.isdir(file):
                fin = codecs.open(folder_path + '/' + file, 'r', encoding='utf-8')  # 若在mac环境下, 需提前删除文件夹下的.DS_Store文件
                                                                                    # ls -a
                                                                                    # rm.DS_Store
                data = self.insert_data(fin)
                res.append(data)
        print(res)

    def insert_data(self, json_file):
        fin = codecs.open(json_file, 'r', encoding='utf-8')
        data = []
        for f in fin.readlines():
            data.append(f)
        # print(data)
        fin.close()
        return data

    def build_data(self, json_file):
        input_data = self.insert_data(json_file)

        actions = []
        i = 1
        bulk_num = 5000

        for line in input_data:
            new_line = eval(line)
            action = {
                      "_index": self.conn.index_name,
                      "_id": i,
                      "_source": {
                                  "title": new_line["title"],
                                  "author": new_line["author"],
                                  "source": new_line["source"],
                                  "info": new_line["info"],
                                  "date": new_line["date"],
                                  "kws": new_line["kws"],
                                  "fund": new_line["fund"],
                                  "abstract": new_line["abstract"],
                                  "cited": new_line["cited"],
                                  "downed": new_line["downed"],
                                  "download": new_line["download"]
                                }
                     }
            i += 1
            actions.append(action)

            from tqdm import tqdm
            if len(actions) == bulk_num:
                print("共需要插入%d条..." % len(actions))
                pbar = tqdm(total=len(actions))
                success, _ = bulk(self.conn.es, actions, index=self.conn.index_name, raise_on_error=True)
                pbar.update(bulk_num)
                del actions[0:len(actions)]  # release space
                pbar.close()
                print(success)

        if len(actions) > 0:
            success, _ = bulk(self.conn.es, actions, index=self.conn.index_name, raise_on_error=True)
            del actions[0:len(actions)]
            print('Perform %d actions' % success)


if __name__ == "__main__":
    index = 'spider_data'  # new index
    ip = '127.0.0.1'
    json_file = 'doc_json.txt'
    insert = Insert2ES(index, ip)
    insert.create_index()
    insert.build_data(json_file)


















