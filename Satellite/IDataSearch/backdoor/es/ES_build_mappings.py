#!/usr/bin/env python
# -*-coding:utf-8-*-
'''
    目的: 为术语和文档分别构造不同的ES映射
'''


class BuildMappings(object):

    def doc_map(self):

        # ********************************** start doc mappings ******************************** #

        index_mappings = {
            "mappings": {
                "properties": {
                    "suggest": {
                        'type': 'completion', "analyzer": "ik_max_word", "filter": ["lowercase"]
                    },
                    "title": {
                        'type': 'text', "index": "true","analyzer": "ik_max_word","search_analyzer": "ik_smart"
                    },
                    "author": {
                        'type': 'text', "index": "true","analyzer": "ik_max_word","search_analyzer": "ik_smart"
                    },
                    "info": {
                        'type': 'text', "index": "true","analyzer": "ik_max_word","search_analyzer": "ik_smart"
                    },
                    "source": {
                        'type': 'keyword', "index": "true"
                    },
                    "date": {
                        'type': 'text', "index": "true"  # 解决日期格式不统一
                    },
                    "kws": {
                        'type': 'keyword', "index": "true"
                    },
                    "fund": {
                        'type': 'text', "index": "true","analyzer": "ik_max_word","search_analyzer": "ik_smart"
                    },
                    "abstract": {
                        'type': 'text', "index": "true","analyzer": "ik_max_word","search_analyzer": "ik_smart"
                    },
                    "download": {
                        'type': 'keyword', "index": "true"
                    },
                    "cited": {
                        'type': 'integer', "index": "true"
                    },
                    "downed": {
                        'type': 'integer', "index": "true"
                    }
                }
            }
        }
        return index_mappings

        # ********************************** end doc mappings ******************************** #

    def detail_map(self):

        # ********************************** start detail term mappings ******************************** #

        index_mappings = {
            "mappings":{
                    "properties":{
                        "name":{
                            'type':'text', "analyzer": "ik_max_word","search_analyzer": "ik_smart","index":"true"
                        },
                        "trans":{
                            'type':'text', "analyzer": "ik_max_word","search_analyzer": "ik_smart","index":"true"
                        },
                        "subject":{
                            'type':'text',"index":"true"
                    }
                }
            }
        }
        return index_mappings

        # ********************************** end detail term mappings ******************************** #

    def simple_map(self):

        # ********************************** start simple term mappings ******************************** #

        index_mappings = {
            "mappings":{
                    "properties":{
                        "name":{
                            'type':'text', "analyzer": "ik_max_word","search_analyzer": "ik_smart","index":"true"
                        },
                        "subject":{
                            'type':'text',"index":"true"
                    }
                }
            }
        }
        return index_mappings

        # ********************************** end simple term mappings ******************************** #

