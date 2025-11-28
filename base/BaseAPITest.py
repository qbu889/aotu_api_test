# base/test_base.py
import pytest
import os
from config.settings import BASE_URL, DATA_DIR
from utils.yaml_utils import YamlUtils
from base.logger import logger
from base.request import RequestBase
from base.assertion import Assertion


class BaseAPITest:
    """API测试基础类"""

    def __init__(self):
        self.base_url = BASE_URL
        self.data_dir = DATA_DIR
        self.logger = logger
        self.req_handler = RequestBase()
        self.assert_handler = Assertion()

    def load_test_data(self, yaml_file):
        """加载测试数据"""
        test_data_raw = YamlUtils.read_yaml(os.path.join(self.data_dir, yaml_file))
        # 过滤掉 None 值
        test_data_raw = [case for case in (test_data_raw or []) if case is not None]
        return test_data_raw

    def execute_api_test(self, case_raw):
        """执行API测试的核心逻辑"""
        # 处理动态数据
        case = YamlUtils.process_dynamic_data(case_raw)

        # 拼接完整URL
        full_url = f"{self.base_url}{case['url']}"

        # 记录测试信息
        self.logger.info(f"执行测试用例 {case['case_id']}: {case['description']}")
        self.logger.info(f"请求URL: {full_url}")
        self.logger.info(f"请求数据: {case.get('request_data', 'N/A')}")

        # 准备请求参数
        request_kwargs = self.req_handler.prepare_request_params(
            method=case['method'],
            url=full_url,
            headers=case['headers'],
            request_data=case.get('request_data')
        )

        # 发送请求
        response = self.req_handler._send_request(**request_kwargs)

        # 记录响应信息
        self.logger.info(f"响应状态码: {response.status_code}")
        try:
            response_json = response.json()
            self.logger.info(f"响应内容: {response_json}")
        except Exception:
            self.logger.info(f"响应内容(非JSON): {response.text}")

        # 执行断言
        self.assert_handler.assert_case(response, case)

        self.logger.info(f"测试用例 {case['case_id']} 执行成功")
        return response
