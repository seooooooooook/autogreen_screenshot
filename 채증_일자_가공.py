# 엑셀에서 작성 일자 행에 있는 데이터를 받아 와서 가공하기
import os.path

import pandas


def extract_links(dataframe):
    return dataframe['URL'].tolist()

def load_excel(file_path):
    return pandas.read_excel(file_path, converters={"작성 일자": str})

def get_date():
    # 엑셀 파일 열기
    pd = pandas.read_excel('input.xlsx')
    # 엑셀 파일에서 작성 일자 행의 데이터를 가져오기
    date = pd['작성 일자']
    # 가져온 데이터를 리스트로 변환
    date = list(date)
    # 리스트의 데이터를 가공하기
    for i in range(len(date)):
        d = str(date[i])
        dlist = d.split('.')
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
    pd.to_excel('output1.xlsx', index=False)


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


get_date()