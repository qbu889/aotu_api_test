import json
import re


def clean_json(raw_json_str):
    """
    清理JSON中的不必要符号，包括制表符、冗余分隔符和无意义标记

    参数:
        raw_json_str: 原始JSON字符串
    返回:
        清理后的JSON字符串
    """
    # 清理非法控制字符
    raw_json_str = clean_control_characters(raw_json_str)

    # 解析JSON
    try:
        data = json.loads(raw_json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"无效的JSON格式: {str(e)}")

    # 处理parserResult字段（替换制表符为冒号）
    if 'parserResult' in data and data['parserResult']:
        data['parserResult'] = data['parserResult'].replace('\t', ':')

    # 处理cmdResult字段（清理各种冗余符号和标记）
    if 'cmdResult' in data and data['cmdResult']:
        cmd = data['cmdResult']

        # 移除%%开头的命令标记
        cmd = re.sub(r'%%.*?%%', '', cmd)

        # 移除结果个数标记
        cmd = re.sub(r'\(结果个数 = \d+\)', '', cmd)

        # 移除分隔线（---或===等）
        cmd = re.sub(r'-{3,}|={3,}', '', cmd)

        # 移除END标记
        cmd = re.sub(r'---\s*END\s*', '', cmd)

        # 替换\r\n为\n，统一换行符
        cmd = cmd.replace('\r\n', '\n')

        # 合并多余空行（保留最多两个连续空行）
        cmd = re.sub(r'\n{3,}', '\n\n', cmd)

        # 去除首尾空白
        data['cmdResult'] = cmd.strip()

    # 转换回JSON字符串（确保中文正常显示）
    return json.dumps(data, ensure_ascii=False, indent=2)


def clean_control_characters(text):
    """
    清理文本中的非法控制字符
    """
    # 使用正则表达式移除所有非法控制字符（保留常见空白字符）
    cleaned_text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    return cleaned_text


# 示例用法
if __name__ == "__main__":
    # 原始JSON数据
    raw_json = '''{
    "resultCode": 1,
    "resultMsg": "执行成功",
    "deviceType": null,
    "parserSate": 1,
    "parserResult": "最近一次小区状态变化的原因\t异常\n最近一次引起小区建立的操作时间\t异常\n最近一次引起小区建立的操作类型\t异常\n最近一次引起小区删除的操作时间\t异常\n最近一次引起小区删除的操作类型\t异常\n小区节能减排状态\t异常\n符号关断状态\t异常\n高铁场景下干扰协同状态\t异常\n主基带处理板信息\t异常\n小区拓扑结构\t异常\n最大发射功率(0.1dBm)\t异常\n小区PLMN信息\t异常\n小区从可用变为不可用时间\t异常\n小区变为不可用前最后一次配置操作时间\t异常\n",
    "parserContent": null,
    "cmdResult": "%%/1933920621/DSP CELL:;%%\r\nRETCODE = 0  执行成功\r\n\r\n查询小区动态参数\r\n----------------\r\n                        本地小区标识  =  1\r\n                            小区名称  =  南平延平上元-HHM-F9-64\r\n                      小区的实例状态  =  正常\r\n          最近一次小区状态变化的原因  =  小区建立成功\r\n      最近一次引起小区建立的操作时间  =  2025-10-30 23:27:40\r\n      最近一次引起小区建立的操作类型  =  小区健康检查\r\n      最近一次引起小区删除的操作时间  =  2025-10-30 23:27:37\r\n      最近一次引起小区删除的操作类型  =  小区建立失败\r\n                    小区节能减排状态  =  未启动\r\n                        符号关断状态  =  符号关断\r\n              高铁场景下干扰协同状态  =  未启动\r\n                    主基带处理板信息  =  0-0-3\r\n                        小区拓扑结构  =  基本模式\r\n                最大发射功率(0.1dBm)  =  460\r\n                        小区PLMN信息  =  460-00/460-15\r\n            小区从可用变为不可用时间  =  0000-00-00 00:00:00\r\n小区变为不可用前最后一次配置操作时间  =  0000-00-00 00:00:00\r\n(结果个数 = 1)\r\n\r\n小区使用的射频单元以及基带处理板信息\r\n------------------------------------\r\n基站标识  射频单元信息  发射通道号  接收通道号  服务基带处理板信息  工作状态  主控处理板信息  最大发射功率(0.1dBm)  小区发射通道功率偏置(0.1dB)  分布单元基站标识\r\n\r\n145010    0-90-0        R0A-R0B     R0A-R0B     0-0-3               正常      0-0-7           460                   65535                        -               \r\n(结果个数 = 1)\r\n\r\n\r\n---    END\r\n\r\n",
    "enodeb_id": "460-00-145010"
}'''
    print(clean_json(raw_json))
