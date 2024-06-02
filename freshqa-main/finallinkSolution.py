# 解析网页
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

# 简化链接
def simplify_displayed_link(displayed_link):
    # Simplify displayed link
    if displayed_link is None:
        return None
    return extract_source_webpage(displayed_link.split(' › ')[0])

# 获取 url_count 条链接
# question：放到搜索框里搜索的内容；url_count：要搜集的url条数
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

