# -*- coding: utf-8 -*-
'''
    SSRP演示平台之爬虫运行主函数
'''

from SSRP_CNKIspider import CnkispaceSpider
from SSRP_CQVIPspider import CqvipSpider
from SSRP_WFspider import WFdataspider
from ES_doc_convert import ESDocConvert
from settings import CommonSettings

from threading import Thread
import time


class SpiderThreadings(object):

    def cnki_task(self, search_word):
        cnki = CnkispaceSpider()
        cnki.get_candidate_words(search_word)
        time.sleep(2)

    def cqvip_task(self, search_word):
        cq = CqvipSpider()
        cq.save_data(search_word)
        time.sleep(2)

    def wanfang_task(self, search_word):
        wf = WFdataspider()
        wf.pandas_save_data(search_word)
        time.sleep(2)


def main():
    """
    search_word: from前台
    :return:
    """

    # ************ 爬取 ************* #
    sp = SpiderThreadings()
    th1 = Thread(target=sp.cnki_task(search_word))
    th2 = Thread(target=sp.cqvip_task(search_word))
    th3 = Thread(target=sp.wanfang_task(search_word))
    th1.start()
    th2.start()
    th3.start()

    # ************ 读取 ************* #
    com = CommonSettings()
    csv_files = com.set_common_output()
    cnki_csv = csv_files[0]
    cqvip_csv = csv_files[1]
    wanfang_csv = csv_files[2]

    # ************ 转换 ************* #
    doc = ESDocConvert()
    doc.convert2json(cnki_csv, json_file='cnki_doc_json.txt')
    print('Convert cnki_data successfully!')
    time.sleep(1)
    doc.convert2json(cqvip_csv, json_file='cqvip_doc_json.txt')
    print('Convert cqvip_data successfully!')
    time.sleep(1)
    doc.convert2json(wanfang_csv, json_file='wf_doc_json.txt')
    print('Convert wanfang_data successfully!')


if __name__ == '__main__':
    main()
