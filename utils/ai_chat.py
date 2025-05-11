# import traceback

# clients=[]
# for key in Config.OPENAI_API_KEYS:
#     clients.append(AsyncOpenAI(
#         api_key=key,
#         base_url=Config.OPENAI_BASE_URL,
#     ))
# client_index=0
# client_count=len(Config.OPENAI_API_KEYS)
import json
import uuid
# 确认 openai 版本 >= 1.0 并导入 AsyncOpenAI
# pip install --upgrade openai
from openai import OpenAI 
import json_repair  # 新增
from config import Config
from utils.models import db, UserEvents, LLMEvent
from datetime import datetime
from typing import List
########################下面是大模型处理的部分######



# 将 chat 函数改为异步函数
def chat_return_json(contents: List[str],process_event_prompt:str) -> json:
    client=OpenAI(
    api_key=Config.get_key(),
    base_url=Config.OPENAI_BASE_URL,
    )
    user_msg = [{"role": "user", "content": content} for content in contents]
    # PREFILL_PRIFEX = "{"

    msg = [
        {"role": "system", "content": process_event_prompt},
        *user_msg,  # 展开用户消息列表
        # {"role": "assistant", "content": PREFILL_PRIFEX},
    ]
    print("--- AI chat_return_json started ---")
    completion = client.chat.completions.create(
        model=Config.MODEL_NAME,
        messages=msg,
        response_format={"type": "json_object"},
    )
    print(completion)
    print("完成调用大模型")
    # json_string = PREFILL_PRIFEX + completion.choices[0].message.content
    json_string = completion.choices[0].message.content
    print(json_string)
    obj = {}
    try:
        obj = json.loads(json_string)
    except json.JSONDecodeError :
        obj = json_repair.loads(json_string)
    except Exception as e:
        print(e)
    return obj


# 创建一个异步函数来处理单个事件
def process_LLM_event(event_data,process_event_prompt: str):
    """处理单个事件，调用大模型并返回结果或异常。"""
    event_id = event_data["id"]
    content = event_data["event_string"]
    timestamp = event_data["timestamp"]
    persons = event_data["persons"]
    groups = event_data["groups"]

    print(f"开始处理事件 ID: {event_id}")
    try:
        json_response = chat_return_json(contents=[content],process_event_prompt=process_event_prompt)

        output_events = json_response.get("events", []) # 使用 .get() 避免 KeyError
        
        # 检查是否成功提取到事件
        if not output_events or not any([ event for event in output_events ]):
            output_entry = {
                "id": event_id,
                "status": "failed",
                "details": [],
                "msg": "没有提取到有效的事件"
            }
            # 更新LLMEvent状态
            llm_event = db.session.query(LLMEvent).filter_by(id=event_id).first()
            if llm_event:
                llm_event.status = 'failed'
                llm_event.returned_entry = output_entry
                db.session.commit()
            return output_entry

        # 为子事件添加元数据
        for output_event in output_events:
            output_event.update({
                "id": str(uuid.uuid4()), # 为新生成的子事件创建唯一ID
                "persons": persons,
                "groups": groups
            })
            
            # 写入UserEvents表
            try:
                # 解析时间
                start_datetime = datetime.strptime(f"{output_event['start_date']} {output_event['start_time']}", "%Y-%m-%d %H:%M")
                end_datetime = datetime.strptime(f"{output_event['end_date']} {output_event['end_time']}", "%Y-%m-%d %H:%M")
                
                # 为每个person创建事件记录
                for person_id in persons:
                    user_event = UserEvents(
                        event_id=output_event['id'],
                        user_id=int(person_id),
                        start_time=start_datetime,
                        end_time=end_datetime,
                        reason=output_event.get('reason', content[:255])  # 使用原始内容作为原因，限制长度
                    )
                    db.session.add(user_event)
                
            except Exception as e:
                print(f"写入UserEvents失败: {e}")
                raise

        # 构造成功的结果条目
        output_entry = {
            "id": event_id, # 原始事件ID
            "status": "success",
            "details": output_events,
            "timestamp": timestamp,
            "msg": "处理成功"
        }

        # 更新LLMEvent状态为success和returned_entry
        llm_event = db.session.query(LLMEvent).filter_by(id=event_id).first()
        if llm_event:
            llm_event.status = 'success'
            llm_event.returned_entry = output_entry  # 保存完整的返回结果
            db.session.commit()

        print(f"成功处理事件 ID: {event_id}")
        return output_entry
        
    except Exception as e:
        print(f"处理事件 ID {event_id} 时出错: {e}")
        # 更新LLMEvent状态为failed
        try:
            llm_event = db.session.query(LLMEvent).filter_by(id=event_id).first()
            if llm_event:
                llm_event.status = 'failed'
                llm_event.returned_entry = {
                    "id": event_id,
                    "status": "failed",
                    "error": str(e),
                    "details": [],
                    "msg": str(e)
                }
                db.session.commit()
        except Exception as db_e:
            print(f"更新LLMEvent状态失败: {db_e}")
    output_entry = {
        "id": event_id, # 原始事件ID
        "status": "failed",
        "details": [],
        "msg": str(e) if 'e' in locals() else "处理失败"
    }
    return output_entry


#旧版代码
# from dashscope import Application
# # 你需要用实际的 LLM 调用替换它
# def process_query_schedule(prompt_query_schedule: str, json_input: str, user_need: str) -> json:
#     print("--- AI Sort Simulation ---")
#     print(f"User Need: {user_need}")
#     print(f"Input Suggestions (JSON): {json_input}")
#     msg=[
#         {"role": "user", "content":json_input},
#         {"role": "user", "content":user_need},
#         {'role': 'user', 'content': '请严格按照prompt中的OutputFormat要求，只输出JSON格式的结果，不要包含任何解释或额外文本。'}
#     ]
    
#     response = Application.call(
#     # 若没有配置环境变量，可用百炼API Key将下行替换为：api_key="sk-xxx"。但不建议在生产环境中直接将API Key硬编码到代码中，以减少API Key泄露风险。
#     api_key=Config.ALI_AGENT_APIKEY,
#     app_id=Config.ALI_AGENT_ID,# 替换为实际的应用 ID
#     messages=msg
#     )
#     print("智能体结果是:",response)
#     json_str=response.output.text
#     obj = {}

#     try:
#         obj = json.loads(json_str)
#     except json.JSONDecodeError :
#         obj = json_repair.loads(json_str)
#     except Exception as e:
#         print(e)
#     return obj
# # --- 结束占位符 ---



from dashscope import Application
# 你需要用实际的 LLM 调用替换它
def process_query_schedule(dayL,dayR,user_need: str) -> json:
    print(f"User Need: {user_need}")
    msg=[
        {"role": "user", "content":f"日期范围为{dayL.strftime("%Y-%m-%d")}到{dayR.strftime("%Y-%m-%d")},时间范围为8:00-22:00共28个时间段"},
        {"role": "user", "content":user_need},
        {'role': 'user', 'content': '请严格按照prompt中的输出格式要求，只输出JSON格式的结果，不要包含任何解释或额外文本。'}
    ]
    
    response = Application.call(
    # 若没有配置环境变量，可用百炼API Key将下行替换为：api_key="sk-xxx"。但不建议在生产环境中直接将API Key硬编码到代码中，以减少API Key泄露风险。
    api_key=Config.ALI_AGENT_APIKEY,
    app_id=Config.ALI_AGENT_ID,# 替换为实际的应用 ID
    messages=msg,
    response_format={"type": "json_object"}
    )
    print("智能体结果是:",response)
    json_str=response.output.text
    obj = {}

    try:
        obj = json.loads(json_str)
    except json.JSONDecodeError :
        obj = json_repair.loads(json_str)
    except Exception as e:
        print(e)
    return obj
# --- 结束占位符 ---