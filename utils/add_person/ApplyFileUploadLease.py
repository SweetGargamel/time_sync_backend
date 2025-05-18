import os
import sys
import hashlib
import json
from config import Config as cfg
from typing import List

from alibabacloud_bailian20231229.client import Client as bailian20231229Client
from alibabacloud_credentials.client import Client as CredentialClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_bailian20231229 import models as bailian_20231229_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient


class ApplyFileUpload:
    def __init__(self):
        pass

    @staticmethod
    def create_client() -> bailian20231229Client:
        config = open_api_models.Config(
            access_key_id=cfg.HEQ_ACESS_KEY_ID,      # 替换为你的 AccessKey ID
            access_key_secret=cfg.HEQ_ACESS_SECRET  # 替换为你的 AccessKey Secret
        )
        config.endpoint = f'bailian.cn-beijing.aliyuncs.com'
        return bailian20231229Client(config)

    @staticmethod
    def calculate_md5(file_path):
        """计算文档的 MD5 值"""
        md5_hash = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5_hash.update(chunk)
        return md5_hash.hexdigest()

    @staticmethod
    def main(args: List[str],path) -> None:
        # 计算文件的MD5值
        file_path = path
        file_md5 = ApplyFileUpload.calculate_md5(file_path)
        file_size = str(os.path.getsize(file_path))  

        client = ApplyFileUpload.create_client()
        apply_file_upload_lease_request = bailian_20231229_models.ApplyFileUploadLeaseRequest(
            file_name=path,    
            md_5=file_md5,                   
            size_in_bytes=file_size,          
            category_type='SESSION_FILE'
        )
        runtime = util_models.RuntimeOptions()
        headers = {}
        try:
            # 复制代码运行请自行打印 API 的返回值
            response=client.apply_file_upload_lease_with_options(
                'default',
                'llm-xzbu470zs36e65vl',
                apply_file_upload_lease_request,
                headers,
                runtime
            )
            # with open('lease_response.json', 'w', encoding='utf-8') as f:
            #     json.dump(response.body.to_map(), f, ensure_ascii=False, indent=4)
            response_data = response.body.to_map()
            # print("API返回值已保存到 lease_response.json")
            print("add_person reponse_data : " ,response_data)
            return response_data
        except Exception as error:
            # 此处仅做打印展示，请谨慎对待异常处理，在工程项目中切勿直接忽略异常。
            # 错误 message
            print(error.message)
            # 诊断地址
            print(error.data.get("Recommend"))
            UtilClient.assert_as_string(error.message)

if __name__ == '__main__':
    ApplyFileUpload.main(sys.argv[1:])
