import requests
from .logger import logger


class RequestBase:
    def __init__(self, base_url=None):
        self.base_url = base_url
        self.session = requests.Session()
        # 默认不强行设置 Content-Type，交由上层或 requests 决定：
        # - 使用 json= 时，requests 会自动设置 application/json
        # - multipart/form-data 的 boundary 需由 requests 自动生成
        # - form/text/xml 等根据调用方 headers 或请求体决定
        self.headers = {}

    def set_base_url(self, base_url):
        """设置基础URL"""
        self.base_url = base_url
        logger.info(f"已设置基础URL: {base_url}")

    def set_headers(self, headers):
        """设置请求头"""
        self.headers.update(headers)
        logger.info(f"已更新请求头: {headers}")

    def prepare_request_params(self, method, url, headers=None, request_data=None):
        """
        根据 Content-Type 自动准备请求参数
        :param method: 请求方法
        :param url: 请求URL
        :param headers: 请求头
        :param request_data: 请求数据
        :return: 准备好的请求参数字典
        """
        request_kwargs = {
            'method': method,
            'url': url,
            'headers': headers or {}
        }

        # 获取 Content-Type（不区分大小写）
        content_type = ''
        if headers:
            for key, value in headers.items():
                if key.lower() == 'content-type':
                    content_type = value.lower().strip()
                    break

        # 如果没有指定 Content-Type，默认为 application/json
        if not content_type:
            content_type = 'application/json'

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

        return request_kwargs

    def _send_request(self, method, url, **kwargs):
        """发送请求的内部方法"""
        # 拼接完整URL
        if self.base_url and not url.startswith('http'):
            full_url = f"{self.base_url.rstrip('/')}/{url.lstrip('/')}"
        else:
            full_url = url

        # 合并请求头，kwargs中的headers优先级更高
        headers = self.headers.copy()
        if 'headers' in kwargs:
            headers.update(kwargs.pop('headers'))

        # 记录请求信息
        logger.info(f"发送{method}请求: {full_url}")
        logger.debug(f"请求参数: {kwargs}")
        logger.debug(f"请求头: {headers}")

        try:
            # 发送请求
            response = self.session.request(
                method=method,
                url=full_url,
                headers=headers, **kwargs
            )

            # 记录响应信息
            logger.info(f"收到响应: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")

            return response

        except Exception as e:
            logger.error(f"请求发生错误: {str(e)}", exc_info=True)
            raise

    def get(self, url, params=None, **kwargs):
        """发送GET请求"""
        return self._send_request('GET', url, params=params, **kwargs)

    def post(self, url, data=None, json=None, **kwargs):
        """发送POST请求"""
        return self._send_request('POST', url, data=data, json=json, **kwargs)

    def put(self, url, data=None, json=None, **kwargs):
        """发送PUT请求"""
        return self._send_request('PUT', url, data=data, json=json, **kwargs)

    def delete(self, url, **kwargs):
        """发送DELETE请求"""
        return self._send_request('DELETE', url, **kwargs)

    def close(self):
        """关闭会话"""
        self.session.close()
        logger.info("已关闭请求会话")
