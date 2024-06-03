import os
import re
import time
import datetime
import pytz
import dateutil
import requests
import json
import csv

import pandas as pd

# from google.colab import files
import ipywidgets as widgets
from IPython.display import display

from openai import OpenAI
import tabulate
import textwrap

from serpapi import GoogleSearch

current_date = datetime.datetime.now(
        pytz.timezone("America/Los_Angeles")
    ).strftime("%B %d, %Y")
#@title API keys


# OpenAI's API key (sign up at https://platform.openai.com/signup to get $5 in
# free credit that can be used during your first 3 months)

# 设置API-KEY
openai_api_key = "sk-JnWHmZFfrx9mWDahm7pJhfDoQNON5zDtm4jabuapWyp09yll"  # @param {type:"string"}
openai_client = OpenAI(
    api_key=openai_api_key,
    base_url="https://api.chatanywhere.tech/v1"
)

# SerpApi's API key (sign up at https://serpapi.com/users/sign_up?plan=free for
# a free plan with 100 searches/month)
serpapi_api_key = "608a172cd041ef113d8365d60d2129dfb80218fea80eb0c361f46ab4d91465b5"  # @param {type:"string"}

assert (
    openai_api_key is not None and openai_api_key != ""
), "OpenAI's API key is not set"
assert (
    serpapi_api_key is not None and serpapi_api_key != ""
), "SerpApi's API key is not set"

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


# 判断是否为日期
def is_date(string, fuzzy=False):
    # Parse a string into a date and check its validity
    try:
        dateutil.parser.parse(string, fuzzy=fuzzy)
        return True
    except ValueError:
        return False

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

def extract_source_webpage(link):
    # Extract source webpage
    return (
        link.strip()
        .replace("https://www.", "")
        .replace("http://www.", "")
        .replace("https://", "")
        .replace("http://", "")
        .split("/")[0]
    )

def simplify_displayed_link(displayed_link):
    # Simplify displayed link
    if displayed_link is None:
        return None
    return extract_source_webpage(displayed_link.split(' › ')[0])

# 格式化搜索结果
def format_search_results(search_data, title_field=None, highlight_field=None):
    # Standardize search results as shown in Figure 3 (left) in the paper
    '''
    参数：
    - search_data: 包含搜索结果数据的字典
    - title_field: 可选，指定用于标题的字段
    - highlight_field: 可选，指定用于高亮显示的字段

    返回：
    - 一个包含格式化后的搜索结果的字典
    '''
    # 标准化字段"snippet_highlighted_words"
    field = 'snippet_highlighted_words'
    if field in search_data and isinstance(search_data[field], list):
        search_data[field] = ' | '.join(search_data[field])
    # 标准化字段"displayed_link"
    field = 'displayed_link'
    if field in search_data:
        search_data[field] = simplify_displayed_link(search_data[field])

    # edge case 1：处理特定类型"local_time"的边缘情况
    if search_data.get('type') == 'local_time':
        source = search_data.get('displayed_link')
        date = format_date(search_data.get('date'))
        title = search_data.get('title')

        snippet = search_data.get('snippet')
        if snippet is None and 'result' in search_data:
            if 'extensions' in search_data and isinstance(
                search_data['extensions'], list
            ):
                snippet = '\n\t'.join(
                    [search_data['result']] + search_data['extensions']
                )
            else:
                snippet = search_data['result']

        highlight = search_data.get('snippet_highlighted_words')
        if highlight is None and 'result' in search_data:
            highlight = search_data['result']

    # edge case 2：处理特定类型"population_result"的边缘情况
    elif 'type' in search_data and search_data['type'] == 'population_result':
        source = search_data.get('displayed_link')
        if source is None and 'sources' in search_data:
            if (
                isinstance(search_data['sources'], list)
                and 'link' in search_data['sources'][0]
            ):
                source = extract_source_webpage(search_data['sources'][0]['link'])

        date = format_date(search_data.get('date'))
        if date is None and 'year' in search_data:
            date = format_date(search_data['year'])

        title = search_data.get('title')

        snippet = search_data.get('snippet')
        if snippet is None and 'population' in search_data:
            if 'place' in search_data:
                snippet = '\n\t'.join(
                    [
                        f"{search_data['place']} / Population",
                    ]
                    + [
                        search_data['population'],
                    ]
                )
            else:
                snippet = search_data['population']

        highlight = search_data.get('snippet_highlighted_words')
        if highlight is None and 'population' in search_data:
            highlight = search_data['population']

    # 处理其他类型的情况
    else:
        source = search_data.get('displayed_link')
        date = format_date(search_data.get('date'))
        title = (
            search_data.get('title')
            if title_field is None
            else search_data.get(title_field)
        )
        highlight = (
            search_data.get('snippet_highlighted_words')
            if highlight_field is None
            else search_data.get(highlight_field)
        )
        snippet = search_data.get('snippet', '')
        # 处理'rich_snippet'字段
        if 'rich_snippet' in search_data:
            for key in ['top', 'bottom']:
                if (
                    key in search_data['rich_snippet']
                    and 'extensions' in search_data['rich_snippet'][key]
                ):
                    snippet = '\n\t'.join(
                        [snippet] + search_data['rich_snippet'][key]['extensions']
                    )
        # 处理"list"字段
        if 'list' in search_data:
            assert isinstance(search_data['list'], list)
            snippet = '\n\t'.join([snippet] + search_data['list'])
        # 处理"contents"字段中的table
        if 'contents' in search_data and 'table' in search_data['contents']:
            tbl = search_data['contents']['table']
            assert isinstance(tbl, list)
            snippet += '\n'
            for row in tbl:
                snippet += f'\n{",".join(row)}'
        # 如果snippet是空白字符串，将其设置为None
        if snippet is not None and snippet.strip() == '':
            snippet = None
    # 返回成固定的格式
    return {
        'source': source,
        'date': date,
        'title': title,
        'snippet': snippet,
        'highlight': highlight,
    }

# 格式化知识图谱
def format_knowledge_graph(search_data):
    # Standardize knowledge graphs as shown in Figure 3 (left) in the paper
    source = None
    if "source" in search_data and "link" in search_data["source"]:
        source = extract_source_webpage(search_data["source"]["link"])

    date = None

    title = None
    if "title" in search_data:
        title = search_data["title"]
        if "type" in search_data:
            title += f"\n\t{search_data['type']}"

    snippet = ""
    for field in search_data:
        if (
            (field not in ["title", "type", "kgmid"])
            and ("_link" not in field)
            and ("_stick" not in field)
            and isinstance(search_data[field], str)
            and not search_data[field].startswith("http")
        ):
            snippet += f"\n\t{field}: {search_data[field]}"

    if snippet.strip() == "":
        snippet = None
    else:
        snippet = snippet.strip()

    highlight = None

    return {
        "source": source,
        "date": date,
        "title": title,
        "snippet": snippet,
        "highlight": highlight,
    }


# 格式化 Q and A
def format_questions_and_answers(search_data):
    # Standardize questions and answers as shown in Figure 3 (left) in the paper
    source = None
    if "link" in search_data:
        source = extract_source_webpage(search_data["link"])

    date = None

    title = None
    if "question" in search_data:
        title = search_data["question"]

    snippet = None
    if "answer" in search_data:
        snippet = search_data["answer"]

    highlight = None

    return {
        "source": source,
        "date": date,
        "title": title,
        "snippet": snippet,
        "highlight": highlight,
    }

# 对freshprompt进行格式化
def freshprompt_format(
    question,
    search_data,
    reasoning_and_answer,
    num_organic_results,
    num_related_questions,
    num_questions_and_answers,
    num_retrieved_evidences,
):
    """Build FreshPrompt for each question

    Args:
        question: The question to process.
        search_data: Search data.
        reasoning_and_answer: The reasoning and answer.
        num_organic_results: Number of organic results to keep.
        num_related_questions: Number of related questions to keep.
        num_questions_and_answers: Number of questions and answers to keep.
        num_retrieved_evidences: Number of retrieved evidences to keep.

    Returns:
        A prompt that incorporates retrieved evidences for each question.
    """

    df = pd.DataFrame(columns=['source', 'date', 'title', 'snippet', 'highlight'])

    # Organic results
    organic_results = [None] * num_organic_results
    for k in range(num_organic_results):
        if (
            'organic_results' in search_data
            and len(search_data['organic_results']) > k
        ):
            organic_results[k] = format_search_results(
                search_data['organic_results'][k]
            )
        else:
            organic_results[k] = format_search_results({})

    for d in organic_results[::-1]:
        df = pd.concat([df, pd.DataFrame([d])], ignore_index=True)

    # Related questions
    related_questions = [None] * num_related_questions
    for k in range(num_related_questions):
        if (
            'related_questions' in search_data
            and len(search_data['related_questions']) > k
        ):
            related_questions[k] = format_search_results(
                search_data['related_questions'][k], title_field='question'
            )
        else:
            related_questions[k] = format_search_results({})

    for d in related_questions[::-1]:
        df = pd.concat([df, pd.DataFrame([d])], ignore_index=True)

    # Questions and Answers
    questions_and_answers = [None] * num_questions_and_answers
    for k in range(num_questions_and_answers):
        if (
            'questions_and_answers' in search_data
            and len(search_data['questions_and_answers']) > k
        ):
            questions_and_answers[k] = format_questions_and_answers(
                search_data['questions_and_answers'][k]
            )
        else:
            questions_and_answers[k] = format_questions_and_answers({})

    for d in questions_and_answers[::-1]:
        df = pd.concat([df, pd.DataFrame([d])], ignore_index=True)

    # Knowledge graph
    knowledge_graph = None
    if 'knowledge_graph' in search_data:
        knowledge_graph = format_knowledge_graph(search_data['knowledge_graph'])
    else:
        knowledge_graph = format_knowledge_graph({})
    df = pd.concat([df, pd.DataFrame([knowledge_graph])], ignore_index=True)

    # Answer box
    answer_box = None
    if 'answer_box' in search_data:
        answer_box = format_search_results(
            search_data['answer_box'], highlight_field='answer'
        )
    else:
        answer_box = format_search_results({})
    df = pd.concat([df, pd.DataFrame([answer_box])], ignore_index=True)

    # Sort by date
    df['date'] = df['date'].apply(lambda x: format_date(x))
    df['datetime'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.sort_values(by='datetime', na_position='first')
    df.replace({pd.NaT: None}, inplace=True)
    df = df.dropna(how='all')

    # Select top_k supporting evidences overall
    evidences = []

    for _, row in df.tail(num_retrieved_evidences).iterrows():
        evidences.append(
            f"""\n\nsource: {row['source']}\ndate: {row['date']}\ntitle: {row['title']}\nsnippet: {row['snippet']}\nhighlight: {row['highlight']}"""
        )

    return (
        ''.join(
            [
                f'\n\n\nquery: {question}',
            ]
            + evidences
        )
        + f'\n\nquestion: {question}{reasoning_and_answer}'
    )

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
question = "英国首相是哪位？"
answer = call_freshprompt(model_name, question, check_premise=check_premise)

# Directly output the answer
print(answer)

