

import pandas as pd
import time, os, pyglet
import subprocess
from io import BytesIO
from resource.font_parse import parse_fnt, render_text_to_image
from resource.time_def import *
from PIL import Image

# 현재 파일 경로
current_path = os.path.dirname(os.path.abspath(__file__))

def load_excel(file_path):
    return pd.read_excel(file_path)


# 링크 추출
# dataframe                   : URL 리스트 가져올 엑셀파일
# (return)                    : List형 URL리스트
def extract_links(dataframe):
    return dataframe['URL'].tolist()

def update_evidence_info(excel_row, dataframe, current, evidence_file_firstname):
    current_date = current.strftime("%Y-%m-%d")
    # current_datetime = current.strftime("%Y-%m-%d_%H%M%S")
    dataframe.at[excel_row, '채증 일자'] = current_date
    # dataframe.at[excel_row, '채증 파일'] = f"{evidence_file_firstname}_{current_datetime}"
    dataframe.at[excel_row, '채증 파일'] = evidence_file_firstname
    return dataframe
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

def edit_image(file_name, link, utckUp, file_path=None):
    resource_image = get_resource(link)
    # 스크린샷 이미지 로드
    page = Image.open(os.path.join(current_path, file_path))
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


def main(file_path, evidence_file_firstname, utckUp=False):
    print("채증 시작")
    # 엑셀 파일 로드
    df = None
    try:
        df = load_excel(file_path)
    except Exception as e:
        print("엑셀파일 경로가 틀립니다.", e)
        return
    links = extract_links(df)
    for excel_row, link in enumerate(links):
        print(excel_row)
        for file in os.listdir('./resource/screenshots'):
            if not file.startswith(str(df.at[excel_row, '채증 파일'])):
                continue

            time.sleep(1)

            file_path = os.path.join('resource/screenshots', file)

            current = datetime.now()
            file_name = f"{df.at[excel_row, evidence_file_firstname]}_{current.strftime('%Y-%m-%d_%H%M%S')}.png"
            # 이미지 채증
            edit_image(file_name, link, utckUp, file_path)
            # 채증 정보 업데이트
            # df = update_evidence_info(excel_row, df, current, df.at[excel_row, '브랜드'])
            df = update_evidence_info(excel_row, df, current, evidence_file_firstname=file_name)

    # 엑셀 파일 저장
    df.to_excel('20240514.xlsx', index=False)
# 실행문
# file_path                   : 엑셀파일 경로
# evidence_file_firstname     : 파일 이름 정의를 위해 엑셀에서 가져올 때 필요한 열 이름
# utckUp                      : 시계 프로그램 위치(True - 위에 배치, False - 아래에 배치)
main('빌리프랩_댓글 수집.xlsx', '출처', utckUp=True)