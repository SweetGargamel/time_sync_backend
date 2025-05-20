from dashscope import Application
from config import Config as cfg
import json
import json_repair

def change_signle_event(user_need: str, event_id: str,index=0):
    if(index == 0):
        app_id  = cfg.WHC_CHANGE_TIME_PERFORM_SINGLE_CHANGE_APP_ID
    else:
        app_id  = cfg.WHC_CHANGE_TIME_PERFORM_SINGLE_CHANGE_APP_ID2
    response = Application.call(
        api_key=cfg.WHC_API_KEY,
        app_id=app_id,  # 替换为实际的应用 ID
        prompt=user_need,
        biz_params={
            "event_id": event_id,
        },
        has_thoughts=True,  # 是否开启思考过程

    )
    print("change signle response:", response)
    json_str = response["output"]["text"]
    print(json_str)
    output={}
    try:
        output = json.loads(json_str)
    except json.JSONDecodeError as e:
        output = json_repair.loads(json_str)
    return output
def perform_change(user_need: str, user_id: str) -> str:
    """
    删除时间事件
    :param user_id: 用户ID
    :return: 删除事件的描述
    """

    response = Application.call(
        # 若没有配置环境变量，可用百炼API Key将下行替换为：api_key="sk-xxx"。但不建议在生产环境中直接将API Key硬编码到代码中，以减少API Key泄露风险。
        api_key=cfg.WHC_API_KEY,
        app_id=cfg.WHC_DELETE_TIME,  # 替换为实际的应用 ID
        prompt=user_need,
        biz_params={
            "user_id": user_id,
        },
        has_thoughts=True,  # 是否开启思考过程
    )
    print("perform_change response:", response)
    json_str = response["output"]["text"]
    id_list = {}
    print(json_str)
    try:
        id_list = json.loads(json_str)
    except json.JSONDecodeError as e:
        id_list = json_repair.loads(json_str)
    # code = obj.get("code", "200")  # 假设响应中有一个output字段包含意图信息
    output_list  = []
    print(id_list)
    success_cout = 0
    index =0
    for i in id_list:
        output=change_signle_event(user_need, i,index=index%2)
        print(i)
        output["event_id"] = i
        if(output.get("code",400) == 200):
            success_cout += 1
        output_list.append(output)

    
    return success_cout,output_list  


if __name__ == "__main__":
    # 测试
    user_need = "清除这周三的所有课程"
    user_id = "241220128"  # 替换为实际的用户ID
    response = perform_change(user_need, user_id)
    print(response)
