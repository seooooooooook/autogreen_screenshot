import datetime
import os

import pandas as pd
import pyppeteer

from processing_image import edit_image
from processing_excel import update_evidence_info, update_title_info, update_date_info
from src.osp import get_data_osp, NoSuchOSPException


def load_excel(file_path):
    dtype = {
        "브랜드": str,
        "구분": str,
        "제목": str,
        "URL": str,
        "작성 일자": str,
        "채증 일자": str,
        "채증 파일": str,
    }

    return pd.read_excel(file_path, dtype=dtype)


async def save_screen_shot(page, url, need_scroll: bool = False) -> bool:
    try:
        await page.goto(url, {"waitUntil": 'load'})
        await asyncio.sleep(3)

        if 'zigzag.kr' in url:
            await page.waitForSelector('div.css-frjp3p.ed6fn8w0')
            await page.querySelectorEval('div.css-frjp3p.ed6fn8w0', 'e => e.click()')

        if 'zigzag.kr' in url or 'mi0.co.kr' in url:
            await page.setJavaScriptEnabled(enabled=False)

        need_scroll = True
        await page.setJavaScriptEnabled(enabled=False)
        if need_scroll:
            doc_height = await page.evaluate('() => document.body.scrollHeight')
            last_doc_height = 0
            while last_doc_height != doc_height:
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await asyncio.sleep(1)
                last_doc_height = doc_height
                doc_height = await page.evaluate('() => document.body.scrollHeight')

        if 'wala-land.com' in url:
            await page.evaluate('window.scrollTo(0, 0)')
            await asyncio.sleep(1)

        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resource/screenshot.png')
        await page.screenshot({'path': output_path, 'fullPage': True})

        await page.setJavaScriptEnabled(enabled=True)
        return True
    except Exception as e:
        print("save screenshot exception : ", e)
        return False


async def main(file_path, evidence_file_firstname='브랜드', utckUp=True):
    browser = await pyppeteer.launch(
        headless=False,
        executablePath="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        args=[
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-features=nw2" "--disable-gpu",
            "--disable-dev-shm-usage",
            '--proxy-server="direct://"',
            "--proxy-bypass-list=*",
            "--disable-extensions",
        ],
    )

    try:
        df = load_excel(file_path)
    except Exception as e:
        print("load excel error : ", e)
        return

    links: list[str] = df['URL'].tolist()

    page = await browser.newPage()

    for row, link in enumerate(links):
        current = datetime.datetime.now()
        try:
            date, title = await get_data_osp(page, link)
        except NoSuchOSPException as e:
            print(f"{link} 에 대한 osp가 존재하지 않습니다.")
            continue
        except Exception as e:
            print("get data osp error : ", e)
            continue

        print(f"{row + 1}/{len(links)} : {link} ::{current}:: title={title} date={date}")

        update_title_info(row, title, df)
        update_date_info(row, date, df)

        disable_javascript_list = ['wala-land.com', 'mi0.co.kr']
        need_scroll_list = ['blog.naver.com', 'zigzag.kr', 'mi0.co.kr']

        disable_javascript = True if (ns in link for ns in disable_javascript_list) else False
        need_scroll = True if (ns in link for ns in need_scroll_list) else False
        # 잘리는 페이지
        # mi0.co.kr
        scrshot_res: bool = await save_screen_shot(page, url=link, need_scroll=need_scroll)

        if scrshot_res:
            file_name = f"{df.at[row, evidence_file_firstname]}_{current.strftime('%Y-%m-%d_%H%M%S')}.png"
            edit_image(file_name, link, utckUp)
            update_evidence_info(row, df, current, evidence_file_firstname)

        df.to_excel("output.xlsx", index=False)


if __name__ == "__main__":
    import asyncio

    asyncio.get_event_loop().run_until_complete(main('input.xlsx'))
