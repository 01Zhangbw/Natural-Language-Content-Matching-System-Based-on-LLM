import datetime
import pytz

from serpapi import GoogleSearch
from openai import OpenAI

current_date = datetime.datetime.now(
    pytz.timezone("America/Los_Angeles")
).strftime("%B %d, %Y")

# 设置API-KEY
openai_api_key = "sk-JnWHmZFfrx9mWDahm7pJhfDoQNON5zDtm4jabuapWyp09yll"  # @param {type:"string"}
openai_client = OpenAI(
    api_key=openai_api_key,
    base_url="https://api.chatanywhere.tech/v1"
)
# serpapi_api_key = "608a172cd041ef113d8365d60d2129dfb80218fea80eb0c361f46ab4d91465b5"  # @param {type:"string"}
serpapi_api_key = "23185f210b020efac2e1cabaca3021b1f22c4c752d434508a3a15dc074f23647"  # @param {type:"string"}

# 后面的针对用户提的问题的prompt就直接拼接在这个demo_prompts后就好
demo_prompts = """
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


if __name__ == '__main__':
    url_list = exact_link_url("What year is considered Albert Einstein's annus mirabilis?", 3)
    print(url_list)
