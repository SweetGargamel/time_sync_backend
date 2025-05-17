# 示例代码仅供参考，请勿在生产环境中直接使用
import requests

def upload_file(pre_signed_url, file_path, headers):
    try:
        with open(file_path, 'rb') as file:
            # 下方设置请求方法用于文档上传，需与您在上一步中调用ApplyFileUploadLease接口实际返回的Data.Param中Method字段的值一致
            response = requests.put(pre_signed_url, data=file, headers=headers)

        # 检查响应状态码
        if response.status_code == 200:
            print("File uploaded successfully.")
        else:
            print(f"Failed to upload the file. ResponseCode: {response.status_code}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

def operate(file_path,response_data):

    pre_signed_url_or_http_url = response_data['Data']['Param']['Url']
    headers = {
        "X-bailian-extra": response_data['Data']['Param']['Headers']['X-bailian-extra'],
        "Content-Type": response_data['Data']['Param']['Headers']['Content-Type']
    }

    # 文档来源可以是本地，上传本地文档至百炼临时存储
    upload_file(pre_signed_url_or_http_url, file_path, headers)

if __name__ == "__main__":
    operate()
    
