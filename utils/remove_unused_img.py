import pandas as pd
import os

def main(file_name: str):
    # Read the Excel file
    df = pd.read_excel(file_name)

    dir = "./20240503"
    file_list = os.listdir(dir)
    # Remove files that are not in the Excel list
    for file_name in file_list:
        if file_name not in df['채증 파일'].values:
            file_path = os.path.join(dir, file_name)
            os.remove(file_path)

main('C:/autogreen_screenshot/이미지 저작권 침해_채증_240503.xlsx')