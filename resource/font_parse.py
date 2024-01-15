import os
from PIL import Image

current_path = os.path.dirname(os.path.abspath(__file__))


# 폰트 .fnt 파일을 텍스트 데이터로 변환
def parse_fnt(fnt_path):
    char_data = {}
    with open(fnt_path, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            if line.startswith("char "):
                parts = line.split()
                char_id = int(parts[1].split("=")[1])
                x = int(parts[2].split("=")[1])
                y = int(parts[3].split("=")[1])
                width = int(parts[4].split("=")[1])
                height = int(parts[5].split("=")[1])
                char_data[char_id] = (x, y, width, height)
    return char_data


# .png 이미지와 .fnt 대조해서 원하는 텍스트로 이미지를 만들어주는 함수
def render_text_to_image(text, char_data, png_path, spacing=0):     # spacing 매개변수 추가
    atlas = Image.open(png_path)
    new_img_width = sum([char_data[ord(c)][2] if c != ' ' else 20 for c in text]) + spacing * (len(text) - 1)   # 총 이미지 너비에 자간 추가
    new_img_height = max([char_data[ord(c)][3] for c in text if c != ' '])
    new_img = Image.new('RGBA', (new_img_width, new_img_height+20))

    x_offset = 0
    for c in text:
        if c == ' ':  # 공백 문자의 처리
            x_offset += 20
            continue

        x, y, width, height = char_data[ord(c)]
        glyph = atlas.crop((x, y, x + width, y + height))

        # 아래로 정렬을 위한 y 좌표 계산
        y_offset = new_img_height - height
        if c in ['g', 'q', 'p', 'y', 'j']:
            y_offset += 6  # 원하는 값만큼 조정
        if c in ['-']:
            y_offset -= 6
        if c in ['오']:
            y_offset -= 3
        if c in [':']:
            y_offset -= 2
        
        new_img.paste(glyph, (x_offset, y_offset))
        x_offset += width + spacing     # 자간 값을 여기에 더합니다

    return new_img