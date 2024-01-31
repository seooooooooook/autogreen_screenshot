# ========================================================================================================== #
# SBS 이미지 단속용 채증 요청
## https://www.notion.so/5525d92ae07d49edb25d517baa1a7895?pvs=4#465d022185174e5bbfdf861eccfa1d10
import subprocess
from io import BytesIO

from selenium.webdriver.support import expected_conditions as EC

# 엑셀의 URL들을 들어가서 전체페이지에 시계가 들어간 이미지를 캡쳐하고
# 요구사항에 맞게 엑셀에 게시 일자, 채증 일자 등등을 수집합니다.
# 지속적으로 요청이 들어오지만 사이트는 달라지는 경우도 있기 때문에 고려해서 유연하게 만들면 좋을 것 같습니다.

## 노션에 넣어둔 엑셀 3개를 보고 짜시면 도움이 될 것 같습니다 !
# ========================================================================================================== #
import pandas as pd
import time, os, pyglet

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from resource.time_def import *
from PIL import Image
from resource.font_parse import parse_fnt, render_text_to_image
from selenium import webdriver
from bs4 import BeautifulSoup

# 현재 파일 경로
current_path = os.path.dirname(os.path.abspath(__file__))

# 크롬 드라이버 설정 초기화
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' \
             'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'
header = {'User-Agent': user_agent}


def chrome_driver(headless, max_screen=False, mobile=False, script_enabled=False, tor_browser=False):
    global user_agent, driver
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless")
    if max_screen:
        options.add_argument("--start-maximized")
    if mobile:
        user_agent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'
        options.add_experimental_option("mobileEmulation", {"deviceName": "iPhone 12 Pro"})
    if script_enabled:
        options.add_experimental_option("prefs", {"profile.managed_default_content_settings.javascript": 2})
    if tor_browser:
        options.add_argument("--proxy-server=socks5://127.0.0.1:9150")
    try:
        driver = webdriver.Chrome(options=options)
    except FileNotFoundError as err:
        print(err)
    finally:
        return driver


# 엑셀 파일 로드
# file_path                   : 엑셀파일 경로
# (return)                    : pandas 라이브러리 자료형
def load_excel(file_path):
    return pd.read_excel(file_path, converters={"작성 일자": str})


# 링크 추출
# dataframe                   : URL 리스트 가져올 엑셀파일
# (return)                    : List형 URL리스트
def extract_links(dataframe):
    return dataframe['URL'].tolist()


# URL바, Window바, 시계프로그램 이미지 추출해 가져오기
# link                        : URL바에 넣을 텍스트(채증 URL)
# (return)                    : { 'urlBar': urlBar, 'utck': utck, 'windowBar': windowBar }
def get_resource(link):
    pyglet.resource.path.append(
        os.path.join(current_path, 'resource', 'font', 'black_font', 'url_font.fnt').replace('\\', '\\\\'))

    utck_time = DateHelper.utck_time()
    window_time = DateHelper.windowTime()
    # * 브라우저 바
    urlBar = Image.open(os.path.join(current_path, 'resource', 'url_bar.png'))
    modified_url = link.replace('https://', '').replace('http://', '').replace('www.', '').replace('com//', 'com/')
    modified_url = modified_url if len(modified_url) < 83 else f"{modified_url[:83]}..."
    url_fnt_path = os.path.join(current_path, 'resource', 'font', 'black_font', 'url_font.fnt')
    url_png_path = os.path.join(current_path, 'resource', 'font', 'black_font', 'url_font_0.png')
    url_char_data = parse_fnt(url_fnt_path)
    url_text_img = render_text_to_image(modified_url, url_char_data, url_png_path, 1)
    urlBar.paste(url_text_img, (265, 32), url_text_img)  # (265, 32)은 텍스트를 배치할 좌표입니다.
    # * 윈도우 바
    windowBar = Image.open(os.path.join(current_path, 'resource', 'window_bar.png'))
    window_fnt_path = os.path.join(current_path, 'resource', 'font', 'white_font', 'time_font.fnt')
    window_png_path = os.path.join(current_path, 'resource', 'font', 'white_font', 'time_font_0.png')
    window_char_data = parse_fnt(window_fnt_path)
    windowTime0_text_img = render_text_to_image(window_time[0], window_char_data, window_png_path, 2)
    windowTime1_text_img = render_text_to_image(window_time[1], window_char_data, window_png_path, 2)
    windowTime2_text_img = render_text_to_image(window_time[2], window_char_data, window_png_path, 2)
    windowBar.paste(windowTime0_text_img, (windowBar.size[0] - 148, 12), windowTime0_text_img)
    windowBar.paste(windowTime1_text_img, (windowBar.size[0] - 88, 16), windowTime1_text_img)
    windowBar.paste(windowTime2_text_img, (windowBar.size[0] - 155, 43), windowTime2_text_img)
    # * UTCK 시계
    utck = Image.open(os.path.join(current_path, 'resource', 'utck.png'))
    utck_date_fnt_path = os.path.join(current_path, 'resource', 'font', 'green_font', 'date_font.fnt')
    utck_date_png_path = os.path.join(current_path, 'resource', 'font', 'green_font', 'date_font_0.png')
    utck_time_fnt_path = os.path.join(current_path, 'resource', 'font', 'green_font', 'time_font.fnt')
    utck_time_png_path = os.path.join(current_path, 'resource', 'font', 'green_font', 'time_font_0.png')
    utck_date_char_data = parse_fnt(utck_date_fnt_path)
    utck_time_char_data = parse_fnt(utck_time_fnt_path)
    utck_date_text_img = render_text_to_image(utck_time[0], utck_date_char_data, utck_date_png_path, 3)
    utck_time_text_img = render_text_to_image(utck_time[1], utck_time_char_data, utck_time_png_path, 10)
    utck.paste(utck_date_text_img, (120, 161), utck_date_text_img)
    utck.paste(utck_time_text_img, (135, 205), utck_time_text_img)
    return {
        'urlBar': urlBar,
        'utck': utck,
        'windowBar': windowBar,
    }


# 스크린샷에 URL바, Window바, 시계프로그램 붙이기(이미지 채증)
# file_name                   : 저장할 파일 이름
# link                        : get_resourece에 넣어줄 채증 URL
# utckUp                      : 시계 프로그램 위치(True - 위에 배치, False - 아래에 배치)
# (return)                    : X(없음)
def edit_image(file_name, link, utckUp):
    resource_image = get_resource(link)
    # 스크린샷 이미지 로드
    page = Image.open(os.path.join(current_path, 'resource/screenshot.png'))
    # 리사이즈
    resource_image['urlBar'] = resource_image['urlBar'].resize(
        (page.width, int(page.width * (resource_image['urlBar'].height / resource_image['urlBar'].width))),
        Image.LANCZOS)
    resource_image['utck'] = resource_image['utck'].resize((int(page.width / 4), int(int(page.width / 4) * (
            resource_image['utck'].height / resource_image['utck'].width))), Image.LANCZOS)
    resource_image['windowBar'] = resource_image['windowBar'].resize(
        (page.width, int(page.width * (resource_image['windowBar'].height / resource_image['windowBar'].width))),
        Image.LANCZOS)
    # 새로운 이미지 생성
    new_image = Image.new("RGB", (
        page.width, page.height + resource_image['urlBar'].height + resource_image['windowBar'].height),
                          (255, 255, 255))
    # 이미지 합성
    new_image.paste(page, (0, resource_image['urlBar'].height))
    utck_y = 45 if utckUp else resource_image['urlBar'].height + page.height - resource_image['utck'].height
    new_image.paste(resource_image['utck'], (page.width - resource_image['utck'].width, utck_y), resource_image['utck'])
    new_image.paste(resource_image['urlBar'], (0, 0), resource_image['urlBar'])
    new_image.paste(resource_image['windowBar'], (0, new_image.height - resource_image['windowBar'].height),
                    resource_image['windowBar'])

    # 디렉토리 있는지 확인 후 없으면 생성
    directory_path = current_path.replace('\\', '/') + f"/{DateHelper.get_date().replace('-', '')}"
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    # 이미지 저장
    # new_image.save(os.path.join(directory_path, file_name), quality=100)
    compress_with_pngquant(new_image).save(os.path.join(directory_path, file_name), quality=100)



# 이미지 리사이즈(사이즈 크기 줄이기)
# pil_image                   : 사이즈 크기를 줄일 PIL 라이브러리로 수정한 이미지 파일
# (return)                    : resize된 이미지 파일(PIL 라이브러리 자료형)
def compress_with_pngquant(pil_image):
    buffer = BytesIO()
    pil_image.save(buffer, format="PNG")
    buffer.seek(0)

    process = subprocess.Popen(
        [os.path.join(current_path, 'pngquant', 'pngquant.exe').replace('\\', '\\\\'), '-', '--quality', '60-80'],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    stdout, _ = process.communicate(buffer.getvalue())

    return Image.open(BytesIO(stdout))


# 페이지 스크린샷
# driver                      : URL 접속할 크롬드라이버
# link                        : 스크린샷 할 페이지 URL
# (return)                    : True / False
def full_screenshot(driver, link):
    # URL 파싱
    if 'facebook.com' in link:
        link = link.replace('//www', '//m')
    elif 'naver.com' in link:
        link = link.replace('//', '//m.')
    elif 'wingbling.co.kr' in link:
        link = link.replace('//', '//m.')

    try:
        # 전체 페이지 초기화
        driver.set_window_size("900", "500")
        driver.get(link)
        time.sleep(1)

        if 'wingbling.co.kr' in link:
            driver.implicitly_wait(2)

        if 'zigzag.kr' in link:
            # '상품정보 더보기' 버튼 클릭
            try:
                WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div.css-frjp3p.ed6fn8w0'))
                )
                el = driver.find_element(By.CSS_SELECTOR, 'div.css-frjp3p.ed6fn8w0')

                driver.execute_script("arguments[0].click();", el)
            except:
                print('상품정보 더보기 버튼이 없습니다.')
                pass

        driver.implicitly_wait(3)

        doc_height = driver.execute_script("return document.documentElement.scrollHeight")
        last_doc_height = 0
        while last_doc_height != doc_height:
            driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(2)
            last_doc_height = doc_height
            doc_height = driver.execute_script("return document.documentElement.scrollHeight")

        if 'wala-land.com' in link:
            doc_height += 597
            driver.execute_script("window.scrollTo(0, 0);")
        if 'wingbling.co.kr' in link:
            try:
                el = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.LINK_TEXT, '웹페이지로 계속하기 →'))
                )
                el.click()
            except:
                print('웹페이지로 계속하기 버튼이 없습니다.')
                pass


            img_elements = WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, 'img'))
            )
            WebDriverWait(driver, 20).until(
                lambda driver: map(lambda e: e.get_attribute('complete') == 'true', img_elements)
            )
            time.sleep(7)

        driver.set_window_size("1400", doc_height + 200)

        # 이미지 파일로 저장
        output_path = current_path.replace('\\', '/')
        driver.save_screenshot(f"{output_path}/resource/screenshot.png")
        return True
    except Exception as e:
        print(e)
        print("페이지가 존재하지 않습니다.")
        return False


# 채증 정보 업데이트
# excel_row                   : 엑셀에 값 입력해줄 때 필요한 행번호
# dataframe                   : 값을 넣어줄 엑셀파일
# current                     : 파일 이름 정의를 위해 필요한 오늘 날짜
# evidence_file_firstname     : 파일 이름 정의를 위해 엑셀에서 가져올 때 필요한 열 이름
# (return)                    : dataframe(수정된 엑셀파일)
def update_evidence_info(excel_row, dataframe, current, evidence_file_firstname):
    current_date = current.strftime("%Y-%m-%d")
    current_datetime = current.strftime("%Y-%m-%d_%H%M%S")
    dataframe.at[excel_row, '채증일자'] = current_date
    dataframe.at[excel_row, '채증 파일명'] = f"{dataframe.at[excel_row, evidence_file_firstname]}_{current_datetime}"
    return dataframe


# 작성 일자 수집
# driver                      : URL 접속할 크롬드라이버
# link                        : 게시일자를 수집할 URL
# (return)                    : date(게시일자)
def crawling_date_and_title(driver, link):
    def extract_data(ds, ts):
        driver.get(link)
        driver.implicitly_wait(3)

        response = driver.page_source
        soup = BeautifulSoup(response, 'html.parser')
        date = '' if ds == "" else soup.select_one(ds)
        title = '' if ts == "" else soup.select_one(ts)

        return date, title

    if 'dailyboan' in link:
        date = "div.inner span.meta span.date"
        title = ""

        date_soup, title_soup = extract_data(ds=date, ts=title)
        print(link, date_soup.text, title_soup.text)
        return date_soup.text, title_soup.text
    elif 'frankler' in link:
        date = "div.hgroup div.post-meta span.date"
        title = ""

        date_soup, title_soup = extract_data(ds=date, ts=title)
        print(link, date_soup.text, title_soup.text)
        return date_soup.text, title_soup.text
    elif 'twitter.com' in link:
        date = "div a time"
        title = ""

        date_soup, title_soup = extract_data(ds=date, ts=title)
        print(link, date_soup.text, title_soup.text)
        return date_soup.text, title_soup.text
    elif 'www.orcite.co.kr' in link:
        date = "ul.etcArea span.txtNum"
        title = ""

        date_soup, title_soup = extract_data(ds=date, ts=title)
        print(link, date_soup.text, title_soup.text)
        return date_soup.text, title_soup.text
    elif 'facebook.com' in link:
        link = link.replace('//www', '//m')
        date = "div._4g34 div abbr"
        title = ""

        date_soup, title_soup = extract_data(ds=date, ts=title)
        print(link, date_soup.text, title_soup.text)
        return date_soup.text, title_soup.text
    elif 'blog.naver.com' in link:
        link = link.replace('//blog', '//m.blog')
        date = "p[class*='date']"
        title = "div#_floating_menu_property"

        date_soup, title_soup = extract_data(ds=date, ts=title)
        print(link, date_soup.text, title_soup.attrs['posttitle'])
        return date_soup.text, title_soup.attrs['posttitle']
    elif 'post.naver.com' in link:
        link = link.replace('//post', '//m.post')
        date = "span.post_date"
        title = "div.sect_title > h3.title"

        date_soup, title_soup = extract_data(ds=date, ts=title)
        print(link, date_soup.text, title_soup.text)
        return date_soup.text, title_soup.text
    elif 'cafe.naver.com' in link:
        link = link.replace('//cafe', '//m.cafe')
        date = "div.user_wrap span.date"
        title = ""

        date_soup, title_soup = extract_data(ds=date, ts=title)
        print(link, date_soup.text, title_soup.text)
        return date_soup.text, title_soup.text

    elif 'wingbling.co.kr' in link:
        date = "div.mst_view_top > div:nth-child(2) > span:nth-child(1)"
        title = "div.mst_view_top > div.mst_view_title"

        date_soup, title_soup = extract_data(ds=date, ts=title)
        print(link, date_soup.text.split(' ')[1], title_soup.text)
        return date_soup.text.split(' ')[1], title_soup.text
    elif 'instagram.com' in link:

        date = 'time._aaqe'
        title = "h1._ap3a"
        driver.get(link)
        dv = driver.find_element(By.CSS_SELECTOR, date).get_attribute('datetime')
        tv = driver.find_element(By.CSS_SELECTOR, title).text
        print(link, dv, tv)
        return dv, tv

    elif 'thepartof.com' in link:
        title = '#prdDetail > div > div:nth-child(2) > span > strong'

        date_soup, title_soup = extract_data(ds="", ts=title)
        title = title_soup.text

        return "", title

    elif 'zigzag.kr' in link:
        title = "div.pdp__title > h1"
        driver.get(link)
        try:
            tv = driver.find_element(By.CSS_SELECTOR, title).text
        except:
            tv = "존재하지 않는 게시물입니다."

        print(link, tv)

        return "", tv
    elif 'mi0.co.kr' in link:
        title = "div.headingArea > h2"
        date_soup, title_soup = extract_data(ds="", ts=title)
        title = title_soup.text
        print(link, title)

        return "", title
    elif 'heii.co.kr' in link:
        title = "h1.eltdf-st-title"
        date_soup, title_soup = extract_data(ds="", ts=title)
        title = title_soup.text
        print(link, title)

        return date_soup, title
    elif 'wala-land.com' in link:
        title = 'h1.content-title'
        date = 'p.date'
        date_soup, title_soup = extract_data(ds=date, ts=title)
        title = title_soup.text
        date = date_soup.text
        print(link, title, date)

        return date, title
    elif 'www.studioandparc.co.kr' in link:
        return '', ''
    elif 'jewelcounty.co.kr' in link:
        print('jewelcounty.co.kr')
        title_selector = 'div.headingArea > h2'
        date_soup, title_soup = extract_data(ds="", ts=title_selector)
        title = title_soup.text

        return '' ,title
    elif 'bluejealousy.co.kr' in link:
        print('bluejealousy.co.kr')
        title_selector = '#mk_center > form:nth-child(17) > table > tbody > tr > td > table > tbody > tr:nth-child(3) > td > table > tbody > tr > td:nth-child(2) > table > tbody > tr:nth-child(1) > td > font > b'
        date_soup, title_soup = extract_data(ds="", ts=title_selector)
        title = title_soup.text

        return '' , title

    elif 'lulusreviews.tistory.com' in link:
        title_selector = 'div.hgroup > h1'
        date_selector = 'div.post-meta > span.date'
        date_soup, title_soup = extract_data(ds=date_selector, ts=title_selector)

        return date_soup.text, title_soup.text
    elif 'brenden.tistory.com' in link:
        title_selector = 'h1.hd-heading'
        date_selector = 'abbr.timeago'
        date_soup, title_soup = extract_data(ds=date_selector, ts=title_selector)

        return date_soup.text, title_soup.text


    else:
        print("URL에 해당하는 osp가 없습니다. 채증을 종료합니다. osp 조건 추가 후 다시 시도해주세요.")
        return

    return '', ''


def date_parser(date):
    if 'T' in date:
        date = date.split('T')[0]
    if '.' in date:
        dlist = date.split('.')
        if len(dlist[1]) == 1:
            dlist[1] = '0' + dlist[1]
        if len(dlist[2]) == 1:
            dlist[2] = '0' + dlist[2]
        date = f"{dlist[0]}-{dlist[1]}-{dlist[2]}"
    return date


# 게시일자 정보 업데이트
# excel_row                   : 엑셀에 값 입력해줄 때 필요한 행번호
# date                        : 파일 이름 정의를 위해 필요한 수집된 게시일자
# dataframe                   : 값을 넣어줄 엑셀파일
# (return)                    : dataframe(수정된 엑셀파일)
def update_date_info(excel_row, date, dataframe):
    parsed_date = date_parser(date)

    dataframe.at[excel_row, '게시일자'] = parsed_date
    return dataframe


# 제목 정보 업데이트
# excel_row                   : 엑셀에 값 입력해줄 때 필요한 행번호
# title                       : 파일 이름 정의를 위해 필요한 수집된 제목
# dataframe                   : 값을 넣어줄 엑셀파일
# (return)                    : dataframe(수정된 엑셀파일)
def update_title_info(excel_row, title, dataframe):
    dataframe.at[excel_row, '게시물 제목'] = title
    return dataframe


# 메인 함수
# file_path                   : 엑셀파일 경로
# evidence_file_firstname     : 파일 이름 정의를 위해 엑셀에서 가져올 때 필요한 열 이름
# utckUp                      : 시계 프로그램 위치(True - 위에 배치, False - 아래에 배치)
def main(file_path, evidence_file_firstname, utckUp=False):
    # driver 초기화
    driver = chrome_driver(headless=True)
    # 엑셀 파일 로드
    try:
        df = load_excel(file_path)
    except Exception as e:
        print("엑셀파일 경로가 틀립니다.", e)
        return

    # 링크 추출
    links = extract_links(df)

    # 이미지 캡처 및 크롤링 로직 (여기에 해당 로직 구현) -> for문으로 돌림
    for excel_row, link in enumerate(links):

        # 현재 날짜, 시간 초기화
        current = datetime.now()
        # 게시일자 수집
        try:
            date, title = crawling_date_and_title(driver, link)
            # 게시일자 정보 업데이트
            df = update_date_info(excel_row, date, df)
            # 제목 정보 업데이트
            df = update_title_info(excel_row, title, df)
        except Exception as e:
            print("게시일자 수집 중 오류가 발생했습니다.", e)
            date = ''
            title = ''

        # 페이지 스크린샷
        scshot_res = full_screenshot(driver, link)

        # True - 페이지 스크린샷 성공 / False - 페이지 스크린샷 실패(삭제된 게시글 | 선택자 못찾음)
        if (scshot_res):
            # 파일 이름 정의
            file_name = f"{df.at[excel_row, evidence_file_firstname]}_{current.strftime('%Y-%m-%d_%H%M%S')}.png"
            # 이미지 채증
            edit_image(file_name, link, utckUp)
            # 채증 정보 업데이트
            df = update_evidence_info(excel_row, df, current, evidence_file_firstname)

    # 업데이트된 데이터프레임 저장
    df.to_excel('output.xlsx', index=False)


# 실행문
# file_path                   : 엑셀파일 경로
# evidence_file_firstname     : 파일 이름 정의를 위해 엑셀에서 가져올 때 필요한 열 이름
# utckUp                      : 시계 프로그램 위치(True - 위에 배치, False - 아래에 배치)
main('input.xlsx', 'ID', utckUp=True)

## 예시로 적어둔 로직입니다! 지우시고 따로 만들어도 됩니다. 단 (1~10)에 적어둔 요구사항 주석은 지우면 안 됩니다.
