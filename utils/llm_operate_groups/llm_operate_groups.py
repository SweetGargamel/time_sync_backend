from config import Config as cfg
import json
from dashscope import Application
import json_repair
def llm_operate_group(prompt):
    """
    获取意图
    :param prompt: 用户输入的提示词
    :return: 意图响应
    """
    response = Application.call(
    # 若没有配置环境变量，可用百炼API Key将下行替换为：api_key="sk-xxx"。但不建议在生产环境中直接将API Key硬编码到代码中，以减少API Key泄露风险。
    api_key=cfg.HEQ_ALI_KEY,  # 替换为实际的API Key
    app_id=cfg.NEW_HEQ_LLM_OPERATE_GROUPS_ID,# 替换为实际的应用 ID
    prompt=prompt)
    # 处理响应
    json_str= response["output"]["text"]
    obj = {}
    try:
        obj = json.loads(json_str)
    except json.JSONDecodeError as e:
        obj = json_repair.loads(json_str)
    print(json_str)
    code= obj.get("code",400 ) # 假设响应中有一个output字段包含意图信息
    msg= obj.get("msg","大模型响应异常，没有返回信息！")
    # description_type=obj.get("description_type","") # 假设响应中有一个output字段包含意图信息
    print(code,msg)
    return code,msg
