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


def update_date_info(excel_row, date, dataframe):
    parsed_date = date_parser(date)
    dataframe.at[excel_row, '작성 일자'] = parsed_date


def update_title_info(excel_row, title, dataframe):
    dataframe.at[excel_row, '제목'] = title


def update_evidence_info(excel_row, dataframe, current, evidence_file_firstname):
    current_date = current.strftime("%Y-%m-%d")
    current_datetime = current.strftime("%Y-%m-%d_%H%M%S")
    dataframe.at[excel_row, '채증 일자'] = current_date
    dataframe.at[excel_row, '채증 파일'] = f"{dataframe.at[excel_row, evidence_file_firstname]}_{current_datetime}"
