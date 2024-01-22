import os

import pyglet
from resource.time_def import *
from resource.font_parse import Image, parse_fnt, render_text_to_image


current_path = os.path.dirname(os.path.abspath(__file__))
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
    new_image.save(os.path.join(directory_path, file_name), quality=100)
