import pytest
import os

from config.settings import BASE_URL, DATA_DIR
from utils.yaml_utils import YamlUtils
from base.logger import logger

# 读取YAML测试数据
test_data_raw = YamlUtils.read_yaml(os.path.join(DATA_DIR, "test_cases.yaml"))

# 过滤掉 None 值（防止 YAML 文件末尾的空列表项导致错误）
test_data_raw = [case for case in (test_data_raw or []) if case is not None]


@pytest.mark.api
@pytest.mark.parametrize("case_raw", test_data_raw)
def test_create_user(case_raw):
    """测试用户创建接口"""
    # 每次测试都处理动态数据
    case = YamlUtils.process_dynamic_data(case_raw)

    # 初始化请求处理器和断言处理器
    from base.request import RequestBase
    from base.assertion import Assertion

    req_handler = RequestBase()
    assert_handler = Assertion()

    # 拼接完整URL
    full_url = f"{BASE_URL}{case['url']}"

    # 使用logger输出测试用例信息
    logger.info(f"执行测试用例 {case['case_id']}: {case['description']}")
    logger.info(f"请求URL: {full_url}")
    logger.info(f"请求数据: {case.get('request_data', 'N/A')}")

    # 准备请求参数（Content-Type 处理已封装到 RequestBase）
    request_kwargs = req_handler.prepare_request_params(
        method=case['method'],
        url=full_url,
        headers=case['headers'],
        request_data=case.get('request_data')
    )

    # 发送请求
    response = req_handler._send_request(**request_kwargs)

    # 使用logger输出响应信息
    logger.info(f"响应状态码: {response.status_code}")
    try:
        response_json = response.json()
        logger.info(f"响应内容: {response_json}")
    except Exception:
        logger.info(f"响应内容(非JSON): {response.text}")

    # 统一断言（所有断言逻辑已封装到 Assertion.assert_case）
    assert_handler.assert_case(response, case)

    logger.info(f"测试用例 {case['case_id']} 执行成功")
