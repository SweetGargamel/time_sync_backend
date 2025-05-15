from flask import Blueprint, request, jsonify, current_app
from .models import db, User, Group, UserGroup, UserEvents, LLMEvent ,Files # 导入数据库模型
from datetime import  datetime,date,time,timedelta
from .add_person import main
from .llm_file_events import main
from utils.ai_chat import process_LLM_event, process_query_schedule
import json
import asyncio
import threading # 新增导入
from utils.Prompt import prompt_of_LLM_events, promopt_of_query_schedule  # 假设你有这些prompt
from .Crawler import crawler

# 初始化全局计数器
index = 0

bp = Blueprint('main', __name__)





# def calculate_availability(dayL: date, dayR: date, persons: list[str], must_persons: list[str], duration_hours: float, all_events: list[UserEvents],suggest_count_want:int =10):
#     """
#     计算时间段内的用户可用性，并生成 time_slots 和初步的 suggest_time。
#     """
#     person_ids_int = {int(p) for p in persons}
#     must_person_ids_int = {int(p) for p in must_persons}
#     num_persons = len(person_ids_int)
#     num_must_persons = len(must_person_ids_int)

#     # 按用户ID组织事件，方便查询
#     user_events_map = {}
#     for p_id in person_ids_int:
#         user_events_map[p_id] = [e for e in all_events if e.user_id == p_id]

#     # --- 1. 计算 time_slots ---
#     time_slots = []
#     start_hour = 8
#     end_hour = 22 # 时间范围 8:00 到 21:59
#     time_interval_minutes = 30
#     # duration_intervals = int(duration_hours * 60 / time_interval_minutes) # 会议持续时间对应的 30 分钟间隔数

#     current_date = dayL
#     while current_date <= dayR:
#         day_info = {
#             "date": current_date.isoformat(),
#             "time_intervals": []
#         }
#         current_dt = datetime.combine(current_date, time(start_hour, 0))
#         end_dt_of_day = datetime.combine(current_date, time(end_hour, 0))

#         while current_dt < end_dt_of_day:
#             interval_start = current_dt
#             interval_end = current_dt + timedelta(minutes=time_interval_minutes)
#             interval_start_time_str = interval_start.strftime("%H:%M")
#             interval_end_time_str = interval_end.strftime("%H:%M")

#             available_count = 0
#             unavailable_ids = []
#             unavailable_must_ids = []
#             num_must_available = 0
#             weight = 0.0 # Initialize weight for the interval, to be calculated iteratively

#             for p_id in person_ids_int:
#                 is_busy = False
#                 # 检查该用户是否有事件与当前 30 分钟间隔重叠
#                 for event in user_events_map.get(p_id, []):
#                     # 事件时间需要是 aware 或 naive 一致，这里假设它们都是 naive UTC 或本地时间
#                     event_start = event.start_time # 假设是 datetime 对象
#                     event_end = event.end_time   # 假设是 datetime 对象
#                     # 检查重叠: (StartA < EndB) and (EndA > StartB)
#                     if event_start < interval_end and event_end > interval_start:
#                         is_busy = True
#                         break # 只要有一个事件重叠，该用户就忙碌

#                 if is_busy:
#                     unavailable_ids.append(str(p_id))
#                     if p_id in must_person_ids_int:
#                         unavailable_must_ids.append(str(p_id))
#                 else:
#                     available_count += 1
#                     if p_id in must_person_ids_int:
#                         num_must_available += 1
                
#                 # Accumulate weight based on availability and importance
#                 person_importance_factor = 1e9 if p_id in must_person_ids_int else 1
#                 if not is_busy: # If the person is available
#                     weight += person_importance_factor

#             interval_info = {
#                 "start": interval_start_time_str,
#                 "end": interval_end_time_str,
#                 "weight": weight, # 使用上面计算的 weight
#                 "available_people_count": available_count,
#                 "unavailable_people": unavailable_ids,
#                 "unavailable_must_people": unavailable_must_ids
#             }
#             day_info["time_intervals"].append(interval_info)
#             current_dt += timedelta(minutes=time_interval_minutes)

#         time_slots.append(day_info)
#         current_date += timedelta(days=1)

#     # --- 2. 计算初步的 suggest_time ---
#     potential_suggestions = []
#     current_date = dayL
#     while current_date <= dayR:
#         current_dt = datetime.combine(current_date, time(start_hour, 0))
#         end_dt_of_day = datetime.combine(current_date, time(end_hour, 0))

#         while current_dt + timedelta(hours=duration_hours) <= end_dt_of_day:
#             slot_start_dt = current_dt
#             slot_end_dt = slot_start_dt + timedelta(hours=duration_hours)

#             all_must_persons_available_for_duration = True
#             total_available_for_duration = 0
#             unavailable_for_duration = []

#             # 检查 must_persons 在整个 duration 内是否都可用
#             if num_must_persons > 0:
#                 for p_id in must_person_ids_int:
#                     person_available_duration = True
#                     for event in user_events_map.get(p_id, []):
#                         if event.start_time < slot_end_dt and event.end_time > slot_start_dt:
#                             person_available_duration = False
#                             break
#                     if not person_available_duration:
#                         all_must_persons_available_for_duration = False
#                         break # 如果一个 must_person 不可用，则此时间段无效

#             # 如果所有 must_persons 都可用（或没有 must_persons），则计算总可用人数
#             if all_must_persons_available_for_duration:
#                 for p_id in person_ids_int:
#                     person_available_duration = True
#                     for event in user_events_map.get(p_id, []):
#                          if event.start_time < slot_end_dt and event.end_time > slot_start_dt:
#                             person_available_duration = False
#                             break
#                     if person_available_duration:
#                         total_available_for_duration += 1
#                     else:
#                         unavailable_for_duration.append(str(p_id))

#                 # 添加到潜在建议列表
#                 potential_suggestions.append({
#                     "start_dt": slot_start_dt, # 保留 datetime 对象用于排序
#                     "end_dt": slot_end_dt,
#                     "available_people_count": total_available_for_duration,
#                     "unavailable_people": unavailable_for_duration
#                 })

#             current_dt += timedelta(minutes=time_interval_minutes) # 每次移动 30 分钟查找下一个起始点
#         current_date += timedelta(days=1)

#     # 按可用人数降序排序
#     potential_suggestions.sort(key=lambda x: x["available_people_count"], reverse=True)

#     # 格式化 suggest_time (默认取前 10 个)
#     initial_suggest_time = []
#     min_suggest_count = min(suggest_count_want,len(potential_suggestions)-1)
#     for suggestion in potential_suggestions[:min_suggest_count]:
#         initial_suggest_time.append({
#             "start_time": suggestion["start_dt"].strftime("%Y-%m-%d %H:%M"),
#             "end_time": suggestion["end_dt"].strftime("%Y-%m-%d %H:%M"),
#             "available_people_count": suggestion["available_people_count"],
#             "unavailable_people": suggestion["unavailable_people"]
#         })

#     return time_slots, initial_suggest_time


def calculate_availability(dayL: date, dayR: date, persons: list[str], must_persons: list[str], duration_hours: int, all_events: list[UserEvents],suggest_count_want:int =15,user_need: str=""):
    """
    计算时间段内的用户可用性，并生成 time_slots 和初步的 suggest_time。
    """
    person_ids_int = {int(p) for p in persons}
    must_person_ids_int = {int(p) for p in must_persons}
    num_persons = len(person_ids_int)
    num_must_persons = len(must_person_ids_int)

    # 按用户ID组织事件，方便查询
    user_events_map = {}
    for p_id in person_ids_int:
        user_events_map[p_id] = [e for e in all_events if e.user_id == p_id]

    # --- 1. 计算 time_slots ---
    time_slots = []
    start_hour = 8
    end_hour = 22 # 时间范围 8:00 到 21:59
    time_interval_minutes = 30
    # duration_intervals = int(duration_hours * 60 / time_interval_minutes) # 会议持续时间对应的 30 分钟间隔数

    current_date = dayL
    while current_date <= dayR:
        day_info = {
            "date": current_date.isoformat(),
            "time_intervals": []
        }
        current_dt = datetime.combine(current_date, time(start_hour, 0))
        end_dt_of_day = datetime.combine(current_date, time(end_hour, 0))

        while current_dt < end_dt_of_day:
            interval_start = current_dt
            interval_end = current_dt + timedelta(minutes=time_interval_minutes)
            interval_start_time_str = interval_start.strftime("%H:%M")
            interval_end_time_str = interval_end.strftime("%H:%M")

            available_count = 0
            unavailable_ids = []
            unavailable_must_ids = []
            num_must_available = 0
            weight = 0.0 # Initialize weight for the interval, to be calculated iteratively

            for p_id in person_ids_int:
                is_busy = False
                # 检查该用户是否有事件与当前 30 分钟间隔重叠
                for event in user_events_map.get(p_id, []):
                    # 事件时间需要是 aware 或 naive 一致，这里假设它们都是 naive UTC 或本地时间
                    event_start = event.start_time # 假设是 datetime 对象
                    event_end = event.end_time   # 假设是 datetime 对象
                    # 检查重叠: (StartA < EndB) and (EndA > StartB)
                    if event_start < interval_end and event_end > interval_start:
                        is_busy = True
                        break # 只要有一个事件重叠，该用户就忙碌

                if is_busy:
                    unavailable_ids.append(str(p_id))
                    if p_id in must_person_ids_int:
                        unavailable_must_ids.append(str(p_id))
                else:
                    available_count += 1
                    if p_id in must_person_ids_int:
                        num_must_available += 1
                
                # Accumulate weight based on availability and importance
                person_importance_factor = 1e9 if p_id in must_person_ids_int else 1
                if not is_busy: # If the person is available
                    weight += person_importance_factor

            interval_info = {
                "start": interval_start_time_str,
                "end": interval_end_time_str,
                "weight": weight, # 使用上面计算的 weight
                "available_people_count": available_count,
                "unavailable_people": unavailable_ids,
                "unavailable_must_people": unavailable_must_ids
            }
            day_info["time_intervals"].append(interval_info)
            current_dt += timedelta(minutes=time_interval_minutes)

        time_slots.append(day_info)
        current_date += timedelta(days=1)

    ai_array=process_query_schedule(dayL,dayR,user_need)
    val_date=ai_array["date_weights"]
    val_time=ai_array["time_weights"]
    
    # --- 2. 计算初步的 suggest_time ---
    potential_suggestions = []
    current_date = dayL
    while current_date <= dayR:
        current_dt = datetime.combine(current_date, time(start_hour, 0))
        end_dt_of_day = datetime.combine(current_date, time(end_hour, 0))

        while current_dt + timedelta(hours=duration_hours) <= end_dt_of_day:
            slot_start_dt = current_dt
            slot_end_dt = slot_start_dt + timedelta(hours=duration_hours)

            all_must_persons_available_for_duration = True
            total_available_for_duration = 0
            unavailable_for_duration = []

            # 检查 must_persons 在整个 duration 内是否都可用
            if num_must_persons > 0:
                for p_id in must_person_ids_int:
                    person_available_duration = True
                    for event in user_events_map.get(p_id, []):
                        if event.start_time < slot_end_dt and event.end_time > slot_start_dt:
                            person_available_duration = False
                            break
                    if not person_available_duration:
                        all_must_persons_available_for_duration = False
                        break # 如果一个 must_person 不可用，则此时间段无效

            # 如果所有 must_persons 都可用（或没有 must_persons），则计算总可用人数
            if all_must_persons_available_for_duration:
                for p_id in person_ids_int:
                    person_available_duration = True
                    for event in user_events_map.get(p_id, []):
                         if event.start_time < slot_end_dt and event.end_time > slot_start_dt:
                            person_available_duration = False
                            break
                    if person_available_duration:
                        total_available_for_duration += 1
                    else:
                        unavailable_for_duration.append(str(p_id))

                delta_days=current_dt.date()-dayL
                delta_times=current_dt-datetime.combine(current_date, time(start_hour, 0))

                tot_times=delta_times.total_seconds() / 60 / 30
                Val_time = 0
                for t1 in range(int(tot_times),int(tot_times+int(duration_hours*2))):
                    Val_time = Val_time + val_time[t1]
                
                # 添加到潜在建议列表
                potential_suggestions.append({
                    "start_dt": slot_start_dt, # 保留 datetime 对象用于排序
                    "end_dt": slot_end_dt,
                    "available_people_count": total_available_for_duration,
                    "unavailable_people": unavailable_for_duration,
                    "weights":total_available_for_duration*val_date[delta_days.days]*Val_time
                })

            current_dt += timedelta(minutes=time_interval_minutes) # 每次移动 30 分钟查找下一个起始点
        current_date += timedelta(days=1)

    # 按可用人数降序排序
    potential_suggestions.sort(key=lambda x: x["weights"], reverse=True)

    # 格式化 suggest_time (默认取前 10 个)
    initial_suggest_time = []
    min_suggest_count = min(suggest_count_want,len(potential_suggestions)-1)
    for suggestion in potential_suggestions[:min_suggest_count]:
        initial_suggest_time.append({
            "start_time": suggestion["start_dt"].strftime("%Y-%m-%d %H:%M"),
            "end_time": suggestion["end_dt"].strftime("%Y-%m-%d %H:%M"),
            "available_people_count": suggestion["available_people_count"],
            "unavailable_people": suggestion["unavailable_people"]
        })

    return time_slots, initial_suggest_time

@bp.route('/api/crawl_nju_class', methods=['POST'])
async def crawl_nju_class():
    data = request.get_json()
    print("/api/crawl_nju_class", data)
    response_data = {
        "code": 200,
        "msg": "课表已经成功导入后台"
    }
    try:
        resp_json = await crawler(username=data["id"], password=data["password"]) 
        events = resp_json['events']
        await update_events(events)
        return jsonify(response_data)
    except ValueError as e:
        error_msg = str(e)
        if "您提供的用户名或者密码有误" in error_msg or "msg" in error_msg:
            response_data = {
                "code": 401,
                "msg": "输入正确的用户密码"
            }
        elif "验证码识别失败次数过多" in error_msg:
            response_data = {
                "code": 403,
                "msg": "后台的爬虫验证码自动识别错误，请您稍后再试"
            }
        else:
            response_data = {
                "code": 403 ,
                "msg": str(e)
            }
        return jsonify(response_data)
    except Exception as e:
        response_data = {
            "code": 500,
            "msg": str(e)
        }
        return jsonify(response_data)
    
def process_ai_output_of_query_schedule(good_time:json):
    """
    处理AI输出的时间建议，将unavailable_people字段重新添加到结果中
    
    Args:
        good_time: AI返回的时间建议列表，每个元素包含start_time, end_time, available_people_count
        
    Returns:
        处理后的时间建议列表，包含完整的字段信息
    """
    try:
        ai_output = good_time
            
        # 获取原始时间建议列表（包含unavailable_people）
        original_suggestions = ai_output
        
        # 创建结果列表
        processed_suggestions = []
        
        # 遍历AI输出的每个时间建议
        for ai_suggestion in original_suggestions:
            # 在原始建议中查找匹配的时间段
            for original in original_suggestions:
                if (ai_suggestion['start_time'] == original['start_time'] and 
                    ai_suggestion['end_time'] == original['end_time'] and 
                    ai_suggestion['available_people_count'] == original['available_people_count']):
                    # 找到匹配项，添加unavailable_people字段
                    processed_suggestion = ai_suggestion.copy()
                    processed_suggestion['unavailable_people'] = original.get('unavailable_people', [])
                    processed_suggestions.append(processed_suggestion)
                    break
        
        return processed_suggestions
        
    except Exception as e:
        print(f"处理AI输出时出错: {e}")
        return good_time  # 如果处理失败，返回原始输入

@bp.route('/api/query_schedule', methods=['POST'])
def handle_query_schedule():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input"}), 400

    try:
        dayL_str = data.get('start_day')
        dayR_str = data.get('end_day')
        persons = data.get('persons', [])
        must_persons = data.get('must_persons', [])
        duration_time = float(data.get('duration_time', 1)) # 持续时间，单位小时
        user_need = data.get('user_need', '') # 获取用户需求
        # suggest_count_want=data.get("suggest_count_want",10)
        if not all([dayL_str, dayR_str, persons]):
             raise ValueError("Missing required fields: start_day, end_day, persons")

        dayL = datetime.strptime(dayL_str.split('T')[0], "%Y-%m-%d").date()
        dayR = datetime.strptime(dayR_str.split('T')[0], "%Y-%m-%d").date()

        if duration_time <= 0:
             raise ValueError("Duration must be positive")

        # 将 ID 转换为整数集合，用于数据库查询
        person_ids_int = {int(p) for p in persons}
        must_person_ids_int = {int(p) for p in must_persons}

    except (ValueError, TypeError, KeyError) as e:
        return jsonify({"error": f"Invalid input data: {e}"}), 400

    try:
        # --- 数据库查询 ---
        # 1. 获取用户信息 (ID 和 Name)
        users = User.query.filter(User.user_id.in_(list(person_ids_int))).all()
        user_data = {user.user_id: user.name for user in users}
        # 确保所有请求的 person ID 都有对应的名字
        for p_id_str in persons:
            if int(p_id_str) not in user_data:
                # 如果找不到用户，可以返回错误或用 ID 代替名字
                 return jsonify({"error": f"User with ID {p_id_str} not found"}), 404

        # 2. 获取相关用户的事件
        # 构建查询范围，稍微扩大一点以包含边界情况
        query_start_dt = datetime.combine(dayL, time.min)
        query_end_dt = datetime.combine(dayR, time.max)
        all_events = UserEvents.query.filter(
            UserEvents.user_id.in_(list(person_ids_int)),
            UserEvents.start_time < query_end_dt, # 事件开始时间在查询结束之前
            UserEvents.end_time > query_start_dt    # 事件结束时间在查询开始之后
        ).all()



        # --- 计算可用性 ---
        time_slots, initial_suggest_time = calculate_availability(
            dayL, dayR, persons, must_persons, duration_time,  all_events,user_need=user_need
        )

        # --- 调用 AI 进行排序 ---
        final_suggest_time = initial_suggest_time # 默认使用初始排序
        
        # if user_need and initial_suggest_time:
        #     try:
        #         # 准备 AI 输入
        #         ai_input_json = json.dumps(initial_suggest_time, ensure_ascii=False)
        #         ##############################

        #         # 调用 chat 函数 (需要替换为实际实现)
        #         ai_output_json =  process_query_schedule(prompt_query_schedule=promopt_of_query_schedule,json_input=ai_input_json,user_need=user_need)
        #         # 解析 AI 输出并处理
        #         final_suggest_time = process_ai_output_of_query_schedule(ai_output_json)

        #         ###############
        #         print(final_suggest_time)


        #     except Exception as ai_error:
        #         print(f"Error during AI sorting: {ai_error}. Falling back to initial suggestions.")
        #         final_suggest_time = initial_suggest_time
        # else:
        #      print("No user_need provided or no initial suggestions, skipping AI sort.")


        # --- 准备最终响应 ---
        main_person_names = [user_data.get(int(p_id), str(p_id)) for p_id in must_persons] # 获取必到人员名字
        # print(time_slots)
        response_data = {
            "time_slots": time_slots,
            "suggest_time": final_suggest_time,
            "main_person": main_person_names, # 返回必到人员名字列表
            "total_days": (dayR - dayL).days + 1,
            "day_length": duration_time, # 返回请求的持续时间
            "date_range": {
                "start": dayL.isoformat(),
                "end": dayR.isoformat()
            },
            "code": 200
        }

        # print(json.dumps(response_data, indent=2, ensure_ascii=False)) # 打印用于调试
        return jsonify(response_data)

    except Exception as e:
        # 更详细的错误日志
        import traceback
        print(f"Error in handle_schedule: {e}\n{traceback.format_exc()}")
        db.session.rollback() # 如果有数据库操作需要回滚
        return jsonify({"error": "An internal server error occurred"}), 500


@bp.route('/api/groups', methods=['GET'])
def get_groups():
    """从数据库获取所有组及其成员信息"""
    try:
        groups = Group.query.all()
        groups_data = []
        for group in groups:
            groups_data.append({
                "id": str(group.group_id),
                "gname": group.name,
                "gperson": [str(user.user_id) for user in group.users]
            })
        print(groups_data)
        return jsonify({"groups": groups_data})
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

@bp.route('/api/persons', methods=['GET'])
def get_persons():
    """从数据库获取所有用户及其所属组信息"""
    try:
        users = User.query.all()
        # offset = users[0].user_id - 1
        persons_data = []
        for user in users:
            persons_data.append({
                "id": str(user.user_id),
                "name": user.name,
                "belong_group": [str(group.group_id) for group in user.groups]
            })
        print(persons_data)
        return jsonify({"persons": persons_data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 新增的更新人员接口

@bp.route('/api/update_persons', methods=['POST'])
def update_persons():
    data = request.get_json()
    # print(data)
    if not data or 'persons' not in data:
        return jsonify({"error": "Invalid input"}), 400

    persons_data = data['persons']
    print("Received persons data:")
    print(persons_data)
    results = []

    try:
        for person_info in persons_data:
            print(person_info)
            opt_type = person_info.get('opt_type')
            person_id = person_info.get('id')
            name = person_info.get('name')
            belong_group_ids = person_info.get('belong_group', [])

            if opt_type == 'create':
                if not name or not person_id:
                    results.append({"id": None, "status": "error", "message": "Name and ID are required for creation"})
                    continue
                # 检查ID是否已存在
                if User.query.get(person_id):
                    results.append({"id": person_id, "status": "error", "message": "ID already exists"})
                    continue
                new_user = User(user_id=person_id, name=name)
                # 处理组关系
                groups = Group.query.filter(Group.group_id.in_(belong_group_ids)).all()
                new_user.groups = groups
                db.session.add(new_user)
                db.session.flush()
                results.append({"id": new_user.user_id, "status": "created"})

            elif opt_type == 'update':
                if not person_id:
                    results.append({"id": None, "status": "error", "message": "ID is required for update"})
                    continue
                user = User.query.get(person_id)
                if not user:
                    results.append({"id": person_id, "status": "error", "message": "User not found"})
                    continue
                if name:
                    user.name = name
                # 更新组关系：先清空再添加
                user.groups.clear()
                groups = Group.query.filter(Group.group_id.in_(belong_group_ids)).all()
                user.groups = groups
                results.append({"id": user.user_id, "status": "updated"})

            elif opt_type == 'delete':
                if not person_id:
                    results.append({"id": None, "status": "error", "message": "ID is required for deletion"})
                    continue
                user = User.query.get(person_id)
                if not user:
                    results.append({"id": person_id, "status": "error", "message": "User not found"})
                    continue
                # 删除用户前需要处理关联关系，或者配置级联删除
                # 这里简单删除用户，关联表中的记录可能需要手动或通过级联删除处理
                db.session.delete(user)
                results.append({"id": person_id, "status": "deleted"})

            else:
                results.append({"id": person_id, "status": "error", "message": f"Invalid opt_type: {opt_type}"})

        db.session.commit()
        return jsonify({"code": 200, "results": results})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# 新增的更新组接口
@bp.route('/api/update_group', methods=['POST'])
def update_group():
    data = request.get_json()
    if not data or 'groups' not in data:
        return jsonify({"error": "Invalid input"}), 400

    groups_data = data['groups']
    results = []

    try:
        for group_info in groups_data:
            opt_type = group_info.get('opt_type')
            group_id = group_info.get('id')
            gname = group_info.get('name') # Changed from 'gname' to match comment example
            gperson_ids = group_info.get('persons', []) # Changed from 'gperson' to match comment example

            if opt_type == 'create':
                if not gname:
                    results.append({"id": group_id, "status": "error", "message": "Group name (name) is required for creation"})
                    continue
                new_group = Group(name=gname)
                # Find users and add them to the group
                users = User.query.filter(User.user_id.in_(gperson_ids)).all()
                new_group.users = users
                db.session.add(new_group)
                db.session.flush() # Get the new group's ID
                results.append({"id": new_group.group_id, "status": "created"})

            elif opt_type == 'update':
                if not group_id:
                    raise 
                group = Group.query.get(group_id)
                if not group:
                    results.append({"id": group_id, "status": "error", "message": "Group not found"})
                    continue
                if gname:
                    group.name = gname
                # Update group members: clear existing and add new
                group.users.clear()
                users = User.query.filter(User.user_id.in_(gperson_ids)).all()
                group.users = users
                results.append({"id": group.group_id, "status": "updated"})

            elif opt_type == 'delete':
                if not group_id:
                    results.append({"id": None, "status": "error", "message": "ID is required for deletion"})
                    continue
                group = Group.query.get(group_id)
                if not group:
                    results.append({"id": group_id, "status": "error", "message": "Group not found"})
                    continue
                # Deleting the group might require handling associations in UserGroup
                # or rely on cascade delete settings.
                # Simple deletion:
                db.session.delete(group)
                results.append({"id": group_id, "status": "deleted"})

            else:
                results.append({"id": group_id, "status": "error", "message": f"Invalid opt_type: {opt_type}"})

        db.session.commit()
        return jsonify({"code": 200, "results": results})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500




async def update_events(events):
    try:
        for event in events:
            person_ids = event.get('persons')
            start_date_str = event.get('start_date')
            start_time_str = event.get('start_time')
            end_date_str = event.get('end_date')
            end_time_str = event.get('end_time')
            reason = event.get('reason', '') # Optional reason
            event_id = event.get('id')

            try:
                start_datetime = datetime.strptime(f"{start_date_str} {start_time_str}", "%Y-%m-%d %H:%M")
                end_datetime = datetime.strptime(f"{end_date_str} {end_time_str}", "%Y-%m-%d %H:%M")
            except ValueError as ve:
                print(f"Skipping event due to invalid date/time: {event.get('id', 'N/A')}, Error: {ve}")
                continue

            for person_id_str in person_ids:
                # 检查记录是否已存在
                existing_event = UserEvents.query.filter_by(
                    event_id=event_id,
                    user_id=person_id_str
                ).first()

                if existing_event:
                    # 如果记录存在，更新现有记录
                    existing_event.start_time = start_datetime
                    existing_event.end_time = end_datetime
                    existing_event.reason = reason
                else:
                    # 如果记录不存在，创建新记录
                    new_busy_slot = UserEvents(
                        event_id=event_id,
                        user_id=person_id_str,
                        start_time=start_datetime,
                        end_time=end_datetime,
                        reason=reason
                    )
                    db.session.add(new_busy_slot)

        # 提交所有更改
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        print(f"Error processing events: {e}")
        import traceback
        tb = e.__traceback__
        tb_info = traceback.extract_tb(tb)
        for frame in tb_info:
            filename, line, func, text = frame
            print(f"文件: {filename}, 行号: {line}, 函数: {func}, 代码: {text}")
        raise
# 新增手动更新事情的api
@bp.route("/api/update_user_confirmed_events",methods=['POST'])
async def update_user_confirmed_events():
    data = request.get_json()

    if not data or 'events' not in data:
        return jsonify({"code": 500, "msg": "失败"}), 500
    print(data)
    events = data['events']
    print("事件信息为",events)
    # Remove unused results list
    try:
        await update_events(events)
        return jsonify({"code": 200, "msg": "成功"})
    except Exception as e:
        print("报错了",e)
        return jsonify({"code": 500, "msg": "服务器内部错误"}), 500




################################################################################################################################################################################################################################################################################################################################################################################################################################################################
def process_events_background(events_data, app):
    """后台处理事件的函数"""
    print("开始处理事件",events_data)
    try:
        with app.app_context():
            for event in events_data:
                try:
                    files_id = event.get('files',[])
                    files_path = []
                    eventstring = event['event_string']
                    for file_id in files_id:
                        file_record = Files.query.filter(
                            Files.file_id == file_id
                        ).first()
                        if not file_record:
                            return jsonify({"error": "File not found"}), 404
                        files_path.append(file_record.file_path)
                    agent_events = main.calc(file_path,eventstring)
                    event['event_string'] = agent_events
                    result =process_LLM_event(event, prompt_of_LLM_events)
                    print(result)
                except Exception as e:
                    print(f"处理事件 {event['id']} 时出错: {e}")
                    continue
    except Exception as e:
        print(f"后台处理事件时出错: {e}")

@bp.route("/api/upload_LLM_events", methods=['POST'])
def upload_LLM_events():  # 移除async关键字，因为不再需要异步处理
    data = request.get_json()
    try:
        events_data = data['events']
        app_instance = current_app._get_current_object()
        
        # 写入LLM_events表
        with app_instance.app_context():
            for event in events_data:
                llm_event = LLMEvent(
                    id=event['id'],
                    timestamp=event['timestamp'],
                    status='processing',
                    event_string=event['event_string'],
                    persons=event['persons'],
                    groups=event['groups']
                )
                db.session.merge(llm_event)
            db.session.commit()

        thread = threading.Thread(
            target=process_events_background,  # 直接传递函数
            args=(events_data, app_instance)  # 传递参数
        )
        thread.start()
        
        return jsonify({"code":200,"msg":"成功"})
    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({"code":500,"msg":"失败"}), 500


from werkzeug.utils import secure_filename
import os
from flask import current_app



index = 0
@bp.route('/api/upload_file', methods=['POST'])
def upload_file():
    # 检查文件是否存在
    if 'file' not in request.files:
        return jsonify(code=400, msg='没有选择文件')
    
    file = request.files['file']
    # 检查文件名是否合法
    if file.filename == '':
        return jsonify(code=400, msg='无效文件名')
    
    # 获取表单数据
    file_id = request.form.get('id')
    if file_id is None:
        print("缺少ID参数")
        return jsonify(code=400, msg='缺少ID参数')
    file_id = str(file_id)
    file_name = file.filename
    print(f"Received file_id: {file_id}")
    # 验证必要参数
    if not file_id or not file_name:
        return jsonify(code=400, msg='缺少ID或文件名参数')
    

    
    try:
        # 获取上传目录配置
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        
        # 确保上传目录存在
        os.makedirs(upload_folder, exist_ok=True)
        
        # 安全处理文件名（使用自定义文件名+原扩展名）
        # original_ext = file.filename.rsplit('.', 1)[1].lower()
        global index
        safe_filename = f"{index}_{file_name}"
        index += 1
        # 保存文件
        file_path = os.path.join(upload_folder, safe_filename)
        file.save(file_path)
        new_file = Files(
            file_id=file_id,
            file_path=file_path
        )
        db.session.add(new_file)
        db.session.commit()
        response_json = jsonify( {
        "code": 200,
        "msg": "success",
        "id": file_id,
        "file_name": file_name
        })
        return response_json
    except Exception as e:
        print(e)
        return jsonify(code=500, msg=f'服务器错误: {str(e)}')


@bp.route("/api/get_updating_events_url/<id>",methods=['GET'])
def get_updating_events_url(id):
    try:
        # 从数据库中查询指定ID的事件
        llm_event = db.session.query(LLMEvent).filter_by(id=id).first()
        
        if not llm_event:
            return jsonify({
                "id": id,
                "status": "not_found",
                "details": []
            }), 404
            
        # 如果有returned_entry，直接返回
        if llm_event.returned_entry:
            return jsonify(llm_event.returned_entry)
            
        # 如果没有returned_entry，返回基本信息
        return jsonify({
            "id": llm_event.id,
            "status": llm_event.status,
            "timestamp": llm_event.timestamp,
            "details": []
        })
        
    except Exception as e:
        print(f"获取事件状态时出错: {e}")
        return jsonify({
            "id": id,
            "status": "failed",
            "details": []
        }), 500



@bp.route("/api/view_events",methods=['POST'])
def view_events():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input"}), 400

    try:
        # 获取请求参数
        person_ids = data.get('id')
        start_date_str = data.get('start_date')
        start_time_str = data.get('start_time', '00:00')
        end_date_str = data.get('end_date')
        end_time_str = data.get('end_time', '23:59')

        # 检查必要参数
        if not all([start_date_str, end_date_str]):
            return jsonify({"error": "Missing required date parameters"}), 400

        # 转换日期时间格式
        try:
            start_datetime = datetime.strptime(f"{start_date_str} {start_time_str}", "%Y-%m-%d %H:%M")
            end_datetime = datetime.strptime(f"{end_date_str} {end_time_str}", "%Y-%m-%d %H:%M")
        except ValueError as e:
            return jsonify({"error": f"Invalid date time format: {str(e)}"}), 400

        # 查询数据库
        events = UserEvents.query.filter(
            UserEvents.user_id.in_([int(person_ids)]),
            UserEvents.start_time <= end_datetime,
            UserEvents.end_time >= start_datetime
        ).all()
        

        # 格式化返回结果
        result = {
            "events": [
                {
                    "id": event.event_id,
                    "pid": str(event.user_id),
                    "reason": event.reason,
                    "start_date": event.start_time.strftime("%Y-%m-%d"),
                    "start_time": event.start_time.strftime("%H:%M"),
                    "end_date": event.end_time.strftime("%Y-%m-%d"),
                    "end_time": event.end_time.strftime("%H:%M")
                }
                for event in events
            ]
        }
        return jsonify(result)

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500


@bp.route("/api/delete_event",methods=['POST'])
def delete_event():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input"}), 400
    
    try:
        # 获取要删除的事件ID列表
        event_ids = data.get('events', [])
        if not event_ids:
            return jsonify({"error": "No event IDs provided"}), 400
            
        # 删除指定的事件
        deleted_count = UserEvents.query.filter(UserEvents.event_id.in_(event_ids)).delete(synchronize_session=False)
        
        # 提交事务
        db.session.commit()
        
        return jsonify({"code":200,"msg":"成功"}),200
        
    except Exception as e:
        # 发生错误时回滚事务
        db.session.rollback()
        return jsonify({"error": str(e)}), 500



@bp.route("/api/LLM_AI_insert_person", methods=['POST'])
def LLM_AI_insert_person(): 
    data = request.get_json()
    if not data or 'file_id' not in data:
        return jsonify({"error": "Missing file_id parameter"}), 400

    try:
        file_id = data['file_id']
        file_record = Files.query.filter(
            Files.file_id == file_id
        ).first()
        
        if not file_record:
            return jsonify({"error": "File not found"}), 404
            
        file_path = file_record.file_path
        main.main(file_path)
        return jsonify({"code":200,"msg":"提交成功"}),200
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify({"error": str(e)}), 500





@bp.route('/')
def home():
    return 'Hello, World!'
