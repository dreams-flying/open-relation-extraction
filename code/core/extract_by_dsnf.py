import sys
sys.path.append("..")  # 先跳出当前目录
from bean.word_unit import WordUnit
from tool.append_to_json import AppendToJson

class ExtractByDSNF:
    """根据DSNF(Dependency Semantic Normal Forms)进行知识抽取"""
    origin_sentence = ''  # str，原始句子
    sentence = None  # SentenceUnit，句子表示，每行为一个词
    entity1 = None  # WordUnit，实体1词单元
    entity2 = None  # WordUnit，实体2词单元
    head_relation = None  # WordUnit，头部关系词单元
    file_path = None  # Element，XML文档
    num = 1  # 三元组数量编号

    def __init__(self, id, origin_sentence, sentence, entity1, entity2, file_path, num):
        self.origin_sentence = origin_sentence
        self.sentence = sentence
        self.entity1 = entity1
        self.entity2 = entity2
        self.file_path = file_path
        self.num = num
        self.id = id

    def is_entity(self, entry):
        """判断词单元是否实体
        Args:
            entry: WordUnit，词单元
        Returns:
            *: bool，实体(True)，非实体(False)
        """
        # 候选实体词性列表
        # nh:人名；ni:组织名；ns:地名；nz:其它专有名词；nw:作品名；nt:时间名词
        entity_postags = {'nh', 'ni', 'ns', 'nz', 'nw', 'nt'}
        if entry.postag in entity_postags:
            return True
        else:
            return False

    def check_entity(self, entity):
        """处理偏正结构(奥巴马总统)，得到偏正部分(总统)，句子成分的主语或宾语
           奥巴马<-(ATT)-总统
           "the head word is a entity and modifiers are called the modifying attributives"
        Args:
            entity: WordUnit，待检验的实体
        Returns:
            head_word or entity: WordUnit，检验后的实体
        """
        head_word = entity.head_word  # 中心词
        if entity.dependency == 'ATT':
            if self.like_noun(head_word) and abs(entity.ID - head_word.ID) == 1:
                return head_word
            else:
                return entity
        else:
            return entity

    def search_entity(self, modify):
        """根据偏正部分(也有可能是实体)找原实体
        Args:
            word: WordUnit，偏正部分或者实体
        Returns:
        """
        for word in self.sentence.words:
            if word.head == modify.ID and word.dependency == 'ATT':
                return word
        return modify

    def like_noun(self, entry):
        """近似名词，根据词性标注判断此名词是否职位相关
        Args:
            entry: WordUnit，词单元
        Return:
            *: bool，判断结果，职位相关(True)，职位不相关(False)
        """
        # LAC
        noun = {'n', 'f', 's', 'nw', 'nz', 'ni', 'nh', 'ns', 'r', 'nt'}
        if entry.postag in noun:
            return True
        else:
            return False

    def get_entity_num_between(self, entity1, entity2):
        """获得两个实体之间的实体数量
        Args:
            entity1: WordUnit，实体1
            entity2: WordUnit，实体2
        Returns:
            num: int，两实体间的实体数量
        """
        num = 0
        i = entity1.ID + 1
        while i < entity2.ID:
            if self.is_entity(self.sentence.words[i]):
                num += 1
            i += 1
        return num

    def build_triple(self, entity1, entity2, relation):
        """建立三元组，写入json文件
        Args:
            entity1: WordUnit，实体1
            entity2: WordUnit，实体2
            relation: str list，关系列表
            num: int，知识三元组编号
        Returns:
            True: 获得三元组(True)
        """
        triple = dict()
        triple['ID'] = self.id
        triple['编号'] = self.num
        self.num += 1
        triple['句子'] = self.origin_sentence
        entity1_str = self.element_connect(entity1)
        entity2_str = self.element_connect(entity2)
        relation_str = self.element_connect(relation)
        triple['知识'] = [entity1_str, relation_str, entity2_str]
        AppendToJson().append(self.file_path, triple)
        print('triple: ' + entity1_str + '\t' + relation_str + '\t' + entity2_str)
        return True

    def element_connect(self, element):
        """三元组元素连接
        Args:
            element: WordUnit list，元素列表
        Returns:
            element_str: str，连接后的字符串
        """
        element_str = ''
        if isinstance(element, list):
            for ele in element:
                if isinstance(ele, WordUnit):
                    element_str += ele.lemma
        else:
            element_str = element.lemma
        return element_str

    def SBV_CMP_POB(self, entity1, entity2):
        """IVC(Intransitive Verb Construction)[DSNF4]
            不及物动词结构的一种形式，例如："奥巴马总统毕业于哈佛大学"--->"奥巴马 毕业 于 哈佛 大学"
            经过命名实体后，合并分词结果将是"奥巴马 毕业 于 哈佛大学"
            entity1--->"奥巴马"    entity2--->"哈弗大学"
        Args:
            entity1: WordUnit，原实体1
            entity2: WordUnit，原实体2
        Returns:
            *: bool，获得三元组(True)，未获得三元组(False)
        """
        ent1 = self.check_entity(entity1)  #　偏正部分，若无偏正部分则就是原实体
        ent2 = self.check_entity(entity2)
        if ent2.dependency == 'POB' and ent2.head_word.dependency == 'CMP':
            if ent1.dependency == 'SBV' and ent1.head == ent2.head_word.head:
                relations = []  # 实体间的关系
                relations.append(ent1.head_word)  # 该实例对应为"毕业"
                relations.append(ent2.head_word)  # 该实例对应为"于"
                return self.build_triple(entity1, entity2, relations)
        return False

    def SBV_VOB(self, entity1, entity2):
        """TV(Transitive Verb)
            [DSNF2]
        Args:
            entity1: WordUnit，原实体1
            entity2: WordUnit，原实体2
        Returns:
            *: bool，获得三元组(True)，未获得三元组(False)
        """
        # print(entity1)
        ent1 = self.check_entity(entity1) #　偏正部分，若无偏正部分则就是原实体
        ent2 = self.check_entity(entity2)
        if ent1.dependency == 'SBV' and ent2.dependency == 'VOB':
            return self.determine_relation_SVB(entity1, entity2, ent1, ent2)
        return False

    def determine_relation_SVB(self, entity1, entity2, ent1, ent2):
        """确定主语和宾语之间的关系
        Args:
            entity1: WordUnit，原实体1
            entity2: WordUnit，原实体2
            ent1: WordUnit，处理偏正结构后的实体1
            ent2: WordUnit，处理偏正结构后的实体2
        Returns:
            *: bool，获得三元组(True)，未获得三元组(False)
        """
        relation_list = []  # 关系列表
        relation_list.append(ent2.head_word)
        entity1_list = []  # 实体1列表
        entity1_list.append(entity1)
        entity2_list = []  # 实体2列表
        entity2_list.append(entity2)

        # 实体补全(解决并列结构而增加)
        ent_1 = self.check_entity(entity1)
        ent_2 = self.check_entity(entity2)

        # example:习近平主席访问首都北京
        if ent_1 != entity1 and abs(ent_1.ID - entity1.ID) == 1:
            entity1_list.append(ent_1)
        if ent_2 != entity2 and abs(ent_2.ID - entity2.ID) == 1:
            entity2_list.append(ent_2)

        coo_flag = True  # 主谓关系中，可以处理的标志位
        # 两个动词构成并列时候，为了防止实体的动作张冠李戴，保证第二个动宾结构不能直接构成SBV-VOB的形式
        # 习近平主席视察厦门，李克强访问香港("视察"-[COO]->"访问")
        i = ent1.ID
        while i < ent2.ID-1:  # 这里减1，因为ID从1开始编号
            temp = self.sentence.words[i]  # ent1的后一个词
            # if temp(entity) <-[SBV]- AttWord -[VOB]-> 'ent2'
            if self.is_entity(temp) and temp.head == ent2.head and temp.dependency == 'SBV':
                # 代词不作为实体对待
                if temp.postag == 'r':
                    continue
                else:
                    coo_flag = False
                    break
            i += 1
        if coo_flag:
            # 针对特殊情况进行后处理
            # 如果特征关系词前面还有一个动词修饰它的话，两个词合并作为特征关系词，如"无法承认"
            temp = self.sentence.words[ent2.head-2]  # 例如："无法"
            if temp.postag == 'v' and ent2.head_word.postag == 'v' and temp.head == ent2.head:
                relation_list.insert(0, temp)
            return self.build_triple(entity1_list, entity2_list, relation_list)
        return False

    def E_NN_E(self, entity1, entity2):
        """[DSNF1]
            如果两个实体紧紧靠在一起，第一个实体是第二个实体的ATT，两个实体之间的词性为NNT(职位名称)
        Args:
            entity1: WordUnit，原实体1
            entity2: WordUnit，原实体2
        Returns:
            *: bool，获得三元组(True)，未获得三元组(False)
        """
        # print(entity1.lemma)
        # print(entity2.lemma)

        #example:美国 前任 总统 奥巴马
        if entity1.dependency == 'ATT' and entity1.head_word.dependency == 'ATT' and entity1.head_word.head == entity2.ID:
            temp = self.sentence.words[entity1.ID]  # entity1的后一个词
            # 如果temp前还有其他名词修饰器修饰
            # 美国 前任 总统 奥巴马
            # "美国" <-[ATT]- 总统    总统 <-[ATT]- 奥巴马    前任 <--- 总统
            # "前任" <---> other noun-modifier
            # entity1 <--[ATT]-- temp <--[ATT]-- entity2
            if temp.head == entity1.head and temp.dependency == 'ATT':
                if 'n' in entity1.head_word.postag:
                    relation_list = []  # 关系列表
                    relation_list.append(temp)
                    relation_list.append(entity1.head_word)
                    return self.build_triple(entity1, entity2, relation_list)
            else:
                # 美国 总统 奥巴马
                if 'n' in entity1.head_word.postag:
                    return self.build_triple(entity1, entity2, entity1.head_word)

        #example:美国 的 奥巴马 总统
        elif (entity1.dependency == 'ATT' and entity2.dependency == 'ATT'
            and entity1.head == entity2.head and abs(entity2.ID - entity1.ID) == 2):
            if 'n' in entity1.head_word.postag:
                return self.build_triple(entity1, entity2, entity1.head_word)
        return False

    def entity_de_entity_NNT(self, entity1, entity2):
        """形如"厦门大学的朱崇实校长"，实体+"的"+实体+名词
        Args:
            entity1: WordUnit，原实体1
            entity2: WordUnit，原实体2
        Returns:
            *: bool，获得三元组(True)，未获得三元组(False)
        """
        entity1_list = []
        entity1_list.append(entity1)
        entity2_list = []
        entity2_list.append(entity2)
        ok = False
        if self.sentence.words[entity1.ID].lemma == '的':
            if (entity1.head == entity2.head or entity1.head_word.head == entity2.ID 
                and 'n' in entity1.head_word.postag and entity1.ID < entity1.head):
                if entity2.postag == 'nh' and abs(entity2.ID - entity1.ID) < 4:
                    self.build_triple(entity1, entity2, entity1.head_word)
                ok = True
        return ok

