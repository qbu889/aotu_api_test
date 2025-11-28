import logging

import schedule
import time
import requests
import json
from datetime import datetime, timedelta


def call_api():
    """定时调用API的函数"""
    #url = "http://10.44.225.27:8020/order/order-basic-flow-services/mwOrderEventMapping/export/dataSync"
    url = "http://192.168.6.72:8082/order/order-basic-flow-services/mwOrderEventMapping/export/dataSync"

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Access-Token": "BBST959u6k_in2kdS6kWp4tjZ_8",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "IcanUserAccount": "admin",
        "Origin": "http://10.44.225.27:8020",
        "Referer": "http://10.44.225.27:8020/order/",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "roleCode": "admin"
    }

    # 动态计算时间范围（最近30天）
    end_time = datetime.now()
    start_time = end_time - timedelta(days=30)

    payload = {
        "mainNetsortOne": "工单管控",
        "sendStartTime": start_time.strftime("%Y-%m-%d %H:%M:%S"),
        "sendEndTime": end_time.strftime("%Y-%m-%d %H:%M:%S")
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
        if response.status_code == 200:
            print(f"[{datetime.now()}] API调用成功")
            return response.json()
        else:
            print(f"[{datetime.now()}] API调用失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"[{datetime.now()}] API调用异常: {e}")


# 设置每天凌晨2点执行
schedule.every().day.at("11:16").do(call_api)

# 保持程序运行
while True:
    schedule.run_pending()
    time.sleep(60)  # 每分钟检查一次
    logging.info("程序已运行")
