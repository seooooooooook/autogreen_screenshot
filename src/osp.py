import pyppeteer.page
from bs4 import BeautifulSoup


def get_soup(html, selector):
    soup = BeautifulSoup(html, 'html.parser')
    return soup.select_one(selector)



class NoSuchOSPException(Exception):
    def __init__(self, message):
        self.message = message

async def get_data_osp(page: pyppeteer.page.Page, link: str):
    if 'wingbling.co.kr' in link:
        await page.goto(link, {"waitUntil": 'load'})
        date_selector = "div.mst_view_top > div:nth-child(2) > span:nth-child(1)"
        title_selector = "div.mst_view_top > div.mst_view_title"
        html = await page.content()

        return get_soup(html, date_selector).text.strip().split('.')[1], get_soup(html, title_selector).text
    elif 'instagram.com' in link:
        await page.goto(link, {"waitUntil": 'load'})
        date_selector = 'time._aaqe'
        title_selector = "h1._ap3a"
        await page.waitForSelector(date_selector)
        await page.waitForSelector(title_selector)
        date = await page.querySelectorEval(date_selector, 'el => el.getAttribute("datetime")')
        title = await page.querySelectorEval(title_selector, 'el => el.textContent')

        return date.split('T')[0], title
    elif 'thepartof.com' in link:
        await page.goto(link, {"waitUntil": 'load'})
        title_selector = '#prdDetail > div > div:nth-child(2) > span > strong'
        html = await page.content()

        return "", get_soup(html, title_selector).text

    elif 'blog.naver.com' in link:
        link = link.replace('//blog', '//m.blog')
        await page.goto(link, {"waitUntil": 'load'})
        date_selector = "p[class*='date']"
        title_selector = "div#_floating_menu_property"
        html = await page.content()

        return get_soup(html, date_selector).text.strip(), get_soup(html, title_selector).attrs['posttitle']
    elif 'post.naver.com' in link:
        # 스샷 짤림
        link = link.replace('//post', '//m.post')
        await page.goto(link, {"waitUntil": 'load'})
        date_selector = "span.post_date"
        title_selector = "div.sect_title > h3.title"
        html = await page.content()

        return get_soup(html, date_selector).text.strip(), get_soup(html, title_selector).text
    elif 'cafe.naver.com' in link:
        link = link.replace('//cafe', '//m.cafe')
        await page.goto(link, {"waitUntil": 'load'})
        date_selector = "div.user_wrap span.date"
        html = await page.content()

        return get_soup(html, date_selector).text.strip(), ''
    elif 'zigzag.kr' in link:
        await page.goto(link, {"waitUntil": 'load'})
        title_selector = "div.pdp__title > h1"
        try:
            title = await page.querySelectorEval(title_selector, 'el => el.textContent')
        except:
            title = '존재하지 않는 게시물입니다f.'

        return '', title
    elif 'mi0.co.kr' in link:
        await page.goto(link, {"waitUntil": 'load'})
        title_selector = "div.headingArea > h2"
        html = await page.content()

        return '', get_soup(html, title_selector).text.strip()
    elif 'heii.co.kr' in link:
        await page.goto(link, {"waitUntil": 'load'})
        title_selector = "h1.eltdf-st-title"
        html = await page.content()

        return '', get_soup(html, title_selector).text.strip()
    elif 'wala-land.com' in link:
        await page.goto(link, {"waitUntil": 'load'})
        title_selector = 'h1.content-title'
        date_selector = 'p.date'
        html = await page.content()

        return get_soup(html ,date_selector).text, get_soup(html, title_selector).text.strip()
    elif 'studioandparc.co.kr' in link:
        return '', ''
    elif 'jewelcounty.co.kr' in link:
        await page.goto(link, {"waitUntil": 'load'})
        title_selector = 'div.headingArea > h2'
        html = await page.content()

        return '' , get_soup(html, title_selector).text
    elif 'bluejealousy.co.kr' in link:
        await page.goto(link, {"waitUntil": 'load'})
        title_selector = '#mk_center > form:nth-child(17) > table > tbody > tr > td > table > tbody > tr:nth-child(3) > td > table > tbody > tr > td:nth-child(2) > table > tbody > tr:nth-child(1) > td > font > b'
        html = await page.content()

        return '' , get_soup(html, title_selector).text.strip()
    else:
        raise NoSuchOSPException("지원하지 않는 사이트 입니다.")