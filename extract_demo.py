import os
import re
import sys
import json
from core.nlp import NLP
from core.extractor import Extractor

if __name__ == '__main__':
    input_path = './data/name_wiki.json'  # 输入的文本文件
    output_path = './data/knowledge_triple.json'  # 输出的处理结果Json文件
    if os.path.isfile(output_path):
        os.remove(output_path)
    # os.mkdir(output_path)

    print('Start extracting...')

    # 实例化NLP(分词，词性标注，命名实体识别，依存句法分析)
    nlp = NLP()
    num = 1  # 知识三元组


    with open(input_path, 'r', encoding='utf-8') as f_in:
        # 遍历每一篇文档中的句子
        id = 0
        for line in f_in:
            l = json.loads(line)
            # print(l)
            # 分句，获得句子列表
            origin_sentences = re.split('[。]|\n', l['text'])
            # origin_sentences = ['1872年，孙入翠亨村私塾，接受国学启蒙教育。']##测试用
            for origin_sentence in origin_sentences:
                origin_sentence = origin_sentence.strip()
                id += 1
                # 原始句子长度小于6，跳过
                if (len(origin_sentence) < 6):
                    continue
                # 分词处理
                lemmas, postags = nlp.segment_postag(origin_sentence)
                # print("lemmas:", lemmas)
                # 词性标注
                words_postag = nlp.storage_unit(lemmas, postags)

                # 命名实体识别
                #原方式用的是LTP模型
                # words_netag = nlp.netag(words_postag)

                # 依存句法分析
                sentence = nlp.parse(words_postag)

                extractor = Extractor()
                num = extractor.extract(id, origin_sentence, sentence, output_path, num)
            # break
