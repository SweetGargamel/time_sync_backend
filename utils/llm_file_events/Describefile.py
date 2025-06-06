# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
import os
import sys
import json

from typing import List

from alibabacloud_bailian20231229.client import Client as bailian20231229Client
from alibabacloud_credentials.client import Client as CredentialClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient
from config import Config as cfg

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
    def main(
        file_id
    ) -> None:
        client = Sample.create_client()
        runtime = util_models.RuntimeOptions()
        headers = {}    
        try:
            # 复制代码运行请自行打印 API 的返回值
            response=client.describe_file_with_options('llm-mkgotttbebky5zg6', file_id, headers, runtime)
            body=response.body
            print(body)
            Data=body.data
            # print(Data.FileName)
            Status=Data.status
            return Status
        except Exception as error:
            # 此处仅做打印展示，请谨慎对待异常处理，在工程项目中切勿直接忽略异常。
            # 错误 message
            print(error.message)
            # 诊断地址
            print(error.data.get("Recommend"))
            UtilClient.assert_as_string(error.message)


if __name__ == '__main__':
    Sample.main("file_session_28534920a0b54a618e89ebda172b9cd5_11381862")