import sys
import json
from http import HTTPStatus
from .ApplyFileUploadLease import Sample as ApplyLeaseSample
from .UploadTempFile import operate
from .AddFile import Sample as AddFileSample
from .Describefile import Sample as DescribeFileSample
import time
from dashscope import Application
from config import Config as cfg

def upload_files(file_path_array):
    print(file_path_array)
    file_id_array=[]
    for file_path in file_path_array:
        try:
            
            # 步骤1：调用申请上传租约
            print("开始申请上传租约...")
            response_data=ApplyLeaseSample.main(file_path)
            time.sleep(2)  # 等待文件写入完成
            print("response_data",response_data)
            # 步骤2：执行文件上传
            print("\n开始上传文件...")
            operate(file_path,response_data=response_data)
            time.sleep(2)  # 等待上传完成
            
            # 步骤3：添加文件至数据管理
            print("\n开始添加文件至数据管理...")
            new_response_data   =   AddFileSample.main(file_path,response_data=response_data)
            flag=True
            while(flag):
                time.sleep(1)

                file_id=str(new_response_data['Data']['FileId'])
                if(DescribeFileSample.main(file_id)=='FILE_IS_READY'): 
                    flag=False
        
            print("\n上传文件所有步骤执行完成！")
            

            file_id = str(new_response_data['Data']['FileId'])
            file_id_array.append(file_id)
        except Exception as e:
            print(f"\n执行过程中出现错误: {str(e)}")
        print(file_id_array)
    return file_id_array
def calc_with_file(file_path_array,user_need):
    file_id_array=upload_files(file_path_array)
    #下面是我自己的智能体
    response = Application.call(
        # 若没有配置环境变量，可用百炼API Key将下行替换为：api_key="sk-xxx"。但不建议在生产环境中直接将API Key硬编码到代码中，以减少API Key泄露风险。
        api_key=cfg.CX_LLM_API_KEY,
        app_id=cfg.CX_GET_EVENTSIDS_APP_ID,# 替换为实际的应用 ID
        prompt=f"用户要求：{user_need},\n用户的文件如下",
        rag_options={
            "session_file_ids": file_id_array,  # FILE_ID1 替换为实际的临时文件ID,逗号隔开多个
        },
        response_format={"type": "json_object"}
    )

    if response.status_code != HTTPStatus.OK:
        print(f'request_id={response.request_id}')
        print(f'code={response.status_code}')
        print(f'message={response.message}')
    else:
        obj = {}
        json_str = response.output.text
        print(json_str)
        try:
            obj = json.loads(json_str)
        except json.JSONDecodeError :
            import json_repair
            obj = json_repair.loads(json_str)
        except Exception as e:
            print(e)
        return obj

def calc_witout_file(user_need):    
    response = Application.call(
        # 若没有配置环境变量，可用百炼API Key将下行替换为：api_key="sk-xxx"。但不建议在生产环境中直接将API Key硬编码到代码中，以减少API Key泄露风险。
        api_key=cfg.CX_LLM_API_KEY,
        app_id=cfg.CX_GET_EVENTSIDS_APP_ID,# 替换为实际的应用 ID
        prompt=f"用户要求：{user_need}",

        response_format={"type": "json_object"}
    )
    if response.status_code != HTTPStatus.OK:
        print(f'request_id={response.request_id}')
        print(f'code={response.status_code}')
        print(f'message={response.message}')
    else:
        obj = {}
        json_str = response.output.text
        try:
            obj = json.loads(json_str)
        except json.JSONDecodeError :
            import json_repair
            obj = json_repair.loads(json_str)
        except Exception as e:
            print(e)
        return obj


if __name__ == "__main__":
    # calc_with_file(["example1.txt"],"")
    pass