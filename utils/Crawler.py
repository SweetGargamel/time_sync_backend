import asyncio
from utils.src.login import LoginCredential
from .src.getcourse import get_course_raw, get_first_week_start
import json
import ddddocr # 导入 ddddocr
from .course_converter import convert_to_events
# 初始化 ddddocr
ocr = ddddocr.DdddOcr()


async def handle_captcha(captcha_content: bytes) -> str:
    # 使用 ddddocr 识别验证码
    captcha = ocr.classification(captcha_content)
    print(f"识别到的验证码: {captcha}")
    # captcha="123123123"
    return captcha

async def crawler(username="", password="") ->json:
    # 在这里输入你的用户名和密码
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # 登录获取凭证
            credential = await LoginCredential.from_login(
                username=username,
                password=password,
                captcha_cb=handle_captcha
            )
            
            # 获取课程数据
            course_data = await get_course_raw(credential)
            
            # 解析原始数据
            course_json = json.loads(course_data)
            with open("courses.json", "w", encoding="utf-8") as f:
                json.dump(course_json, f, ensure_ascii=False, indent=4)
            # 创建精简版数据
            simplified_data = []
            for course in course_json['datas']['cxxszhxqkb']['rows']:
                simplified_course = {
                    'c_time_place': course['ZCXQJCDD'],
                    'c_name': course['KCM'],
                    'c_classroom': course['JASMC'],
                    'c_campus': course['XXXQDM_DISPLAY'],
                    "c_weeks": course['ZCMC'],
                    "c_exam_time":course["QMKSXX"],
                }
                simplified_data.append(simplified_course)
            
            # 保存精简版数据
            with open('simplified_courses.json', 'w', encoding='utf-8') as f:
                json.dump(simplified_data, f, ensure_ascii=False, indent=4)
            print("简化版：",simplified_data)
            print()
            print()
            # 获取学期开始日期
            semester_start = await get_first_week_start(credential)
            # print("学期开始日期:", semester_start)
            
            # 转换为事件格式
            events_data = convert_to_events(simplified_data, semester_start, username)
            
            # 保存事件数据
            with open('events.json', 'w', encoding='utf-8') as f:
                json.dump(events_data, f, ensure_ascii=False, indent=4)
            print("事件数据已保存到 events.json")

            return events_data

        except Exception as e:
            error_msg = str(e)
            if "无效的验证码" in error_msg:
                retry_count += 1
                if retry_count < max_retries:
                    print(f"验证码识别失败，第{retry_count}次重试...")
                    await asyncio.sleep(1)  # 暂停1秒
                    continue
                else:
                    print("验证码识别失败次数过多，请稍后重试")
                    raise ValueError("验证码识别失败次数过多")
            else:
                raise e
        

if __name__ == "__main__":
    # 运行异步主程序
    asyncio.run(crawler(username = "241220128",  password = "whc62558223--"))