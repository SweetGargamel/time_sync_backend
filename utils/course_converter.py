import uuid
from datetime import datetime, timedelta
import re

# 从Crawler.py导入的课程时间映射
NJU_CLASS_TIME = {
    "1": {"start": "8:00", "end": "8:50"},
    "2": {"start": "9:00", "end": "9:50"},
    "3": {"start": "10:10", "end": "11:00"},
    "4": {"start": "11:10", "end": "12:00"},
    "5": {"start": "14:00", "end": "14:50"},
    "6": {"start": "15:00", "end": "15:50"},
    "7": {"start": "16:10", "end": "17:00"},
    "8": {"start": "17:10", "end": "18:00"},
    "9": {"start": "18:30", "end": "19:20"},
    "10": {"start": "19:30", "end": "20:20"},
    "11": {"start": "20:30", "end": "21:20"}
}

def _parse_weekday(weekday_str):
    weekday_map = {
        "周一": 0, "周二": 1, "周三": 2, "周四": 3, "周五": 4, "周六": 5, "周日": 6
    }
    return weekday_map.get(weekday_str)

import re

def _parse_weeks(weeks_str):
    # 去除所有空格并分割周的范围和条件部分
    weeks_str = weeks_str.strip().replace(" ", "")
    parts = weeks_str.split("周", 1)
    range_part = parts[0]
    cond_part = parts[1] if len(parts) > 1 else ''
    
    # 解析周的范围
    if '-' in range_part:
        start_str, end_str = range_part.split('-')
        start = int(start_str)
        end = int(end_str)
    else:
        # 单个周的情况
        start = end = int(range_part)
    
    weeks = list(range(start, end + 1))
    
    # 处理条件
    condition = ''
    if cond_part:
        # 使用正则表达式提取括号中的条件
        match = re.search(r'\((.*?)\)', cond_part)
        if match:
            condition = match.group(1)
    
    if condition == '双':
        weeks = [w for w in weeks if w % 2 == 0]
    elif condition == '单':
        weeks = [w for w in weeks if w % 2 == 1]
    
    return weeks

def _get_class_time(periods):
    # 处理类似 "7-8节" 或 "9-11节" 的格式
    periods = periods.replace("节", "").split("-")
    start_period = int(periods[0])
    end_period = int(periods[1])
    
    start_time = NJU_CLASS_TIME[str(start_period)]["start"]
    end_time = NJU_CLASS_TIME[str(end_period)]["end"]
    
    return start_time, end_time

def _calculate_date(semester_start, week_num, weekday):
    # semester_start 已经是 datetime.date 对象，不需要再次解析
    # 计算目标日期
    target_date = semester_start + timedelta(days=(week_num-1)*7 + weekday)
    return target_date.strftime("%Y-%m-%d")

def _parse_exam_time(exam_time_str):
    """解析考试时间字符串，返回日期和时间"""
    if "请咨询院系或任课教师" in exam_time_str:
        return None, None, None
    
    # 使用正则表达式提取日期和时间
    pattern = r"时间：(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2})-(\d{2}:\d{2})"
    match = re.search(pattern, exam_time_str)
    if match:
        date = match.group(1)
        start_time = match.group(2)
        end_time = match.group(3)
        return date, start_time, end_time
    return None, None, None

def convert_to_events(courses_data: list, semester_start: datetime.date, username: str) -> dict:
    try:
        """
        将课程数据转换为事件格式
        
        Args:
            courses_data (list): 课程数据列表
            semester_start (datetime.date): 学期开始日期
            username (str): 用户名
            
        Returns:
            dict: 包含转换后事件列表的字典
        """
        events = []
        
        for course in courses_data:
            # 跳过自由时间的课程
            if "自由时间" in course["c_time_place"]:
                continue
                
            time_place = course["c_time_place"].split()
            weekday = _parse_weekday(time_place[0])
            periods = time_place[1]
            weeks = time_place[2]
            
            weeks= _parse_weeks(weeks)
            start_time, end_time = _get_class_time(periods)
            
            # 为每个周生成一个事件
            for week in weeks:
                event_date = _calculate_date(semester_start, week, weekday)
                
                event = {
                    "id": str(uuid.uuid4()),
                    "reason": f"{course['c_name']}{course['c_classroom']}{course['c_campus']} {course['c_time_place']}",
                    "persons": [username],
                    "start_date": event_date,
                    "start_time": start_time,
                    "end_date": event_date,
                    "end_time": end_time
                }
                events.append(event)
            
            # 处理考试时间
            exam_date, exam_start_time, exam_end_time = _parse_exam_time(course["c_exam_time"])
            if exam_date and exam_start_time and exam_end_time:
                exam_event = {
                    "id": str(uuid.uuid4()),
                    "reason": f"{course['c_name']}期末考试 {course['c_campus']}",
                    "persons": [username],
                    "start_date": exam_date,
                    "start_time": exam_start_time,
                    "end_date": exam_date,
                    "end_time": exam_end_time
                }
                events.append(exam_event)
        
        return {"events": events} 
    except Exception as e:
        print(f"Error converting courses to events: {e}")
        return {"events": []}