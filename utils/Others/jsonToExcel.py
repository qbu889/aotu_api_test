import json
import pandas as pd

# 完整的字段映射字典：JSON字段名 -> 中文列名
column_mapping = {
    "ADD_EVENT_NUMBER": "追加事件流水号",
    "ASSIGNEE": "分派对象",
    "ASSIGN_TENANCE_GROUP": "分派维护组",
    "BUSINESS_LEVEL": "业务层级",
    "CC_LIST": "抄送对象",
    "CI": "CI",
    "CIRCUIT_LEVEL": "电路级别",
    "COMPLAINT_USER_NUM": "投诉用户数",
    "COPY_TENANCE_GROUP": "抄送维护组",
    "CREATE_TIME": "创建时间",
    "CREATOR": "创建人",
    "CURRENTLY_ALARM_FP": "告警指纹",
    "DEAL_CITY": "工单处理归属地市",
    "DEAL_COUNTY": "工单处理归属区县",
    "END_TIME": "归档时间",
    "EVENT_CLEAN_TIME": "事件清除时间",
    "EVENT_LABEL": "事件标签",
    "EVENT_NUMBER": "主事件流水号",
    "EXCEPTION_TIME": "入异常库时间",
    "FORCE_CLEAN_TIME": "强清时间",
    "GCSS_CLIENT_LEVEL": "集客客户级别",
    "GCSS_SERVICE_LEVEL": "集客业务级别",
    "HANDLE_MAINTENANCE_GROUP": "经办维护组",
    "IS_FIRST_DELAY": "是否延期",
    "IS_SPECIAL_HANDLING": "是否特殊处理工单",
    "LINK_EXCEPTION_LIBRARY_REASON_DESC": "异常原因",
    "LINK_ID": "流转表ID",
    "LINK_MERGERMAIN_ORDER_ID": "合并主单号",
    "LINK_MERGERSON_ORDER_ID": "合并子单号",
    "LINK_MERGERSON_ORDER_ID_1": "投诉工单号",
    "MAIN_ACCEPT_LIMIT_T1": "T1受理时限",
    "MAIN_ACCEPT_LIMIT_T2": "T2受理时限",
    "MAIN_ACCEPT_OVER_T1": "T1工单受理超时",
    "MAIN_ACCEPT_OVER_T2": "T2工单受理超时",
    "MAIN_ACCEPT_TIME_T1": "T1接单时间",
    "MAIN_ACCEPT_TIME_T2": "T2接单时间",
    "MAIN_CITY": "地市",
    "MAIN_COMPLETE_LIMIT_T1": "T1处理时限",
    "MAIN_COMPLETE_LIMIT_T2": "T2处理时限",
    "MAIN_COMPLETE_OVER_T1": "T1工单处理超时",
    "MAIN_COMPLETE_OVER_T2": "T2工单处理超时",
    "MAIN_COUNTY": "区县",
    "MAIN_FAULT_RESPONSE_LEVEL": "故障响应级别",
    "MAIN_MASTER_LABEL": "主子单标签",
    "MAIN_NETSORT_ONE": "网络一级分类",
    "MAIN_NETSORT_THREE": "网络三级分类",
    "MAIN_NETSORT_TWO": "网络二级分类",
    "MAIN_ORDER_LABEL": "工单标签",
    "MAIN_OVERTIME_LABEL": "工单超时标签",
    "MAIN_TENANCE_COMPANY": "代维公司",
    "MAIN_TENANCE_GROUP": "主派维护组",
    "MAIN_TENANCE_MODE": "维护方式",
    "MAIN_TENANCE_SHEET_ID": "投诉工单号",
    "OPERATE_LINK": "当前环节",
    "OPERATION": "当前操作",
    "ORDER_TYPE": "工单类型",
    "PROCESS_INSTANCE_ID": "流程实例ID",
    "PROVINCELEVEL": "省内派单级别",
    "PUBLIC_INCIDENT_ID": "事件ID",
    "ROOT_CAUSE_MAJOR": "根因专业",
    "ROOT_CAUSE_NE_NAME": "根因网元",
    "SEND_TIME": "派单时间",
    "SEND_USER_ID": "派单人id",
    "SEND_USER_NAME": "派单人名称",
    "SHEET_ACCEPT_LIMIT": "故障受理时限",
    "SHEET_COMPLETE_LIMIT": "故障处理时限",
    "SHEET_ID": "工单编号",
    "SPECIAL_HANDLING_REASON": "特殊处理原因",
    "STATUS": "工单状态",
    "T1_PROCESSING_TIME": "T1处理时间",
    "T2_PROCESSING_TIME": "T2处理时间",
    "TASK_ID": "任务ID",
    "TITLE": "工单主题",
    "TITLE_TO": "工单自定义主题",
    "TO_ORG_ROLE": "派发对象",
    "TRIGGER_MAJOR": "触发专业",
    "TRIGGER_NE_NAME": "触发网元",
    "UPDATE_TIME": "数据更新时间",
    "WIRELESS_SITE_TYPE": "无线站点类型",
    "WORK_ORDER_WAY": "派单方式",
    "WO_ID": "工单编号"
}

# 读取 JSON 文件
with open("/Users/linziwang/PycharmProjects/aotu_api_test/resource/遗留库查询.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# 提取 records
records = data.get("data", {}).get("records", [])

if not records:
    raise ValueError("未找到 records 数据，请检查 JSON 结构")

# 按照JSON中实际出现的字段顺序来处理
if records:
    actual_fields = list(records[0].keys())
else:
    raise ValueError("records为空，无法确定字段顺序")

# 创建按实际顺序排列的映射
ordered_mapping = {field: column_mapping.get(field, field) for field in actual_fields}

# 构建 DataFrame
rows = []
for record in records:
    row = []
    for field in actual_fields:
        value = record.get(field, None)
        # 特别处理 LINK_MERGERSON_ORDER_ID：可能是 JSON 字符串，可选解析为字符串摘要
        if field == "LINK_MERGERSON_ORDER_ID" and isinstance(value, str):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    # 提取所有 eventNumber 并拼接
                    nums = [item.get("eventNumber") for item in parsed if item.get("eventNumber")]
                    value = ",".join(map(str, nums)) if nums else None
            except:
                pass  # 保留原值
        row.append(value)
    rows.append(row)

# 使用中文列名
chinese_column_names = [ordered_mapping[field] for field in actual_fields]
df = pd.DataFrame(rows, columns=chinese_column_names)

# 导出为 Excel
output_file = "遗留库工单.xlsx"
df.to_excel(output_file, index=False)

print(f"✅ 已成功导出 {len(records)} 条记录到 '{output_file}'，列顺序按照JSON数据中字段的实际顺序")
