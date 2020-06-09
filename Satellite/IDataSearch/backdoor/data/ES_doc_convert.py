#!/usr/bin/env python
# -*-coding:utf-8-*-
'''
    目的：论文爬取数据清洗
    @ 此文件用于获取ES导入的json格式
'''
import os
import json
import codecs
import pandas as pd


class ESDocConvert(object):

    # 修改csv
    def edifycsv(self, file):
        df = pd.read_csv(file, encoding='utf-8', header=0)
        df = df.drop(['id'], axis=1)
        for col in df:
            df[col] = df[col].astype(str).replace(',', '，', regex=True).replace('\r', '', regex=True).replace('\n', '', regex=True)
        df.to_csv(file, index=False, encoding='utf-8')

    def convert2json(self, file, json_file):
        self.edifycsv(file)
        fin = codecs.open(file, 'r', encoding='utf-8')
        info = []
        for f in fin:
            f_1 = f.replace('\n', '')
            info.append(f_1.split(','))
        fin.close()
        fout = codecs.open(json_file, 'w+', encoding='utf-8')
        for i in range(1, len(info)):
            info[i] = dict(zip(info[0], info[i]))

            json.dump(info[i], fout, ensure_ascii=False)  # 解决中文乱码
            fout.write('\n')
        fout.close()


if __name__ == "__main__":
    os.chdir('')  # 自定义路径
    file = 'amino_acid.csv'
    doc = ESDocConvert()
    doc.convert2json(file, json_file='doc_json.txt')
