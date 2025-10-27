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
