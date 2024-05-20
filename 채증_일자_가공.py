# 엑셀에서 작성 일자 행에 있는 데이터를 받아 와서 가공하기
import os.path

import pandas


def extract_links(dataframe):
    return dataframe['URL'].tolist()

def load_excel(file_path):
    return pandas.read_excel(file_path, converters={"작성 일자": str})

def get_date():
    # 엑셀 파일 열기
    pd = pandas.read_excel('20240422.xlsx')
    # 엑셀 파일에서 작성 일자 행의 데이터를 가져오기
    date = pd['작성 일자']
    # 가져온 데이터를 리스트로 변환
    date = list(date)
    # 리스트의 데이터를 가공하기
    for i in range(len(date)):
        d = str(date[i])
        dlist = d.split('.')
        # 2024-04-0516:01:53 뒤에 붙은 시간 제거
        if date[i] == 'nan':
            print('데이터 없음')
            # 해당 셀에 데이터가 없으면 빈 값으로 대치
            date[i] = ''
            continue
        if 'T' in str(date[i]):
            print("가공 전 : ",date[i])
            date[i] = str(date[i]).split('T')[0]
        if len(dlist) >= 3:
            print("가공 전 : ",d)
            if len(dlist[1]) == 1:
                dlist[1] = '0' + dlist[1]
            if len(dlist[2]) == 1:
                dlist[2] = '0' + dlist[2]
            date[i] = f"{dlist[0]}-{dlist[1]}-{dlist[2]}"



        date[i] = str(date[i]).replace(' ', '')
        print("처리 완료 ::::" ,date[i])

    # 가공한 데이터를 엑셀 파일에 저장하기
    pd['작성 일자'] = date
    pd.to_excel('output.xlsx', index=False)

def parse_date():
    # 엑셀 파일 열기
    pd = pandas.read_excel('output.xlsx')
    # 엑셀 파일에서 작성 일자 행의 데이터를 가져오기
    datelist = pd['작성 일자'].tolist()
    for excel_row, date in enumerate(datelist):
        # "2024-04-0516:01:53" 뒤에 붙은 시간 제거
        print("가공 전 : ",date)
        if len(str(date)) == 18:
            date = date[:10]
            # 해당 셀에 변경 데이터 적용
            datelist[excel_row] = date
            print("가공 후 : ",date)
    # 가공한 리스트를 엑셀 파일에 저장하기
    pd['작성 일자'] = datelist
    
    pd.to_excel('output2.xlsx', index=False)


def delete_img():
    try:
        df = load_excel('updated_file4.xlsx')
    except Exception as e:
        print("엑셀파일 경로가 틀립니다.", e)
        return

    links = extract_links(df)

    for excel_row, link in enumerate(links):
        if 'mi0.co.kr' not in link and 'studioandparc.co.kr' not in link:
            continue

        # 파일 이름
        file_name = df.iloc[excel_row]['채증 파일']
        path = f"/20240111/{file_name}.png"
        delete_evidence_inf(path)


def delete_evidence_inf(file_path: str):

    if os.path.exists(f"/Users/union/Downloads/etc-request/autogreen{file_path}"):
        os.remove(f"/Users/union/Downloads/etc-request/autogreen{file_path}")
        print(f"{file_path} 파일이 삭제되었습니다.")

    else:
        print(f"{file_path} 파일이 존재하지 않습니다.")

def update_fname(file_path):
    try:
        df = load_excel(file_path)
    except Exception as e:
        print("엑셀파일 경로가 틀립니다.", e)
        return
    
    브랜드기업 = df['브랜드/기업'].tolist()

    for excel_row, bname in enumerate(브랜드기업):
        if pandas.isnull(df.at[excel_row, '채증 파일']) :
            continue
        file_name = df.at[excel_row, '채증 파일']
        print(file_name)
        file_name = file_name.replace('쿠팡', '')
        df.at[excel_row, '채증 파일']= f'{bname}{file_name}'
        print(f'{bname}{file_name}')

    df.to_excel('output0321_res.xlsx', index=False)


parse_date()