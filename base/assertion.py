from .logger import logger
import pytest


class Assertion:
    @staticmethod
    def assert_equal(actual, expected, message="值不相等"):
        """断言两个值相等"""
        try:
            assert actual == expected, f"{message} - 实际值: {actual}, 期望值: {expected}"
            logger.info(f"断言成功: {actual} == {expected}")
            return True
        except AssertionError as e:
            logger.error(f"断言失败: {str(e)}")
            raise

    @staticmethod
    def assert_not_equal(actual, expected, message="值相等"):
        """断言两个值不相等"""
        try:
            assert actual != expected, f"{message} - 实际值: {actual}, 期望值: {expected}"
            logger.info(f"断言成功: {actual} != {expected}")
            return True
        except AssertionError as e:
            logger.error(f"断言失败: {str(e)}")
            raise

    @staticmethod
    def assert_in(actual, expected, message="实际值不在期望值中"):
        """断言实际值在期望值中"""
        try:
            assert actual in expected, f"{message} - 实际值: {actual}, 期望值: {expected}"
            logger.info(f"断言成功: {actual} 在 {expected} 中")
            return True
        except AssertionError as e:
            logger.error(f"断言失败: {str(e)}")
            raise

    @staticmethod
    def assert_not_in(actual, expected, message="实际值在期望值中"):
        """断言实际值不在期望值中"""
        try:
            assert actual not in expected, f"{message} - 实际值: {actual}, 期望值: {expected}"
            logger.info(f"断言成功: {actual} 不在 {expected} 中")
            return True
        except AssertionError as e:
            logger.error(f"断言失败: {str(e)}")
            raise

    @staticmethod
    def assert_status_code(response, expected_code, message="状态码不匹配"):
        """断言响应状态码"""
        try:
            assert response.status_code == expected_code, \
                f"{message} - 实际状态码: {response.status_code}, 期望状态码: {expected_code}"
            logger.info(f"状态码断言成功: {response.status_code} == {expected_code}")
            return True
        except AssertionError as e:
            logger.error(f"状态码断言失败: {str(e)}")
            raise

    @staticmethod
    def assert_json_key_exists(response_json, key, message="JSON中不存在指定键"):
        """断言JSON响应中存在指定键"""
        try:
            assert key in response_json, f"{message} - 键: {key}"
            logger.info(f"JSON键存在断言成功: {key} 在响应中存在")
            return True
        except AssertionError as e:
            logger.error(f"JSON键存在断言失败: {str(e)}")
            raise

    @staticmethod
    def assert_json_value(response_json, key, expected_value, message="JSON值不匹配"):
        """断言JSON响应中指定键的值"""
        try:
            # 如果期望值为空字典，则只检查键是否存在
            if expected_value == {}:
                Assertion.assert_json_key_exists(response_json, key)
                return True

            Assertion.assert_json_key_exists(response_json, key)
            actual_value = response_json[key]

            # 如果期望值是字典类型，则递归检查
            if isinstance(expected_value, dict) and isinstance(actual_value, dict):
                for k, v in expected_value.items():
                    if k in actual_value:
                        Assertion.assert_equal(actual_value[k], v, f"{message} - 键 {k}")
                    else:
                        raise AssertionError(f"{message} - 键 {k} 不存在于响应中")
            else:
                Assertion.assert_equal(actual_value, expected_value, message)
            return True
        except AssertionError as e:
            logger.error(f"JSON值断言失败: {str(e)}")
            raise

    @staticmethod
    def assert_response_code(response_json, expected_code, message="响应业务码不匹配"):
        """断言响应体中的业务状态码"""
        try:
            Assertion.assert_json_key_exists(response_json, 'code')
            actual_code = response_json['code']
            assert actual_code == expected_code, \
                f"{message} - 实际业务码: {actual_code}, 期望业务码: {expected_code}"
            logger.info(f"响应业务码断言成功: {actual_code} == {expected_code}")
            return True
        except AssertionError as e:
            logger.error(f"响应业务码断言失败: {str(e)}")
            raise

    @staticmethod
    def assert_response_content(response_json, expected_response, assert_handler):
        """
        递归断言响应内容
        :param response_json: 实际响应JSON
        :param expected_response: 期望响应内容
        :param assert_handler: 断言处理器
        """
        for key, expected_value in expected_response.items():
            # 处理嵌套字典的情况
            if isinstance(expected_value, dict):
                # 确保键存在且值是字典
                assert_handler.assert_json_key_exists(response_json, key)
                actual_value = response_json[key]
                if isinstance(actual_value, dict):
                    # 递归处理嵌套字典
                    Assertion.assert_response_content(actual_value, expected_value, assert_handler)
                else:
                    pytest.fail(f"期望键 {key} 的值是字典，但实际值是 {type(actual_value)}: {actual_value}")
            else:
                # 处理普通键值对
                assert_handler.assert_json_value(response_json, key, expected_value)

    @staticmethod
    def handle_json_parsing(response, expected_http_code):
        """
        处理解析JSON响应的逻辑
        :param response: HTTP响应对象
        :param expected_http_code: 期望的HTTP状态码
        :return: 解析后的JSON对象或None
        """
        try:
            response_json = response.json()
            return response_json
        except Exception as e:
            # 如果期望状态码不是2xx，且无法解析JSON，则可能是服务器错误
            if expected_http_code < 200 or expected_http_code >= 300:
                print(f"警告: 状态码 {response.status_code} 的响应不是有效的JSON格式")
                return None
            else:
                pytest.fail(f"响应解析JSON失败: {str(e)}")

    @staticmethod
    def assert_case(response, case):
        """
        聚合断言方法：统一执行测试用例的所有断言
        :param response: HTTP响应对象
        :param case: 测试用例字典，包含所有期望值
        """
        # 1. 断言HTTP状态码
        Assertion.assert_status_code(response, case['expected_http_code'])

        # 2. 解析响应数据
        response_json = Assertion.handle_json_parsing(response, case['expected_http_code'])
        if response_json is None:
            return

        # 3. 断言响应体中的业务状态码
        if 'expected_res_code' in case:
            Assertion.assert_response_code(response_json, case['expected_res_code'])

        # 4. 断言响应内容
        if 'expected_response' in case and case['expected_response']:
            # 只有当期望响应不是空字典时才进行断言
            if case['expected_response'] != {}:
                # 创建一个临时的 Assertion 实例用于递归调用
                assert_handler = Assertion()
                Assertion.assert_response_content(response_json, case['expected_response'], assert_handler)
