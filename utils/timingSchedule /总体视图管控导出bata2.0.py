# TestCase/API/test_api.py
import pytest
import self

from base.BaseAPITest import BaseAPITest


class TestUserAPI(BaseAPITest):
    """用户相关API测试"""

    def __init__(self):
        super().__init__()
        # 加载测试数据
        self.test_data = self.load_test_data("test_cases.yaml")

    @pytest.mark.api
    @pytest.mark.parametrize("case_raw", self.test_data)
    def test_create_user(self, case_raw):
        """测试用户创建接口"""
        self.execute_api_test(case_raw)


# 如果需要更多的API测试类，可以继续继承
class TestOrderAPI(BaseAPITest):
    """订单相关API测试"""

    def __init__(self):
        super().__init__()
        # 可以加载不同的测试数据文件
        self.test_data = self.load_test_data("order_test_cases.yaml")
