"""
导入器基类 - 定义统一的导入接口
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from pathlib import Path


class BaseImporter(ABC):
    """数据导入器基类"""
    
    def __init__(self, source_path: str):
        """
        初始化导入器
        
        Args:
            source_path: 数据源文件路径
        """
        self.source_path = Path(source_path)
        self._validate_source()
    
    def _validate_source(self):
        """验证数据源是否存在"""
        if not self.source_path.exists():
            raise FileNotFoundError(f"数据源文件不存在: {self.source_path}")
    
    @abstractmethod
    def read_cases(self) -> List[Dict]:
        """
        读取用例数据
        
        Returns:
            用例列表
        """
        pass
    
    @abstractmethod
    def validate_format(self) -> bool:
        """
        验证数据格式
        
        Returns:
            格式是否正确
        """
        pass
    
    def get_case_count(self) -> int:
        """获取用例数量"""
        try:
            cases = self.read_cases()
            return len(cases)
        except:
            return 0
    
    def preview_cases(self, limit: int = 5) -> List[Dict]:
        """
        预览前N条用例
        
        Args:
            limit: 预览数量
        
        Returns:
            用例列表
        """
        cases = self.read_cases()
        return cases[:limit]
