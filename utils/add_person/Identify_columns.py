import json
import json_repair
from openai import OpenAI
from config import Config as cfg
client = OpenAI(
    api_key=cfg.HEQ_ALI_KEY, 
    base_url=cfg.NEW_HEQ_IDENTIFY_COLUMNS_MODEL_URL
)
# system_prompt = """
# 用户会给你一个Excel表格的前15列（或者更少），你需要识别哪一列是id列（或者学号列，学工号列），哪一列是学生姓名列，哪一列是这个学生所属学院或者专业列。
# 请返回一个json，分别告诉我哪一列是id,哪一列是学生姓名，哪一列是所属学院或者专业列(注意，请你返回列的索引，从0开始)。
# ```json
# {
# "id_column": 1,
# "name_column": 2,
# "major_column": 3
# }
# ```
# """

system_prompt='''
## Role: 
# 数据分析专家和表格解析顾问
## Background: 
## 用户提供了一个表格数据，以列表的列表（list of lists）的形式给出，其中第一个子列表是表头，后续子列表是数据行（通常是前15行或更少的数据）。需要识别其中的ID列（或学号列、学工号列）、学生姓名列以及学生所属学院（或专业列）。用户希望借助专业的数据分析和表格解析能力，准确地定位这些关键列。
## Goals: 根据用户提供的表格数据（列表的列表形式），准确识别ID列、学生姓名列和所属学院或专业列，并以JSON格式返回结果。注意，请你返回列的索引，从0开始。
- 如果既有专业列也有学院则优先返回学院列的索引。
## Constrains: 
仅根据用户提供的表格数据进行操作，确保识别的准确性和逻辑性。注意，请你返回列的索引，从0开始。返回的内容禁止有```或者```json等内容。
## OutputFormat: 
返回一个JSON对象，包含ID列、学生姓名列和所属学院或专业列的列号。注意，请你返回列的索引，从0开始。返回的内容禁止有```或者```json等内容。
## Examples:
### 例子1：
表格数据（list of lists）如下：
```
[
  ["课程号", "课程名", "教师", "学号", "姓名", "学院"],
  [420040.0, "《万古江河：中国历史文化的转折与展开》阅读01班", "特木勒", 241870029, "秦绍俊", "*工科试验班"],
  [420070.0, "《意大利文艺复兴时期的文化》阅读02班", "闵凡祥", 241870081, "侯紫俊", "*工科试验班"],
  [420070.0, "《意大利文艺复兴时期的文化》阅读02班", "闵凡祥", 241870095, "赵熠杨", "*工科试验班"],
  [420100.0, "《大国的兴衰》阅读01班", "郑安光", 241870142, "蒋帅", "*工科试验班"],
  [430020.0, "《四书章句集注》阅读01班", "代玉民", 241870063, "王宣昊", "*工科试验班"]
]
```
    输出：
    ```json
    {
    "id_column": 3,
    "name_column": 4,
    "college_column": 5
    }
    ```
### 例子2：
表格数据（list of lists）如下：
```
[
  ["学号", "姓名", "班级"],
  [241870029, "张三", "计算机科学与技术1班"],
  [241870081, "李四", "软件工程2班"]
]
```
输出：
```json
{
  "id_column": 0,
  "name_column": 1,
  "college_column": -1
}
```
'''

def identify_columns_self(data_as_list_of_lists):
    """Identify columns in a file based on list of lists data."""

    completion = client.chat.completions.create(
        model=cfg.NEW_HEQ_IDENTIFY_COLUMNS_MODEL,  # 此处以 deepseek-r1 为例，可按需更换模型名称。
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': json.dumps(data_as_list_of_lists, ensure_ascii=False)}
        ],
        response_format={"type": "json_object"},
    )
    
    obj = {}
    json_string = completion.choices[0].message.content
    try:
        obj = json.loads(json_string)
    except json.JSONDecodeError:
        obj = json_repair.loads(json_string)
    # No general except Exception as e: print(e) here, let it propagate if not JSONDecodeError

    if 'id_column' not in obj or not isinstance(obj.get('id_column'), int) or obj.get('id_column') < 0:
        raise ValueError("缺少有效的id字段或无效的id字段")
    if 'name_column' not in obj or not isinstance(obj.get('name_column'), int) or obj.get('name_column') < 0:
        raise ValueError("缺少有效的name字段或无效的name字段")
    
    # college_column can be -1 if not found, or a valid non-negative index.
    # The prompt now explicitly asks for -1 if not found. So we expect it to be present and valid.
    if 'college_column' not in obj or not isinstance(obj.get('college_column'), int) or obj.get('college_column') < -1:
         raise ValueError("LLM did not return a valid 'college_column' (must be an integer >= -1).")

    id_column = obj['id_column']
    name_column = obj['name_column']
    college_column = obj['college_column']
    return id_column, name_column, college_column
