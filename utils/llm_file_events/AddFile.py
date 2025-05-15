import os
import sys
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
    def main(args: List[str],) -> None:
        with open('lease_response.json', 'r', encoding='utf-8') as f:
            response_data = json.load(f)
            lease_id = response_data['Data']['FileUploadLeaseId']
        client = Sample.create_client()
        add_file_request = bailian_20231229_models.AddFileRequest(
            lease_id=lease_id,
            parser='DASHSCOPE_DOCMIND',
            category_id='default',
            category_type='SESSION_FILE'
        )
        runtime = util_models.RuntimeOptions()
        headers = {}
        try:
            response = client.add_file_with_options('llm-mkgotttbebky5zg6', add_file_request, headers, runtime)
            # 把第一个参数改为业务空间ID
            
            # 保存返回值到json文件
            with open('upload_response.json', 'w', encoding='utf-8') as f:
                json.dump(response.body.to_map(), f, ensure_ascii=False, indent=4)
            print("API返回值已保存到 upload_response.json")
            
        except Exception as error:
            print(error.message)
            print(error.data.get("Recommend"))
            UtilClient.assert_as_string(error.message)

if __name__ == '__main__':
    Sample.main(sys.argv[1:])
