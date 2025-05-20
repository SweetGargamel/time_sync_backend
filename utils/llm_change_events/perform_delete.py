from dashscope import Application
from config import Config as cfg
import json
import json_repair
from utils.models import db, UserEvents


def perform_delete(user_need: str, user_id: str) -> str:
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
    print("perform_delete response:", response)
    json_str = response["output"]["text"]
    id_list = {}
    print(json_str)
    try:
        id_list = json.loads(json_str)
    except json.JSONDecodeError as e:
        id_list = json_repair.loads(json_str)
    print(id_list)
    for i in id_list:
        print(i)
    
    # 删除UserEvents表中的数据
    for event_id in id_list:
        try:
            event = UserEvents.query.filter_by(event_id=event_id).first()
            if event:
                db.session.delete(event)
            db.session.commit()
        except Exception as e:
            print(f"删除事件 {event_id} 时出错: {str(e)}")
            db.session.rollback()
    
    return id_list  # 假设响应中有一个output字段包含删除事件的描述


if __name__ == "__main__":
    # 测试
    user_need = "清除这周三的所有课程"
    user_id = "241220128"  # 替换为实际的用户ID
    response = perform_delete(user_need, user_id)
    print(response)
