from datetime import datetime, timedelta
import string, random

class DateHelper:
    @staticmethod
    def now():
        today = datetime.now()              # 현재 국제시간(utc)으로 측정하고 있어서 우리나라 시간이 나오지 않음
        timezone_offset = today.utcoffset().seconds / 3600 if today.utcoffset() else 0
        today -= timedelta(hours=timezone_offset)
        return today

    @staticmethod
    def utck_time():
        today = DateHelper.now()
        # 년, 월, 일, 요일 정보를 포맷팅 (Node.js와 동일하게)
        days = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
        month_name = ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월']
        parsed_date = f"{today.year}년 {month_name[today.month-1]} {today.day}일 {days[today.weekday()]}"
        parsed_time = today.strftime('%H:%M:%S')
        return (parsed_date, parsed_time)

    @staticmethod
    def windowTime():
        today = DateHelper.now()
        parsed_date = today.strftime('%Y-%m-%d')
        # 시간 파싱 (오전/오후 구분)
        hours = int(today.strftime('%H'))
        minutes = today.strftime('%M')
        if hours < 12:
            parsed_hour = f"오전 {hours if hours != 0 else 12}:{minutes}"
        else:
            parsed_hour = f"오후 {hours-12 if hours != 12 else 12}:{minutes}"
        # '오전' 또는 '오후' 부분과 시간 부분을 분리
        am_pm, time = parsed_hour.split(' ', 1)

        return (am_pm, time, parsed_date)

    @staticmethod
    def get_date():
        today = DateHelper.now()
        return today.strftime('%Y-%m-%d')

    @staticmethod
    def random_alpha(count=1):
        result = ''
        for i in range(0, count):
            result+=random.choice(string.ascii_letters)
        return result