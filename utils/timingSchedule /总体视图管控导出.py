import requests
import json
from datetime import datetime
import schedule
import time
from base.logger import logger


def export_data_sync(environment='dev', granularity_type=None, start_time=None, end_time=None, city=None,
                     send_start_time=None, send_end_time=None):
    """
    调用数据同步导出接口

    Args:
        environment (str): 环境类型，'dev' 或 'prod'
        granularity_type (str, optional): 粒度类型
        start_time (str, optional): 归档开始时间，格式 "YYYY-MM-DD HH:MM:SS"
        end_time (str, optional): 归档结束时间，格式 "YYYY-MM-DD HH:MM:SS"
        city (str, optional): 城市名称
        send_start_time (str, optional): 发送开始时间，格式 "YYYY-MM-DD HH:MM:SS"
        send_end_time (str, optional): 发送结束时间，格式 "YYYY-MM-DD HH:MM:SS"

    Returns:
        dict: 接口响应结果
    """

    # 环境配置
    env_config = {
        'dev': {
            'host': "http://192.168.6.72:8020",
            'token': 'X2LaSlaqpjQpZQD6yJqtuHw7Z0Y'
        },
        'prod': {
            'host': "http://10.44.225.27:8020",
            'token': 'BBST959u6k_in2kdS6kWp4tjZ_8'
        }
    }

    # 获取对应环境配置
    if environment not in env_config:
        logger.error(f"无效的环境配置: {environment}，必须是 'dev' 或 'prod'")
        raise ValueError("environment 必须是 'dev' 或 'prod'")

    config = env_config[environment]
    host = config['host']
    token = config['token']

    # 根据环境确定URL
    if environment == 'dev':
        url = f"{host}/order/order-basic-flow-services/mwOrderEventMapping/export/dataSync"
    else:  # prod
        url = f"{host}/order/order-basic-flow-services/totality/view/export/dataSync"

    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Access-Token': token,
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'IcanUserAccount': 'admin',
        'Origin': host,
        'Referer': host + '/order/',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
        'roleCode': 'admin'
    }

    # 构造请求数据
    payload = {}

    # 添加归档时间参数（如果提供）
    if granularity_type:
        payload["granularityType"] = granularity_type
    if start_time:
        payload["archivedStartTime"] = start_time
    if end_time:
        payload["archivedEndTime"] = end_time
    if city:
        payload["city"] = city

    # 添加发送时间参数（如果提供）
    if send_start_time:
        payload["sendStartTime"] = send_start_time
    if send_end_time:
        payload["sendEndTime"] = send_end_time

    # 记录请求日志
    logger.info(f"开始调用数据同步接口 - 环境: {environment}")
    logger.info(f"请求URL: {url}")
    logger.info(f"请求参数: {json.dumps(payload, ensure_ascii=False)}")

    try:
        response = requests.post(
            url=url,
            headers=headers,
            data=json.dumps(payload),
            timeout=30
        )

        # 检查响应状态
        response.raise_for_status()

        # 记录成功响应日志
        logger.info(f"接口调用成功 - 状态码: {response.status_code}")

        # 返回JSON响应
        result = response.json()
        logger.info(f"响应数据: {json.dumps(result, ensure_ascii=False)}")
        return result

    except requests.exceptions.RequestException as e:
        logger.error(f"请求失败: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"响应解析失败: {e}")
        return None
    except Exception as e:
        logger.error(f"未知错误: {e}")
        return None


def scheduled_data_sync():
    """定时任务执行的数据同步函数"""
    logger.info("开始执行定时数据同步任务")

    # 调用示例 - dev环境，使用发送时间参数
    result = export_data_sync(
        environment='dev',
        send_start_time="2025-10-01 00:00:00",
        send_end_time="2025-11-28 00:00:00"
    )

    if result:
        logger.info("定时任务执行成功")
    else:
        logger.error("定时任务执行失败")


def run_scheduled_tasks():
    """运行定时任务"""
    logger.info("启动定时任务调度器")

    # 设置定时任务 - 每天凌晨2点执行
    schedule.every().day.at("13:54").do(scheduled_data_sync)

    # 也可以设置其他时间间隔的任务
    # schedule.every(30).minutes.do(scheduled_data_sync)  # 每30分钟执行一次
    # schedule.every().hour.do(scheduled_data_sync)       # 每小时执行一次

    while True:
        schedule.run_pending()
        time.sleep(60)  # 每分钟检查一次是否有待执行的任务


# 使用示例
if __name__ == "__main__":
    # # 立即执行一次
    # logger.info("立即执行数据同步任务")
    # result = export_data_sync(
    #     environment='dev',
    #     send_start_time="2025-10-01 00:00:00",
    #     send_end_time="2025-11-28 00:00:00"
    # )
    #
    # if result:
    #     print("接口调用成功:")
    #     print(json.dumps(result, indent=2, ensure_ascii=False))
    # else:
    #     print("接口调用失败")

    # 如果需要启动定时任务，取消下面的注释
    run_scheduled_tasks()
