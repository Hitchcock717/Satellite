#!/usr/bin/env python
# -*-coding:utf-8-*-
'''
    目的：论文推荐方法1-----基于作者两两合作关系, 寻找新的连通分量

'''

import codecs
from ES_doc_export import *


class DocRecommend1ES(object):

    def __init__(self, index_name, ip):
        self.data = DocExportES(index_name, ip)

    def get_data(self,file, file2, num):
        self.data.get_range_data(file, file2, num)

    def process_data(self, file, file2, num):
        self.get_data(file, file2, num)
        df = pd.read_csv(file2, header=None)
        s = df.iloc[:, [3]]
        s1 = s.dropna()

        # 转换成Series
        ser = pd.Series(s1.values.flatten())

        # 删除单个作者
        bool_1 = ser.str.contains('.*;.*')
        filter_1 = ser[bool_1]
        bool1 = ser.str.contains('.*；.*')
        filter1 = ser[bool1]

        # 拼接过滤出的两个作者序列
        new_ser = pd.concat([filter_1, filter1])
        new_ser1 = new_ser.str.replace('；', ';')
        new_ser2 = new_ser1.str.replace(';$', '')
        new_ser3 = new_ser2.str.replace(' ', '')
        new_ser4 = new_ser3.str.replace('^[\u4e00-\u9fa5]+$', '')
        new_ser5 = new_ser4.str.replace(';', ',')
        new_ser6 = new_ser5.str.replace(',$', '')

        # series先转list，再转dataframe [series--->df]
        # new_df_list = {'author': new_ser6.values}
        # new_df = pd.DataFrame(new_df_list)
        # new_df1 = new_ser6.isnull().value_counts()
        # 发现无空值
        # 若有空值，可执行df.dropna(axis=0, how='any', inplace=True)

        # 过滤两位作者合作的情况
        new_bool1 = new_ser6.str.contains('^[^,]*,[^,]*$')

        # 过滤两位作者以上合作的情况
        new_bool = new_ser5.str.contains('.*,.*,.*')
        filter_more_aus = new_ser5[new_bool]

        # 将多位合作作者转化为两两一组
        # 该方法只能实现顺序分隔
        test = filter_more_aus.iloc[0]
        a = test.split(',')
        b = [a[i:i + 2] for i in range(0, len(a), 2)]

        # 排列组合
        import itertools
        test = filter_more_aus.iloc[0]
        a = test.split(',')
        result = list(itertools.combinations(a, 2))

        more_aus_data = []
        more_aus_list = filter_more_aus.str.split(',')
        for aus in more_aus_list:
            aus_combi = list(itertools.combinations(aus, 2))
            more_aus_data.extend(aus_combi)
        filter_two_aus = new_ser6[new_bool1]

        two_aus_data = []
        two_aus_list = filter_two_aus.str.split(',')
        for aus in two_aus_list:
            aus_combi = list(itertools.combinations(aus, 2))
            two_aus_data.extend(aus_combi)

        # 合并所有作者两两之间的关系
        aus_data = []
        more_aus_data.extend(two_aus_data)
        aus_data.extend(more_aus_data)

        # 清洗,删去无用关系
        for aus in aus_data:
            aus_check = aus[1]
            if aus_check == '':
                aus_data.remove(aus)

        # 作者数据准备完成
        print(aus_data)
        return aus_data

    def export_data(self,file, file2, file3, num):
        clean_data = self.process_data(file, file2, num)
        fout = codecs.open(file3, 'w+', encoding='utf-8')
        for clean in clean_data:
            fout.write(str(clean))
        fout.flush()
        fout.close()


if __name__ == "__main__":
    index = 'cnki_doc'
    localhost = '127.0.0.1'
    rec = DocRecommend1ES(index, localhost)
    os.chdir('')  # 自定义路径
    file = 'cnki_doc1.csv'  # 搜索统计表
    file2 = 'today.csv'     # 推荐过滤表
    file3 = 'author_data.txt'  # 作者合作关系表
    # rec.process_data(file, file2, num=100)
