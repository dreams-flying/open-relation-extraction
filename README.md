# open-relation-extraction
基于百度开源的依存句法分析系统[DDParser](https://github.com/baidu/DDParser)，实现面向开放域文本的三元组抽取。
# 所需环境
python>=3.6</br>
[paddlepaddle](https://www.paddlepaddle.org.cn/install/quick?docurl=/documentation/docs/zh/install/pip/windows-pip.html)>=2.0</br>
[LAC](https://github.com/baidu/lac)>=2.1
# 项目目录
├── code&emsp;&emsp;代码目录</br>
├── data&emsp;&emsp;存放数据</br>
├── img    </br>
├── resource&emsp;&emsp;默认的用户词典目录</br>
├── extract_demo.py&emsp;&emsp;程序入口
# 数据集
数据采用[维基百科语料库json版](https://storage.googleapis.com/nlp_chinese_corpus/wiki_zh_2019.zip)，从语料库中筛选了人物数据放在data下。
# 例子
```text=“孙中山为广府人，出生于清广东省广州府香山县翠亨村，祖籍广东省东莞。”```</br>
```
["孙中山", "为", "广府人"]；["孙中山", "出生于", "广州府香山县翠亨村"]
["清", "广东省", "广州府香山县"]；["广东省", "广州府香山县", "翠亨村"]
```
# DSNFs范式
![image](https://github.com/dreams-flying/open-relation-extraction/blob/master/img/DSNF.png)
# 参考文献
Jia S, Li M, Xiang Y. Chinese Open Relation Extraction and Knowledge Base Establishment[J]. ACM Transactions on Asian and Low-Resource Language Information Processing (TALLIP), 2018, 17(3): 15.

https://github.com/lemonhu/open-entity-relation-extraction
