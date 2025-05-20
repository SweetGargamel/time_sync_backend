import json
import json_repair
from openai import OpenAI
from config import Config as cfg
client = OpenAI(
    api_key=cfg.HEQ_ALI_KEY, 
    base_url=cfg.NEW_HEQ_IDENTIFY_COLUMNS_MODEL_URL
)


system_prompt = """
## Role: 组名识别与映射专家

## Background:
用户提供了两组信息：
1.  `new_potential_groups`: 从新文件中提取的潜在组名列表 (字符串数组)。
2.  `existing_groups_with_ids`: 数据库中已经存在的组名及其ID的列表 (对象数组, 每个对象包含 `id` 和 `name` 字段)。

需要将 `new_potential_groups` 中的每个组名与 `existing_groups_with_ids` 进行比较。

## Goals:
1.  识别出 `new_potential_groups` 中那些在 `existing_groups_with_ids` 中**不存在**的组名。这些是真正的新组。
2.  对于 `new_potential_groups` 中那些在 `existing_groups_with_ids` 中**已存在**的组名，找出它们对应的ID。

## Constraints:
-   返回结果必须是一个JSON对象。
-   JSON对象应包含两个键：
    1.  `"new_group_names"`: 一个列表，包含所有真正新的组名（字符串类型）。如果所有潜在组都已存在，则此列表为空 `[]`。
    2.  `"identified_existing_groups"`: 一个列表，包含那些在 `new_potential_groups` 中提到并且在 `existing_groups_with_ids` 中能找到对应ID的组。列表中的每个元素都是一个对象，格式为 `{"id": <数据库中的组ID>, "name_from_file": "<new_potential_groups中的组名>"}`。如果所有潜在组都是新的，则此列表为空 `[]`。
-   返回的JSON内容不应包含任何markdown标记（如 ```json 或 ```）。
-   组名匹配应尽可能智能，例如，可以考虑去除常见的前后缀（如“学院”、“系”、“班”）或进行模糊匹配，但优先精确匹配。如果存在多个可能的匹配，优先选择最相似的那个。如果无法确定，则视为新组。

## OutputFormat:
返回一个JSON对象，格式如下：
```json
{
  "new_group_names": ["真正的新组名1", ...],
  "identified_existing_groups": [
    {"id": 123, "name_from_file": "文件中出现的已存在组名A"},
    {"id": 456, "name_from_file": "文件中出现的已存在组名B"},
    ...
  ]
}
```

## Examples:

### 例子 1:
输入:
```json
{
  "new_potential_groups": ["计算机学院", "物理学院", "历史学系", "数学系"],
  "existing_groups_with_ids": [
    {"id": 1, "name": "物理学院"},
    {"id": 2, "name": "化学学院"},
    {"id": 3, "name": "数学系"}
  ]
}
```
输出:
```json
{
  "new_group_names": ["计算机学院", "历史学系"],
  "identified_existing_groups": [
    {"id": 1, "name_from_file": "物理学院"},
    {"id": 3, "name_from_file": "数学系"}
  ]
}
```

### 例子 2:
输入:
```json
{
  "new_potential_groups": ["软件工程", "人工智能"],
  "existing_groups_with_ids": [
    {"id": 10, "name": "软件工程"},
    {"id": 11, "name": "人工智能"},
    {"id": 12, "name": "数据科学"}
  ]
}
```
输出:
```json
{
  "new_group_names": [],
  "identified_existing_groups": [
    {"id": 10, "name_from_file": "软件工程"},
    {"id": 11, "name_from_file": "人工智能"}
  ]
}
```

### 例子 3:
输入:
```json
{
  "new_potential_groups": ["市场部", "研发部"],
  "existing_groups_with_ids": []
}
```
输出:
```json
{
  "new_group_names": ["市场部", "研发部"],
  "identified_existing_groups": []
}
```
"""

def identified_nonrepeat_groups(new_potential_groups: list[str], existing_groups_with_ids: list[dict]):
    """Identifies new group names and maps existing ones to their IDs."""

    completion = client.chat.completions.create(
        model=cfg.NEW_HEQ_IDENTIFY_COLUMNS_MODEL,  # 此处以 deepseek-r1 为例，可按需更换模型名称。
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': json.dumps({"new_potential_groups": new_potential_groups, "existing_groups_with_ids": existing_groups_with_ids}, ensure_ascii=False)}
        ],
        response_format={"type": "json_object"},
    )
    
    obj = {}
    json_string = completion.choices[0].message.content
    try:
        obj = json.loads(json_string)
    except json.JSONDecodeError:
        obj = json_repair.loads(json_string)
    except Exception as e:
        print(f"Error parsing LLM response: {e}")
        return [], [] # Return empty lists on error

    new_group_names = obj.get('new_group_names', [])
    identified_existing_groups = obj.get('identified_existing_groups', [])

    if not isinstance(new_group_names, list):
        print(f"LLM returned unexpected format for new_group_names: {new_group_names}")
        new_group_names = []
    if not isinstance(identified_existing_groups, list):
        print(f"LLM returned unexpected format for identified_existing_groups: {identified_existing_groups}")
        identified_existing_groups = []
        
    return new_group_names, identified_existing_groups
