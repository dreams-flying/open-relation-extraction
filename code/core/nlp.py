import os
import sys
sys.path.append("..")  # 先跳出当前目录
from bean.word_unit import WordUnit
from bean.sentence_unit import SentenceUnit
from core.entity_combine import EntityCombine

from LAC import LAC

from ddparser import DDParser

def combine(lac_result):
    """合并部分分词结果
    此部分主要合并连续的LOC结果，使其形成一个整体
    例子：国家主席习近平视察 中国 福建 厦门
    """
    flag1 = -1
    flag2 = -1
    wordList = []
    postagList = []
    tempList = []
    for i, (word, postag) in enumerate(zip(lac_result[0], lac_result[1])):
        if postag == 'LOC':
            flag1 = i
            tempList.append(word)
            j = i+1
            while j < len(lac_result[0]):
                if lac_result[1][j] == 'LOC':
                    tempList.append(lac_result[0][j])
                    j = j+1
                else:
                    flag2 = j
                    break
            break
    if flag1 != -1:
        k1 = 0
        while k1 < flag1:
            wordList.append(lac_result[0][k1])
            postagList.append(lac_result[1][k1])
            k1 += 1
        wordList.append(''.join(tempList))
        postagList.append('LOC')
        k2 = flag2
        while k2 < len(lac_result[0]):
            wordList.append(lac_result[0][k2])
            postagList.append(lac_result[1][k2])
            k2 += 1
        return [wordList, postagList]
    else:
        return lac_result

class NLP:
    """进行自然语言处理，包括分词，词性标注，命名实体识别，依存句法分析
    Attributes:
        default_user_dict_dir: str，用户自定义词典目录
    """
    default_user_dict_dir = './resource/user_dict.txt'  # 默认的用户词典目录

    # print(tex)
    
    def __init__(self, user_dict_dir=default_user_dict_dir):
        self.default_user_dict_dir = user_dict_dir
        # 加载LAC模型
        # 分词和词性标注模型
        self.lac = LAC(mode='lac')

        # 添加用户词典
        # 装载干预词典, sep参数表示词典文件采用的分隔符，为None时默认使用空格或制表符'\t'
        self.lac.load_customization(self.default_user_dict_dir, sep='\n')

        # 依存句法分析模型
        self.ddp = DDParser()

    def segment_postag(self, sentence):
        """进行分词和词性标注处理
        Args:
            sentence: string，句子
        Returns:
            lemmas: list，分词结果
            postags: list，词性标注结果
        """
        # 分词和词性标注
        lemmas, postags = [], []
        lac_result = self.lac.run(sentence)
        # print(lac_result)
        lac_result = combine(lac_result)
        # print(lac_rult)
        for word in lac_result[0]:
            lemmas.append(word)
        for word in lac_result[1]:
            if word == 'LOC':#LOC-->ns
                word = 'ns'
            if word == 'PER':#PER-->nh
                word = 'nh'
            if word == 'ORG':#ORG-->ni
                word = 'ni'
            if word == 'TIME':#TIME-->nt
                word = 'nt'
            postags.append(word)
        return lemmas, postags

    def storage_unit(self, lemmas, postags):
        """存储分词和词性标注结果
        Args:
            lemmas: list，分词后的结果
            postags: list，词性标注结果
        Returns:
            words: WordUnit list，包含分词与词性标注结果
        """
        words = []  # 存储句子处理后的词单元

        for i in range(len(lemmas)):
            # 存储分词与词性标记后的词单元WordUnit，编号从1开始
            word = WordUnit(i+1, lemmas[i], postags[i])
            words.append(word)
        return words

    def netag(self, words):
        """命名实体识别，并对分词与词性标注后的结果进行命名实体识别与合并
          目前代码中没有用到，原方式用的是LTP模型。一种简单的方式是利用combine()函数
        Args:
            words: WordUnit list，包含分词与词性标注结果
        Returns:
            words_netag: WordUnit list，包含分词，词性标注与命名实体识别结果
        """
        # for word in words:
        #     print(word.to_string())
        # print(kk)
        lemmas = []  # 存储分词后的结果
        postags = []  # 存储词性标书结果
        for word in words:
            lemmas.append(word.lemma)
            postags.append(word.postag)
        # 命名实体识别
        netags = self.recognizer.recognize(lemmas, postags)
        # print('\t'.join(netags))  # just for test
        words_netag = EntityCombine().combine(words, netags)
        return words_netag

    def parse(self, words):
        """对分词，词性标注与命名实体识别后的结果进行依存句法分析(命名实体识别可选)
        Args:
            words_netag: WordUnit list，包含分词，词性标注与命名实体识别结果
        Returns:
            *: SentenceUnit，该句子单元
        """
        lemmas = []  # 分词结果
        postags = []  # 词性标注结果
        for word in words:
            lemmas.append(word.lemma)
            postags.append(word.postag)
        # 依存句法分析
        arcs=self.ddp.parse_seg([lemmas])
        for arc in arcs:
            for i in range(len(arc['word'])):
                words[i].head = arc['head'][i]
                words[i].dependency = arc['deprel'][i]
        return SentenceUnit(words)

if __name__ == '__main__':
    nlp = NLP()
    # 分词和词性标注测试
    sentence = '中国首都北京'
    lemmas, postags = nlp.segment_postag(sentence)
    print(lemmas)
    print(postags)

    words = nlp.storage_unit(lemmas, postags)
    # for word in words:
    #     print(word.to_string())

    # 依存句法分析测试
    # print('***' + '依存句法分析测试' + '***')
    sentence = nlp.parse(words)
    print(sentence.to_string())
    # print('sentence0 head: ' + sentence.words[0].head_word.lemma)

