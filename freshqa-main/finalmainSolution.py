import datetime
import pytz
from serpapi import GoogleSearch
from openai import OpenAI


from formatSolution import freshprompt_format
import dateutil
import datetime
import pytz
import re


# 判断是否为日期
def is_date(string, fuzzy=False):
    # Parse a string into a date and check its validity
    try:
        dateutil.parser.parse(string, fuzzy=fuzzy)
        return True
    except ValueError:
        return False

# 格式化日期

current_date = datetime.datetime.now(
    pytz.timezone("America/Los_Angeles")
).strftime("%B %d, %Y")
def format_date(d):
    # Standardize the date format for each search result
    date = dateutil.parser.parse(current_date, fuzzy=True).strftime("%b %d, %Y")
    if d is None:
        return None

    for t in ["second", "minute", "hour"]:
        if f"{t} ago" in d or f"{t}s ago" in d:
            return date

    t = "day"
    if f"{t} ago" in d or f"{t}s ago" in d:
        n_days = int(re.search("(\d+) days? ago", d).group(1))
        return (
            datetime.datetime.strptime(date, "%b %d, %Y")
            - datetime.timedelta(days=n_days)
        ).strftime("%b %d, %Y")

    try:
        return dateutil.parser.parse(d, fuzzy=True).strftime("%b %d, %Y")
    except ValueError:
        for x in d.split():
            if is_date(x):
                return dateutil.parser.parse(x, fuzzy=True).strftime("%b %d, %Y")

# 设置API-KEY
openai_api_key = "sk-JnWHmZFfrx9mWDahm7pJhfDoQNON5zDtm4jabuapWyp09yll"  # @param {type:"string"}
openai_client = OpenAI(
    api_key=openai_api_key,
    base_url="https://api.chatanywhere.tech/v1"
)
# serpapi_api_key = "608a172cd041ef113d8365d60d2129dfb80218fea80eb0c361f46ab4d91465b5"  # @param {type:"string"}
serpapi_api_key = "23185f210b020efac2e1cabaca3021b1f22c4c752d434508a3a15dc074f23647"  # @param {type:"string"}


assert (
    openai_api_key is not None and openai_api_key != ""
), "OpenAI's API key is not set"
assert (
    serpapi_api_key is not None and serpapi_api_key != ""
), "SerpApi's API key is not set"
# 调用LLM的API函数
def call_llm_api(prompt, model, temperature, max_tokens, chat_completions=True):
    """
    调用LLM（大型语言模型）的API以生成响应文本。

    参数：
    - prompt: 用户输入的提示文本
    - model: 要使用的语言模型
    - temperature: 设置生成文本的随机性（温度参数）
    - max_tokens: 设置生成文本的最大长度
    - chat_completions: 指定是否使用聊天模式，默认为True

    返回：
    - 生成的响应文本
    """

    # 参见OpenAI文档获取详细信息：https://platform.openai.com/docs/guides/gpt
    if chat_completions:
        # 调用聊天模式的API
        response = openai_client.chat.completions.create(
            model=model,  # 使用指定的模型
            temperature=temperature,  # 设置生成文本的随机性
            max_tokens=max_tokens,  # 设置生成文本的最大长度
            messages=[
                {
                    "role": "system",  # 系统角色消息，用于设置助手的行为
                    "content": (
                        "You are a helpful assistant. Answer as concisely as"
                        f" possible. Knowledge cutoff: {current_date}."  # 提供上下文和知识截断日期
                    ),
                },
                {"role": "user", "content": "What's today's date?"},  # 用户消息示例
                {
                    "role": "assistant",
                    "content": f"Today is {current_date} in Pacific Standard Time.",  # 助手响应示例
                },
                {"role": "user", "content": prompt},  # 实际用户提示消息
            ],
        )
        return response.choices[0].message.content  # 返回生成的文本内容

    else:
        # 调用完成模式的API
        response = openai_client.completions.create(
            model=model,  # 使用指定的模型
            temperature=temperature,  # 设置生成文本的随机性
            max_tokens=max_tokens,  # 设置生成文本的最大长度
            prompt=prompt,  # 实际用户提示
        )
        return response.choices[0].text  # 返回生成的文本内容

# @title Function calling for the search engine

# 调用搜索引擎
def call_search_engine(query):
    params = {
    "q": query,
    # "location": "California, United States",
    "hl": "en",
    "gl": "us",
    "google_domain": "google.com",
    "api_key": serpapi_api_key,

  }

    search = GoogleSearch(params)
    return search.get_dict()

# 后面的针对用户提的问题的prompt就直接拼接在这个demo_prompts后就好
freshprompt_demo = """
query: What year is considered Albert Einstein's annus mirabilis?

source: quora.com
date: None
title: What caused Einstein's annus mirabilis?
snippet: No. He was smarter. He was so smart that “they” are probably fundamentally incapable of understanding just how “smart” Einstein was. Around 1900, Lord Kelvin, a physicist so brilliant they named a unit after him, famously recommended that young students not study physics, because so little remained to be done. He listed, specifically, two remaining issues to be solved, after which all that remained was to do ever better measurements: the photoelectric effect and the absence of a result in the Michelson-Morley experiment. He might well have added the Ultraviolet Catastrophe. Einstein was the person who solved both those riddles (and the Ultraviolet Catastrophe in the bargain), and the answers were what 20th century physics was all about: relativity and quantum mechanics. These two are arguably the most profound breakthroughs in our understanding of the world around us in all of human history. He basically single-handedly created modern physics. And in addition to that, there is basic…
highlight: None

source: bbvaopenmind.com
date: Jun 30, 2015
title: Einstein's Miracle Year - BBVA OpenMind
snippet: Einstein's miraculous year: 1905. He published four key studies for our current conception of different aspects of reality: light, matter, ...
highlight: 1905

source: guides.loc.gov
date: Nov 06, 2019
title: Introduction - Annus Mirabilis of Albert Einstein
snippet: In 1905 Albert Einstein published four groundbreaking papers that revolutionized scientific understanding of the universe.
highlight: 1905

source: cantorsparadise.com
date: Jul 18, 2023
title: Einstein's Miraculous Year: A Summary of the 1905 Annus ...
snippet: These are the four papers that Albert Einstein published in 1905, which are considered to be the foundation of modern physics.
highlight: 1905

source: guides.loc.gov
date: Jan 26, 2024
title: The 1905 Papers - Annus Mirabilis of Albert Einstein
snippet: It is an English translation of all his writings, while the second book is where the four 1905 papers were published in the original German. For ...
highlight: 1905

question: What year is considered Albert Einstein's annus mirabilis?
answer: As of today May 27, 2024, the most up-to-date and relevant information regarding this query is as follows. 1905 is considered Albert Einstein's annus mirabilis, his miraculous year.


query: Which photographer took the most expensive photograph in the world?

source: en.wikipedia.org
date: None
title: List
snippet: 
Rank,Artist,Date
1,Man Ray,May 14, 2022
2,Edward Steichen,Nov 10, 2022
3,Andreas Gursky,November 8, 2011
4,Richard Prince,May 12, 2014
highlight: None

source: all-about-photo.com
date: Dec 22, 2019
title: Most expensive photographs ever sold | Photo Article
snippet: The most expensive photo in history as of December 2014 is $6.5 million! The work of Australian landscape photographer Peter Lik, Phantom is a ...
highlight: Australian landscape photographer Peter Lik, Phantom

source: all-about-photo.com
date: Dec 20, 2022
title: Was the most expensive photograph ever taken was sold for $22 million?
snippet: The most expensive image ever sold at auction, Le Violon d'Ingres (1924) by Man Ray, which features a nude woman's back superimposed with a violin's f-holes, sold for $12.4 million on May 14th, 2022 at Christie's New York.
highlight: None

source: barnebys.com
date: May 15, 2023
title: The 11 Most Expensive Photographers
snippet: From Vogue icon Helmut Newton to feminist art pioneer Cindy Sherman, these photographers have produced indelible images that command equally ...
highlight: Vogue icon Helmut Newton

source: artisanhd.com
date: Dec 19, 2023
title: Top 5 Most Expensive Photographs & Why We Love Them
snippet: Our Top 5 Favorite Most Expensive Photographs · Andreas Gursky: Rhein II (1999) – $4.3M · Edward Steichen: The Flatiron – $11.8M · Richard Prince: ...
	4.7store rating (134)
	‎Free 3–9 day delivery
	‎10
	day returns
highlight: Andreas Gursky: Rhein II

question: Which photographer took the most expensive photograph in the world?
answer: As of today May 27, 2024, the most up-to-date and relevant information regarding this query is as follows. The most expensive photograph in the world is "Le Violon d'Ingres". The photograph was created by Man Ray.


"""
#@title Demonstration examples




#@title Retrieving search data for demonstration examples


# demo_search_data = [call_search_engine(q) for q in demo_questions]

# 调用 freshprompt 函数

def call_freshprompt(model, question, check_premise=False, verbose=False):
    # 初始化模型参数
    temperature = 0.0  # 模型的温度参数，影响生成结果的随机性
    max_tokens = 256  # 最大生成的token数量
    chat_completions = True  # 是否使用对话完成模式

    # 根据模型类型设置不同的参数
    if model.startswith('gpt-4'):
        num_organic_results = 15  # 自然搜索结果数量
        num_related_questions = 3  # 相关问题数量
        num_questions_and_answers = 3  # 问答对数量
        num_retrieved_evidences = 15  # 检索到的证据数量
    else:
        num_organic_results = 15
        num_related_questions = 2
        num_questions_and_answers = 2
        num_retrieved_evidences = 5
    
    # 根据是否检查前提来设置后缀
    if check_premise:
        suffix = (
            "\nPlease check if the question contains a valid premise before"
            " answering.\nanswer: "
        )
    else:
        suffix = "\nanswer: "

    # 生成用户问题的提示
    freshprompt_question = freshprompt_format(
        question,  # 用户问题
        call_search_engine(question),  # 调用搜索引擎获取相关数据
        suffix,  # 后缀
        num_organic_results,  # 结果
        num_related_questions,  # 相关问题
        num_questions_and_answers,  # QA的数量
        num_retrieved_evidences,  # 检索增强证据
    )

    # 拼接示例提示和用户问题提示
    fresh_prompt = freshprompt_demo + freshprompt_question  # 将这两部分相加
    # 前一部分是示例，后一部分是要问的问题。

    # 调用大语言模型API获取答案
    answer = call_llm_api(
        fresh_prompt, model, temperature, max_tokens, chat_completions
    )
    return answer  # 返回生成的答案

def exact_link_url(question, url_count):
    search_data = call_search_engine(question)
    list = []
    for i in range(url_count):
        # print(i)
        search_result = search_data['questions_and_answers'][i]
        if "link" in search_result:
            source = search_result["link"]
            list.append(source)
            # print(i, source)
    return list


# @markdown ---
model_name = "gpt-3.5-turbo" #@param ["gpt-4-0125-preview", "gpt-4-turbo-preview", "gpt-4-1106-preview", "gpt-4", "gpt-4-0613", "gpt-4-32k", "gpt-4-32k-0613", "gpt-3.5-turbo-1106", "gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-3.5-turbo-instruct", "gpt-3.5-turbo-0613", "gpt-3.5-turbo-16k-0613", "gpt-3.5-turbo-0301"]
check_premise = True  # @param {type:"boolean"}
# @markdown ### Ask your question here!

# question = "Who is the latest artist confirmed to be performing during the 2024 Grammys telecast?"  # @param {type:"string"}
question = "中国国家主席现在是谁"
answer = call_freshprompt(model_name, question, check_premise=check_premise)

# Directly output the answer
print(answer)

