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

    # 根据 Content-Type 自动选择参数格式
    request_kwargs = {
        'method': case['method'],
        'url': full_url,
        'headers': case['headers']
    }
    
    # 获取 Content-Type（不区分大小写）
    content_type = ''
    if case.get('headers'):
        # 查找 Content-Type（支持不同大小写）
        for key, value in case['headers'].items():
            if key.lower() == 'content-type':
                content_type = value.lower().strip()
                break
    
    # 如果没有指定 Content-Type，默认为 application/json
    if not content_type:
        content_type = 'application/json'
    
    request_data = case.get('request_data')
    
    # 根据 Content-Type 选择合适的参数格式
    if request_data:
        if 'application/json' in content_type:
            # JSON 格式：使用 json 参数，requests 会自动序列化
            request_kwargs['json'] = request_data
            logger.debug(f"使用 JSON 格式发送数据")
        elif 'application/x-www-form-urlencoded' in content_type:
            # Form 表单格式：使用 data 参数，requests 会自动编码为 form-urlencoded
            request_kwargs['data'] = request_data
            logger.debug(f"使用 Form URL-Encoded 格式发送数据")
        elif 'multipart/form-data' in content_type:
            # Multipart 表单格式：使用 data 参数
            request_kwargs['data'] = request_data
            # 注意：multipart/form-data 的 boundary 由 requests 自动生成
            # 需要从 headers 中移除 Content-Type，让 requests 自动设置
            if 'headers' in request_kwargs:
                request_kwargs['headers'] = {k: v for k, v in request_kwargs['headers'].items() 
                                            if k.lower() != 'content-type'}
            logger.debug(f"使用 Multipart Form-Data 格式发送数据（boundary 自动生成）")
        elif 'text/' in content_type or 'application/xml' in content_type:
            # 纯文本或 XML：使用 data 参数
            if isinstance(request_data, str):
                request_kwargs['data'] = request_data
            else:
                # 如果是字典，转为字符串（可能需要根据实际情况调整）
                logger.warning(f"Content-Type 为 {content_type}，但 request_data 是字典类型，将尝试转换")
                import json
                if 'xml' in content_type:
                    request_kwargs['data'] = str(request_data)
                else:
                    request_kwargs['data'] = json.dumps(request_data, ensure_ascii=False)
            logger.debug(f"使用文本/XML 格式发送数据")
        else:
            # 其他格式：默认使用 data 参数
            request_kwargs['data'] = request_data
            logger.debug(f"使用默认格式发送数据（Content-Type: {content_type}）")

    # 发送请求
    response = req_handler._send_request(**request_kwargs)

    # 使用logger输出响应信息
    logger.info(f"响应状态码: {response.status_code}")
    try:
        response_json = response.json()
        logger.info(f"响应内容: {response_json}")
    except Exception:
        logger.info(f"响应内容(非JSON): {response.text}")

    # 断言HTTP状态码
    assert_handler.assert_status_code(response, case['expected_http_code'])

    # 解析响应数据
    response_json = assert_handler.handle_json_parsing(response, case['expected_http_code'])
    if response_json is None:
        return

    # 断言响应体中的业务状态码
    if 'expected_res_code' in case:
        assert_handler.assert_response_code(response_json, case['expected_res_code'])

    # 断言响应内容
    # 遍历期望的响应内容进行断言
    if 'expected_response' in case and case['expected_response']:
        # 只有当期望响应不是空字典时才进行断言
        if case['expected_response'] != {}:
            assert_handler.assert_response_content(response_json, case['expected_response'], assert_handler)

    logger.info(f"测试用例 {case['case_id']} 执行成功")
