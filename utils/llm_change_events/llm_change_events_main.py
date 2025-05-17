from get_intention import get_intention,get_delete_description,get_change_description

class UndefinedOperationError(Exception):
    def __init__(self, message="未能有效识别您期望的操作类型，请修改您的提示词"):
        self.msg=message
    def __str__(self):
        return self.msg

def llm_change_events_main(prompt):
    """
    主函数，处理用户输入的提示词并获取意图
    :param prompt: 用户输入的提示词
    :return: 意图和描述类型123
    """
    opt_type= get_intention(prompt)
    if(opt_type=="Delete"):
        desc_type = get_delete_description(prompt)
        if(desc_type=="time_description"):
            pass
        elif(desc_type=="time_with_description"):
            pass
        else:
            raise UndefinedOperationError("您提供的信息不够充分，请您修改提示词后再操作")

    elif(opt_type=="Change"):
        desc_type = get_change_description(prompt)
        if(desc_type=="time_description"):
            pass
        elif(desc_type=="time_with_description"):
    else:
        raise UndefinedOperationError("我们只支持修改和删除日程，未能识别您的操作意图，请修改您的提示词")