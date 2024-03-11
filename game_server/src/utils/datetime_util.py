#coding=utf-8
"""
时间处理工具
"""
import calendar
import datetime


FORMAT_DATE = '%Y-%m-%d'
FORMAT_DATE2 = '%Y%m%d'
FORMAT_DATETIME = '%Y-%m-%d %H:%M:%S'


def get_now_str(date_format=FORMAT_DATETIME):
    """
    获取当前时间的字符串
    :param date_format:
    :return:
    """
    return datetime_to_str(datetime.datetime.now(), date_format=date_format)


def timestamp_to_datetime(timestamp: int):
    """
    时间戳转datetime
    :param timestamp:
    :return:
    """
    return datetime.datetime.fromtimestamp(timestamp)


def timestamp_to_str(timestamp: int, date_format: str = FORMAT_DATE, process_none: bool = False):
    """
    时间戳转时间字符串
    165656565-》‘2020-12-12’
    :param timestamp:
    :param date_format:
    :param process_none:
    :return:
    """
    return datetime_to_str(timestamp_to_datetime(timestamp), date_format=date_format, process_none=process_none)


def datetime_to_str(dt: datetime.datetime, date_format: str = FORMAT_DATE, process_none: bool = False):
    """
    datetime转时间字符串
    :param dt:
    :param date_format:
    :param process_none:
    :return:
    """
    if process_none and dt is None:
        return ''
    return dt.strftime(date_format)


def str_to_datetime(date_str: str, date_format: str = FORMAT_DATE, process_none: bool = False):
    """
    字符串转datetime
    :param date_str:
    :param date_format:
    :param process_none:
    :return:
    """
    if process_none and not date_str:
        return None
    return datetime.datetime.strptime(date_str, date_format)


def datetime_to_data(data: datetime.date):
    return datetime.datetime(data.year, data.month, data.day, 0, 0, 0)

def days_of_the_month():
    """查询当前日期的所在月的天数"""

    cur_date = datetime.datetime.now()
    year = cur_date.year
    month = cur_date.month

    init_days_weekday, month_last_day = calendar.monthrange(year,
                                                            month)  # a,b——weekday的第一天是星期几（0-6对应星期一到星期天）和这个月的所有天数

    return month_last_day

def get_today_day():
    """获取今天是几号"""
    return datetime.date.today().day

def get_now_target_day():
    # 特定时间
    target_date = datetime.datetime(2023, 12, 1)
    
    # 当前时间
    current_date = datetime.datetime.now()
    
    # 计算距离特定时间的天数
    delta = current_date - target_date
    return delta.days
