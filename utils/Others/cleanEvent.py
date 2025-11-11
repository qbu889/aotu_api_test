import json
def clean_data(fp_value,event_time):
    # 提供的原始信息
    fp_value = fp_value
    event_time = event_time
    active_status = "3"  # 保持不变

    # 处理日期格式：将"/"替换为"-"
    cleaned_time = event_time.replace("/", "-")
    # 确保月份和日期为两位数（如果有需要）
    date_part, time_part = cleaned_time.split(" ")
    year, month, day = date_part.split("-")
    cleaned_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
    cleaned_event_time = f"{cleaned_date} {time_part}"

    # 构建目标格式数据
    result = {
        "ACTIVE_STATUS": active_status,
        "EVENT_TIME": cleaned_event_time,
        "FP0_FP1_FP2_FP3": fp_value,
        "CFP0_CFP1_CFP2_CFP3": fp_value
    }

    return result


if __name__ == "__main__":
    fp_value = "2607625924_1378624078_2095215297_2178125287_2"
    event_time = "2025/11/10 16:38"
    cleaned_data = clean_data(fp_value, event_time)
    # 打印格式化的JSON结果
    print(json.dumps(cleaned_data, indent=2, ensure_ascii=False))
