# 实训调研

## 0429-0505

### RAG

RAG是大模型输出进行优化，引用训练数据来源之外的权威知识库。RAG的定义：https://aws.amazon.com/cn/what-is/retrieval-augmented-generation/

RAG的工作原理：（引入了一个信息检索组件，利用用户输入首先从新数据源提取信息，用户查询和相关信息提供给LLM，LLM用新的知识和训练数据创建更好的响应。）

1. 创建外部数据：如文件、数据库记录、长文本或者嵌入语言模型的AI技术将数据转换为数字表示形式将其存储在向量数据库。
2. 检索相关信息：数据查询将转换为向量表示形式，并和向量数据库匹配。
3. RAG模型通过上下文添加检索到的相关数据来增强用户输入。使用提示工程技术与LLM有效沟通。
4. 更换外部数据。

幻觉是模型生成的文本不遵循原文、不符合事实。https://zhuanlan.zhihu.com/p/642648601

解决模型幻觉的方法之一是检索增强。

检索增强：https://www.zhihu.com/search?type=content&q=%E6%A3%80%E7%B4%A2%E5%A2%9E%E5%BC%BA

AIGC的检索增强技术综述：https://zhuanlan.zhihu.com/p/684879771

LLM+RAG：https://zhuanlan.zhihu.com/p/651380539

RAG的好处：https://www.zhihu.com/question/625481187/answer/3309968693

检索+提示：https://zhuanlan.zhihu.com/p/470784563

### 搜索引擎/知识图谱

向量搜索引擎：https://www.51cto.com/article/779593.html

- 图像相似性搜索
- 反向图像搜索
- 对象相似性搜索
- 稳健型OCR文档搜索
- 语义搜索
- 跨模型检索
- 探索感知相似性
- 比较模型表示
- 概念插值
- 概念空间遍历

基于知识图谱的LLM检索增强方法：https://zhuanlan.zhihu.com/p/683229102

大模型+检索增强：

1. 检索增强模型Atlas，论文题目:Few-shot Learning with Retrieval Augmented Language Models
2. **REPLUG**模型可以说是**“黑盒”式检索增强**的代表。在这种新范式下，语言模型是一个黑盒子（它的参数被冻结了，不会被更新优化），**检索组件才是可微调的部分**。
3. 通过检索Wikipedia帮助OpenQA

## 0506-0513

参考论文：

[1] FreshLLM：https://arxiv.org/pdf/2310.03214，GitHub：https://github.com/freshllms/freshqa

拆解claim：

[1] Mitigating Large Language Model Hallucinations via Autonomous Knowledge Graph-Based Retroftting（AAAI2024）：
[2] FLEEK: Factual Error Detection and Correction with Evidence Retrieved from External Knowledge（EMNLP2023）：https://aclanthology.org/2023.emnlp-demo.10.pdf
[3] FacTool: Factuality Detection in Generative AI -- A Tool Augmented Framework for Multi-Task and Multi-Domain Scenarios：https://arxiv.org/pdf/2307.13528
[4] Verify-and-Edit: A Knowledge-Enhanced Chain-of-Thought Framework（ACL2023）：https://aclanthology.org/2023.acl-long.320.pdf

## 0513-0520

研读论文并调试模型：
FreshLLM：https://arxiv.org/pdf/2310.03214，GitHub：https://github.com/freshllms/freshqa

审稿页面：https://openreview.net/forum?id=q38SZkUmUh

摘要：LLM训练一次，从来不更新，缺乏动态适应我们不断变化世界的能力。我们在回答测试当前世界知识的背景下对LLM生成的文本真实性进行详细研究。介绍FRESHQA，一种新的动态QA基准涵盖了各种各样的问题和答案类型，包括需要快速变化的世界知识的问题，以及需要揭穿的错误前提的问题。并提出FRESHPROMPT，提升了FRESHQA的LLM表现，通过将相关的和这一新的资料从搜索引擎检索增强的提示方法（如搜索引擎提示方法Press et al. 2022：https://arxiv.org/pdf/2210.03350）。

贡献：

1. 提出新的动态QA基准，叫FRESHQA，具有一组不同的问题和答案类型，包括问题的答案可能会随着时间的推移和问题的处境事实上是不正确的。
2. 在fast-changing, false-premise, multi-hop问题上struggle。我们的双评估模式捕捉到了由诸如连锁思维提示。
3. FRESHPROMPT是一种简单的上下文学习方法，与检索增强方法相比，通过有效来自搜索引擎的事实和最新信息整合到模型的提示中，提高LLM的真实性。

限制和未来工作：

![image-20240519171140090](C:\Users\Lenovo\AppData\Roaming\Typora\typora-user-images\image-20240519171140090.png)

结论：

![image-20240519171450005](C:\Users\Lenovo\AppData\Roaming\Typora\typora-user-images\image-20240519171450005.png)

## 0521-0527

freshllm的代码示例：

```
#@title Demonstration examples


demo_questions = [
    "What year is considered Albert Einstein's annus mirabilis?",
    "Which photographer took the most expensive photograph in the world?",
    "How many days are left until the 2023 Grammy Awards?",
    "How many years ago did the Boxing Day Tsunami happen?",
    (
        "When did Amazon become the first publicly traded company to exceed a"
        " market value of $3 trillion?"
    ),
]

concise_demo_reasonings_and_answers = [
    (
        "1905 is considered Albert Einstein's annus mirabilis, his miraculous"
        " year."
    ),
    (
        'The most expensive photograph in the world is "Le Violon d\'Ingres".'
        " The photograph was created by Man Ray."
    ),
    (
        "The 2023 Grammy Awards ceremony was held on February 5, 2023. Thus,"
        " the ceremony has already taken place."
    ),
    (
        "The disaster occurred on December 26, 2004. Thus, it happened 19 years"
        " ago."
    ),
    "Amazon's market capitalization has never exceeded $3 trillion.",
]

verbose_demo_reasonings_and_answers = [
    (
        "In the year of 1905, Albert Einstein published four groundbreaking"
        " papers that revolutionized scientific understanding of the universe."
        " Thus, scientists call 1905 Albert Einstein's annus mirabilis — his"
        " year of miracles."
    ),
    (
        "Man Ray's famed \"Le Violon d'Ingres\" became the most expensive"
        " photograph ever to sell at auction, sold for $12.4 million on May"
        " 14th, 2022 at Christie's New York. The black and white image, taken"
        " in 1924 by the American surrealist artist, transforms a woman's naked"
        " body into a violin by overlaying the picture of her back with"
        " f-holes. Thus, Man Ray is the photographer who took the most"
        " expensive photograph in the world."
    ),
    (
        "The 2023 Grammy Awards, officially known as the 65th Annual Grammy"
        " Awards ceremony, was held in Los Angeles on February 5, 2023. Thus,"
        " the event has already taken place."
    ),
    (
        "The Boxing Day Tsunami refers to the 2004 Indian Ocean earthquake and"
        " tsunami, which is one of the deadliest natural disasters in recorded"
        " history, killing an estimated 230,000 people across 14 countries. The"
        " disaster occurred on December 26, 2004, which is 19 years ago."
    ),
    (
        "Amazon's market capitalization hit a peak of roughly $1.9 trillion in"
        " July 2021. In 2022, Amazon became the first public company ever to"
        " lose $1 trillion in market value. Thus, Amazon's market value has"
        " never exceeded $3 trillion. In fact, Apple became the first publicly"
        " traded U.S. company to exceed a market value of $3 trillion in"
        " January 2022."
    ),
]

prefix = (
    f"\nanswer: As of today {current_date}, the most up-to-date and relevant"
    " information regarding this query is as follows. "
)

concise_demo_reasonings_and_answers = [
    prefix + x for x in concise_demo_reasonings_and_answers
]
verbose_demo_reasonings_and_answers = [
    prefix + x for x in verbose_demo_reasonings_and_answers
]


```

freshprompt的结果：（能够进行跑通）
![image-20240526150910823](C:\Users\Lenovo\AppData\Roaming\Typora\typora-user-images\image-20240526150910823.png)



fresheval-strict：

由于必须有google-colab包，但是这个包总是安装失败。

因此可以删除colab相关的内容，将CSV数据集下载到本地进行运行。最后可以跑通strict-eval函数。



「RELAXED」模式只衡量主要答案是否正确，「STRICT」模式则衡量回答中的所有说法是否都是最新的事实（即没有幻觉）。两者的区别主要在于prompt的不同。



