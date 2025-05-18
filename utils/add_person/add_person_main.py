import sys
import json
from http import HTTPStatus
from config import Config as cfg
from .ApplyFileUploadLease import ApplyFileUpload 
from .UploadTempFile import operate
from .AddFile import AddFile 
import time
from dashscope import Application

def main(file_path):
    try:
        # 步骤1：调用申请上传租约
        print("开始申请上传租约...")
        response_data=ApplyFileUpload.main(sys.argv[1:],file_path)
        time.sleep(2)  # 等待文件写入完成
        
        # 步骤2：执行文件上传
        print("\n开始上传文件...")
        operate(file_path,response_data)
        time.sleep(2)  # 等待上传完成
        
        # 步骤3：添加文件至数据管理
        print("\n开始添加文件至数据管理...")
        new_response_data=AddFile.main(sys.argv[1:],response_data=response_data)
        
        time.sleep(20)
        print("\n上传文件所有步骤执行完成！")
        
        # 读取并解析upload_response.json

        file_id = str(new_response_data['Data']['FileId'])

        response = Application.call(
            api_key=cfg.HEQ_ALI_KEY, 
            app_id=cfg.HEQ_ALI_APP_ID1,  # 应用ID替换YOUR_APP_ID
            prompt='你需要把文件中的每一行信息以json格式返回，json中共有两个字段，"user_id"和"name"，其中"user_id"字段为学工号，"name"字段为姓名。',
            rag_options={
                "session_file_ids": [file_id],  # FILE_ID1 替换为实际的临时文件ID,逗号隔开多个
            }
        )

        if response.status_code != HTTPStatus.OK:
            print(f'request_id={response.request_id}')
            print(f'code={response.status_code}')
            print(f'message={response.message}')
            print(f'请参考文档：https://help.aliyun.com/zh/model-studio/developer-reference/error-code')
        else:
            print("response:",response.output.text)

        response_1 = Application.call(
            api_key=cfg.HEQ_ALI_KEY, 
            app_id=cfg.HEQ_ALI_APP_ID2,  # 应用ID替换YOUR_APP_ID
            prompt=response.output.text
        )

        if response.status_code != HTTPStatus.OK:
            print(f'request_id={response.request_id}')
            print(f'code={response.status_code}')
            print(f'message={response.message}')
            print(f'请参考文档：https://help.aliyun.com/zh/model-studio/developer-reference/error-code')
        else:
            print("response1:",response_1.output.text)
        
    except Exception as e:
        print(f"\n执行过程中出现错误: {str(e)}")

if __name__ == "__main__":
    main()