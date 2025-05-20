import os
import sys
import hashlib
import json

from typing import List
from config import Config as cfg
from alibabacloud_bailian20231229.client import Client as bailian20231229Client
from alibabacloud_credentials.client import Client as CredentialClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_bailian20231229 import models as bailian_20231229_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient


class Sample:
    def __init__(self):
        pass

    @staticmethod
    def create_client() -> bailian20231229Client:
        config = open_api_models.Config(
            access_key_id=cfg.CX_ACESS_KEY_ID,      # 替换为你的 AccessKey ID
            access_key_secret=cfg.CX_ACCESS_SECRET  # 替换为你的 AccessKey Secret
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
    def main(file_path: str) -> None:
        file_md5 = Sample.calculate_md5(file_path)
        file_size = str(os.path.getsize(file_path))  

        client = Sample.create_client()
        apply_file_upload_lease_request = bailian_20231229_models.ApplyFileUploadLeaseRequest(
            file_name=os.path.basename(file_path),    
            md_5=file_md5,                   
            size_in_bytes=file_size,          
            category_type='SESSION_FILE'
        )
        runtime = util_models.RuntimeOptions()
        headers = {}
        try:
            response=client.apply_file_upload_lease_with_options(
                'default',
                'llm-mkgotttbebky5zg6', #这里需要填写业务空间的id
                apply_file_upload_lease_request,
                headers,
                runtime
            )
            # with open('lease_response.json', 'w', encoding='utf-8') as f:
            #     json.dump(response.body.to_map(), f, ensure_ascii=False, indent=4)
            response_data = json.loads(json.dumps(response.body.to_map(), ensure_ascii=False, indent=4))
            print("在llmfileeventsAPI返回值为",response_data)

            return response_data
        except Exception as error:
            print(error.message)
            print(error.data.get("Recommend"))
            UtilClient.assert_as_string(error.message)

if __name__ == '__main__':
    file_path=sys.argv[1]
    Sample.main(file_path)
