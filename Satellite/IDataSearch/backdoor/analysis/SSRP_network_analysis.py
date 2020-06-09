# -*- coding: utf-8 -*-
'''
    SSRP分析平台之关系图分析 --- 关键词共现
'''

import numpy as np
import collections
from sklearn.decomposition import PCA


class NetworkAnalysis(object):

    def __init__(self):
        self.path = 'co-occurence-matrix.txt'

    def build_word_dict(self, words):
        key_list = list(set([key for key in words if key != '']))
        key_dict = {}
        pos = 0

        for i in key_list:
            pos += 1
            key_dict[pos] = str(i)
        # print(key_dict)
        return key_dict

    def build_matrix(self, x, y):
        return [[0 for j in range(y)] for i in range(x)]

    def init_matrix(self, matrix, dic, length):
        # matrix[0][0] = '+'
        for i in range(1, length):
            matrix[0][i] = dic[i]
        for i in range(1, length):
            matrix[i][0] = dic[i]
        # print(matrix)
        return matrix

    def show_matrix(self, matrix):
        matrix_text = ''
        count = 0
        for i in range(0, len(matrix)):
            for j in range(0, len(matrix)):
                matrix_text = matrix_text + str(matrix[i][j]) + '\t'
            matrix_text = matrix_text[:-1] + '\n'
            count += 1
            # print('No.' + str(count) + 'had been done!')
        # print(matrix_text)
        return matrix_text

    def count_matrix(self, matrix, length, key_list):
        for i in range(1, length):
            for j in range(1, length):
                count = 0
                for key in key_list:
                    ech = str(key).split()
                    if str(matrix[0][i]) in ech and str(matrix[j][0]) in ech and str(matrix[0][i]) != str(matrix[j][0]):
                        count += 1
                    else:
                        continue
                matrix[i][j] = str(count)
        # print(matrix)
        return matrix

    def write(self, text):
        with open(self.path, 'w+', encoding='utf-8') as f:
            f.write(text)
        return self.path + ' is ok!'

    def main(self):
        key_dict = self.build_word_dict()
        length = len(key_dict) + 1
        matrix = self.build_matrix(length, length)
        # print('Matrix had been built successfully!')
        matrix = self.init_matrix(matrix, key_dict, length)
        # print('Col and row had been writen!')
        matrix = self.count_matrix(matrix, length, self.words)
        # print('Matrix had been counted successfully!')
        matrixtxt = self.show_matrix(matrix)
        self.write(matrixtxt)


class WordVector(object):
    def __init__(self):
        self.network = NetworkAnalysis()
        self.dataset = self.network.words
        self.min_count = 1  # 最小词频
        self.window_size = 5
        self.word_demension = 10
        self.embedding_path = 'word2word_wordvec.bin'

    # 统计总词数
    def build_word_dict(self):
        words = []
        for data in self.dataset:
            words.extend(data)
        reserved_words = [item for item in collections.Counter(words).most_common() if item[1] >= self.min_count]
        word_dict = {item[0]:item[1] for item in reserved_words}
        # print(word_dict)
        return word_dict

    # 构造上下文窗口
    def build_word2word_dict(self):
        word2word_dict = {}
        for data_index, data in enumerate(self.dataset):
            for index in range(len(data)):
                if index < self.window_size:
                    left = data[:index]
                else:
                    left = data[index - self.window_size: index]
                if index + self.window_size > len(data):
                    right = data[index + 1:]
                else:
                    right = data[index + 1: index + self.window_size + 1]
                context = left + [data[index]] + right
                for word in context:
                    if word not in word2word_dict:
                        word2word_dict[word] = {}
                    else:
                        for co_word in context:
                            if co_word != word:
                                if co_word not in word2word_dict[word]:
                                    word2word_dict[word][co_word] = 1
                                else:
                                    word2word_dict[word][co_word] += 1
        # print(word2word_dict)
        return word2word_dict

    # *********************** 方法1：不使用scipy---完整版 ************************** #
    # 构造词词共现矩阵
    def build_word2word_matrix(self):
        word2word_dict = self.build_word2word_dict()
        word_dict = self.build_word_dict()
        word_list = list(word_dict)
        word2word_matrix = self.init_word2word_matrix()[1]
        length = self.init_word2word_matrix()[0]
        # words_all = len(word_list)
        for i in range(1, length):
            for j in range(1, length):
                sum_tf = sum(word2word_dict[word_list[i - 1]].values())
                weight = word2word_dict[word_list[i - 1]].get(word_list[j - 1], 0) / sum_tf
                word2word_matrix[i][j] = weight

        # print(word2word_matrix)
        return word2word_matrix

    # 构造初始矩阵格式
    def init_word2word_matrix(self):
        word_names = list(self.build_word_dict().keys())
        key_dict = {}
        pos = 0

        for i in word_names:
            pos += 1
            key_dict[pos] = str(i)
        # print(key_dict)
        length = len(key_dict) + 1
        raw_matrix = self.network.build_matrix(length, length)
        empty_matrix = self.network.init_matrix(raw_matrix, key_dict, length)

        # print(empty_matrix)
        return length, empty_matrix

    # *********************** 方法2：使用scipy---纯数字版 ************************** #
    # 构造词词共现矩阵
    def build_word2word_scipy_matrix(self):
        word2word_dict = self.build_word2word_dict()
        word_dict = self.build_word_dict()
        word_list = list(word_dict)
        length = self.init_word2word_scipy_matrix()

        rows, cols, data = [], [], []
        for i in range(1, length):
            for j in range(1, length):
                sum_tf = sum(word2word_dict[word_list[i - 1]].values())
                weight = word2word_dict[word_list[i - 1]].get(word_list[j - 1], 0) / sum_tf
                if weight != 0:
                    rows.append(i)
                    cols.append(j)
                    data.append(weight)
                else:
                    continue

        # 共现度计算非0值
        # print('矩阵的行索引为%s' % rows)
        # print('矩阵的列索引为%s' % cols)
        # print('矩阵的数据为%s' % data)

        row = np.array(rows)
        col = np.array(cols)
        datum = np.array(data)

        scipy_matrix = self.build_advance_matrix(datum, row, col)
        return scipy_matrix, rows, cols, data

    # 利用方法二构造关系图数据格式
    def build_network_scipy_data(self):
        rows = self.build_word2word_scipy_matrix()[1]
        cols = self.build_word2word_scipy_matrix()[2]
        data = self.build_word2word_scipy_matrix()[3]
        word_names = list(self.build_word_dict().keys())
        id = 1
        nodes = []
        for name in word_names:
            node = {}
            node['id'] = id
            node['label'] = name
            nodes.append(node)
            id += 1
        # print(nodes)
        edges = []
        for sou, tar, val in zip(rows, cols, data):
            network = {}
            network['from'] = sou
            network['to'] = tar
            network['value'] = val
            edges.append(network)
        # print(edges)
        return nodes, edges

    # scipy---coo_matrix方法, 节省内存空间
    def build_advance_matrix(self, datum, row, col):
        from scipy.sparse import coo_matrix
        word_vector = coo_matrix((datum, (row, col)), shape=(len(row), len(col))).toarray()
        # print(word_vector)
        return word_vector

    # 构造初始矩阵格式
    def init_word2word_scipy_matrix(self):
        word_names = list(self.build_word_dict().keys())
        key_dict = {}
        pos = 0

        for i in word_names:
            pos += 1
            key_dict[pos] = str(i)
        # print(key_dict)
        length = len(key_dict) + 1
        return length

    # 打印最终矩阵格式
    def show_word2word_matrix(self):
        matrix = self.build_word2word_matrix()
        format = self.network.show_matrix(matrix)
        return format

    # 利用方法一构造关系图数据格式
    def build_network_data(self):
        word2word_matrix = self.build_word2word_matrix()
        word_names = list(self.build_word_dict().keys())
        # print(word2word_matrix)
        i = 0
        network_data = []
        while i < len(word_names):
            network = {}
            network['source'] = word_names[i]
            j = 0
            while j < len(word_names):
                network['target'] = word_names[j]
                if int(word2word_matrix[i+1][j]) > 0:
                    network['value'] = int(word2word_matrix[i+1][j+1])
                    network_data.append(network)
                j += 1
            i += 1

        # print(network_data)
        return network_data

    # 使用PCA进行降维
    def low_dimension(self):
        worddoc_matrix = self.build_word2word_matrix()
        pca = PCA(n_components=self.word_demension)
        low_embedding = pca.fit_transform(worddoc_matrix)
        # print(low_embedding)
        return low_embedding

    # 保存模型
    def train_embedding(self):
        # print('training.....')
        word_list = list(self.build_word_dict().keys())
        word_dict = {index: word for index, word in enumerate(word_list)}
        word_embedding_dict = {index: embedding for index, embedding in enumerate(self.low_dimension())}
        # print('saving models.....')
        with open(self.embedding_path, 'w+') as f:
            for word_index, word_embedding in word_embedding_dict.items():
                word_word = word_dict[word_index]
                word_embedding = [str(item) for item in word_embedding]
                f.write(word_word + '\t' + ','.join(word_embedding) + '\n')
        f.close()
        # print('done.....')


if __name__ == '__main__':
    vec = WordVector()
    vec.build_network_scipy_data()
