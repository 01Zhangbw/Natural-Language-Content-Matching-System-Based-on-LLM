import asyncio

import pyppeteer
from pyppeteer import launcher

# 在导入 launch 之前 把 --enable-automation 禁用 防止监测webdriver
launcher.DEFAULT_ARGS.remove("--enable-automation")
from pyppeteer import launch


# 腾讯网搜索
async def tencent_search(page, search_data, browser):
    await page.goto(f'https://new.qq.com/search?query={search_data}&page=1')
    # report_obj存搜索结果的前六条报道{链接，内容}对象
    report_obj = []
    for i in range(1, 10):
        print("当前获取到的报道数", len(report_obj))
        if len(report_obj) == 2:
            break

        try:
            await page.waitForSelector(
                f"#root > div > div.wrap > div.left-wrap.LEFT > div:nth-child(2) > ul > li:nth-child({i}) > a")
            report_url = await page.evaluate(
                f'() => {{ return document.querySelector("#root > div > div.wrap > div.left-wrap.LEFT > div:nth-child(2) > ul > li:nth-child({i}) > a").getAttribute("href"); }}'
            )

            # 检查是否包含 "baike.sogou.com"
            if "baike.sogou.com" in report_url:
                print(f"第{i}个链接包含 'baike.sogou.com'，跳过")
                continue

        except Exception as e:
            print(f"{i}获取不了")
            continue

        # report_obj.append(report_url)
        print(report_url)

        sub_page = await browser.newPage()
        await sub_page.goto(report_url, timeout=100000)

        # j表示迭代报道中的第几段
        j = 1
        max_failed_attempts = 2  # 设置最大连续失败尝试次数
        failed_attempts = 0  # 记录连续失败尝试次数

        # 当前报道的所有段文字内容
        target_text = ""
        while True:
            element_selector = f'#ArticleContent > div > div:nth-child({j})'
            try:
                print(j)
                if await sub_page.waitForSelector(element_selector, timeout=1000):
                    # 当前段文字内容
                    element_text = await sub_page.evaluate(
                        f'() => {{ return document.querySelector("{element_selector}").textContent; }}')
                    print(element_text)
                    if not element_text.startswith('\n') and not element_text.startswith(' '):
                        target_text += element_text
                    j += 1
                    failed_attempts = 0  # 重置失败尝试计数
            except pyppeteer.errors.TimeoutError:
                failed_attempts += 1
                j += 1
                if failed_attempts >= max_failed_attempts:
                    # 若获取某一段超时，则尝试获取下一段，若还是获取不到，说明已经到了最后一段。

                    # 若获取到的文本多于200字，才append进数组
                    if len(target_text) >= 200:
                        # 报道的链接url和报道的文字text封成对象append进数组
                        report_obj.append({"url": report_url, "text": target_text})
                    print(f"连续 {max_failed_attempts} 次获取超时，退出循环")
                    break

        print("目前获取到的报道字典：", report_obj)
        # 关闭子页面
        await sub_page.close()
    return report_obj


# 搜狐的搜索
async def souhu_version(page, search_data, browser):
    await page.goto(f'https://search.sohu.com/?keyword={search_data}')

    # 滚动一下，加载出下面没显示的标题
    await page.evaluateOnNewDocument('''
        (function() {
            window.addEventListener('beforeunload', function() {
                // 模拟滚动到页面底部
                window.scrollTo(0, document.body.scrollHeight);
            });
        })();
    ''')
    await asyncio.sleep(2)

    # report_obj存热榜前十的{链接，标题，内容}对象
    report_obj = []
    for i in range(1, 20):
        print("当前获取到的报道数", len(report_obj))
        if len(report_obj) == 2:
            break
        # news-list > div > div:nth-child(1) > div > div > div.cards-content-right > div > a
        url_selector = f"#news-list > div > div:nth-child({i}) > div > div > div.cards-content-right > div > a"
        try:
            await page.waitForSelector(url_selector, timeout=1000)
            print(f"第{i}篇报道")
            search_url = await page.evaluate(
                f'() => {{ return document.querySelector("{url_selector}").getAttribute("href"); }}'
            )

            print(search_url)
        except Exception as e:
            print(f"第{i}篇链接无法获取")
            continue
        sub_page = await browser.newPage()
        await sub_page.goto(search_url, timeout=100000)

        # j表示迭代报道中的第几段
        j = 1
        max_failed_attempts = 2  # 设置最大连续失败尝试次数
        failed_attempts = 0  # 记录连续失败尝试次数

        # 当前报道的所有段文字内容
        target_text = ""
        while True:
            # mp-editor > p:nth-child(2)

            element_selector = f'#mp-editor > p:nth-child({j})'
            try:
                print(j)
                if await sub_page.waitForSelector(element_selector, timeout=1000):
                    # 当前段文字内容
                    element_text = await sub_page.evaluate(
                        f'() => {{ return document.querySelector("{element_selector}").textContent; }}')
                    print(element_text)
                if not element_text.startswith('\n') and not element_text.startswith(' '):
                    target_text += element_text
                j += 1
                failed_attempts = 0  # 重置失败尝试计数
            except pyppeteer.errors.TimeoutError:
                failed_attempts += 1
                j += 1
                if failed_attempts >= max_failed_attempts:
                    # 若获取某一段超时，则尝试获取下一段，若还是获取不到，说明已经到了最后一段。

                    # 若获取到的文本多于200字，才append进数组
                    if len(target_text) >= 200:
                        # 报道的链接url和报道的文字text封成对象append进数组
                        report_obj.append({"url": search_url, "text": target_text})
                    print(f"连续 {max_failed_attempts} 次获取超时，退出循环")
                    break

        print("目前获取到的报道字典：", report_obj)
        # 关闭子页面
        await sub_page.close()

    return report_obj


async def baidu_search(page, search_data, browser):
    await page.goto("https://www.baidu.com/")
    # kw


async def entry(search_data="中国第一个宇航员"):
    # 加载浏览器
    # headless为False时会弹出浏览器调试框
    # userDataDir='../userdata'只需登录一次
    browser = await launch(headless=False, userDataDir='../userdata')
    # 打开新标签页
    page = await browser.newPage()

    # 腾讯搜索
    report_obj = await tencent_search(page, search_data, browser)

    # 搜狐搜索
    # report_obj = await souhu_version(page, search_data, browser)

    # 百度搜索
    # report_obj = await baidu_search(page, search_data, browser)

    # return report_obj
    # 给页面一些时间加载搜索结果
    await asyncio.sleep(1000)


if __name__ == '__main__':
    report = asyncio.get_event_loop().run_until_complete(entry())
    print("1111搜索结果：\n", report)
