from .get_intention import get_intention,get_delete_description,get_change_description
from .perform_delete import perform_delete
from .perform_change import perform_change
from typing import List
class UndefinedOperationError(Exception):
    def __init__(self, message="未能有效识别您期望的操作类型，请修改您的提示词"):
        self.msg=message
    def __str__(self):
        return self.msg

def llm_change_events_main(prompt:str,user_id_list:List[str]):
    """
    主函数，处理用户输入的提示词并获取意图
    :param prompt: 用户输入的提示词
    :param user_id: 用户id(注意你要循环使用这个数组)
    :return: 意图和描述类型123
    """
    opt_type= get_intention(prompt)
    if(opt_type=="Delete"):
        desc_type = get_delete_description(prompt)
        if(desc_type=="time_only" or desc_type=="time_description"):
            for user_id in user_id_list:
                id_list=perform_delete(prompt,user_id)
                return len(id_list)
        else:
            print("desc_type",desc_type)
            raise UndefinedOperationError("您提供的信息不够充分（缺少相关对于要删除事件的时间描述），请您修改提示词后再操作")

    elif(opt_type=="Change"):
        desc_type = get_change_description(prompt)
        if(desc_type=="time_description" or desc_type=="time_with_description"):
            for user_id in user_id_list:
                success_count,output=perform_change(prompt,user_id)
                return success_count,output
        else:
            print("desc_type",desc_type)
            raise UndefinedOperationError("您提供的信息不够充分(不包含详细的原来和要移动到的时间描述)，请您修改提示词后再操作")
    else:
        raise UndefinedOperationError("我们只支持修改和删除日程，未能识别您的操作意图，请修改您的提示词")