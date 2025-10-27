import logging
import os
import sys
from datetime import datetime

# 自定义UTF-8输出类
class UTF8StreamHandler(logging.StreamHandler):
    def emit(self, record):
        try:
            msg = self.format(record)
            # 强制使用UTF-8编码输出
            if sys.platform.startswith('win'):
                # Windows下直接写入bytes
                msg_bytes = (msg + '\n').encode('utf-8', errors='replace')
                sys.stdout.buffer.write(msg_bytes)
                sys.stdout.buffer.flush()
            else:
                # 非Windows系统正常输出
                print(msg)
        except Exception:
            self.handleError(record)

# Windows 环境下设置环境变量
if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'


class Logger:
    def __init__(self, name=__name__):
        # 创建日志器
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # 确保日志目录存在
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # 日志文件名（Windows不支持冒号，使用连字符替代）
        now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        log_file = os.path.join(log_dir, f'test_{now}.log')

        # 避免重复添加处理器
        if not self.logger.handlers:
            # 创建文件处理器 - 指定UTF-8编码
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)

            # 创建自定义控制台处理器
            console_handler = UTF8StreamHandler()
            console_handler.setLevel(logging.INFO)

            # 定义日志格式
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)

            # 添加处理器到日志器
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

    def get_logger(self):
        return self.logger


# 实例化日志对象，供全局使用
logger = Logger().get_logger()
