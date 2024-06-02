
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
