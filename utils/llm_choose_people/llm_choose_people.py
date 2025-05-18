from http import HTTPStatus
from dashscope import Application
from config import Config as cfg
import json
def llm_choose_people(user_need):
    response = Application.call(
    # 若没有配置环境变量，可用百炼API Key将下行替换为：api_key="sk-xxx"。但不建议在生产环境中直接将API Key硬编码到代码中，以减少API Key泄露风险。
    api_key=cfg.CX_LLM_API_KEY,
    app_id='040e3eae9eb9481bba002b1f6315d855',# 替换为实际的应用 ID
    prompt=user_need,
    response_format={"type": "json_object"}
    )
    print(response)
    if response.status_code != HTTPStatus.OK:
        print(f'request_id={response.request_id}')
        print(f'code={response.status_code}')
        print(f'message={response.message}')
        print(f'请参考文档：https://help.aliyun.com/zh/model-studio/developer-reference/error-code')
    else:
        peop_list = []
        json_str = response.output.text
        try:
            peop_list = json.loads(json_str)
        except json.JSONDecodeError :
            import json_repair
            peop_list = json_repair.loads(json_str)
        except Exception as e:
            print(e)
        peop_list = [str(x) for x in peop_list]
        return peop_list