from config import Config as cfg
import json
from dashscope import Application
import json_repair
def get_intention(prompt):
    """
    获取意图
    :param prompt: 用户输入的提示词
    :return: 意图响应
    """
    response = Application.call(
    # 若没有配置环境变量，可用百炼API Key将下行替换为：api_key="sk-xxx"。但不建议在生产环境中直接将API Key硬编码到代码中，以减少API Key泄露风险。
    api_key=cfg.WHC_API_KEY,  # 替换为实际的API Key
    app_id=cfg.WHC_INTENSION_APP_ID,# 替换为实际的应用 ID
    prompt=prompt)
    # 处理响应
    json_str= response["output"]["text"]
    obj = {}
    try:
        obj = json.loads(json_str)
    except json.JSONDecodeError as e:
        obj = json_repair.loads(json_str)
    opt_type= obj.get("opt_type","" ) # 假设响应中有一个output字段包含意图信息
    # description_type=obj.get("description_type","") # 假设响应中有一个output字段包含意图信息
    return opt_type

    # 调用应用的call方法获取意图

def get_delete_description(prompt):
    """
    获取意图描述
    :param prompt: 用户输入的提示词
    :return: 意图描述
    """
    response = Application.call(
        api_key=cfg.WHC_API_KEY,  # 替换为实际的API Key
        app_id=cfg.WHC_DELETE_DESC_TYPE_APP_ID,  # 替换为实际的应用 ID
        prompt=prompt)
    # 处理响应
    json_str = response["output"]["text"]
    obj = {}
    try:
        obj = json.loads(json_str)
    except json.JSONDecodeError as e:
        obj = json_repair.loads(json_str)
    description_type = obj.get("description_type", "")  # 假设响应中有一个output字段包含意图信息
    return description_type

def get_change_description(prompt):
    """
    获取意图描述
    :param prompt: 用户输入的提示词
    :return: 意图描述
    """
    response = Application.call(
        api_key=cfg.WHC_API_KEY,  # 替换为实际的API Key
        app_id=cfg.WHC_CHANGE_DESC_TYPE_APP_ID,  # 替换为实际的应用 ID
        prompt=prompt)
    # 处理响应
    json_str = response["output"]["text"]
    obj = {}
    try:
        obj = json.loads(json_str)
    except json.JSONDecodeError as e:
        obj = json_repair.loads(json_str)
    description_type = obj.get("description_type", "")  # 假设响应中有一个output字段包含意图信息
    return description_type

if __name__ == "__main__":
    # 测试
    prompt = "清除周末的日程"
    intention = get_intention(prompt)
    print(f"意图: {intention}")