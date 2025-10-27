"""
YAML处理器 - 处理YAML测试用例文件
"""
import yaml
from typing import List, Dict, Optional
from pathlib import Path


class YAMLHandler:
    """YAML文件处理器"""
    
    def __init__(self, yaml_path: str):
        """
        初始化YAML处理器
        
        Args:
            yaml_path: YAML文件路径
        """
        self.yaml_path = Path(yaml_path)
        self._ensure_directory()
    
    def _ensure_directory(self):
        """确保YAML文件所在目录存在"""
        self.yaml_path.parent.mkdir(parents=True, exist_ok=True)
    
    def read(self) -> List[Dict]:
        """读取YAML文件"""
        if not self.yaml_path.exists():
            return []
        
        try:
            with open(self.yaml_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                return data if data else []
        except Exception as e:
            print(f"❌ 读取YAML失败: {e}")
            return []
    
    def write(self, cases: List[Dict]):
        """写入YAML文件"""
        try:
            with open(self.yaml_path, 'w', encoding='utf-8') as f:
                yaml.dump(
                    cases, f,
                    allow_unicode=True,
                    default_flow_style=False,
                    sort_keys=False,
                    indent=2
                )
        except Exception as e:
            print(f"❌ 写入YAML失败: {e}")
            raise
    
    def merge_cases(self, new_cases: List[Dict], strategy: str = 'skip') -> List[Dict]:
        """
        合并用例
        
        Args:
            new_cases: 新用例列表
            strategy: 合并策略
                - 'skip': 跳过重复ID的用例
                - 'replace': 用新用例替换旧用例
                - 'append': 直接追加所有新用例
        
        Returns:
            合并后的用例列表
        """
        existing_cases = self.read()
        
        if strategy == 'append':
            return existing_cases + new_cases
        
        # 建立ID索引
        existing_dict = {case['case_id']: case for case in existing_cases}
        new_dict = {case['case_id']: case for case in new_cases}
        
        if strategy == 'skip':
            # 跳过已存在的ID
            for case_id, case in new_dict.items():
                if case_id not in existing_dict:
                    existing_dict[case_id] = case
        
        elif strategy == 'replace':
            # 替换已存在的ID
            existing_dict.update(new_dict)
        
        # 按case_id排序
        return sorted(existing_dict.values(), key=lambda x: x['case_id'])
    
    def backup(self, suffix: str = None) -> Optional[Path]:
        """
        备份当前YAML文件
        
        Args:
            suffix: 备份文件后缀
        
        Returns:
            备份文件路径
        """
        if not self.yaml_path.exists():
            return None
        
        if suffix is None:
            from datetime import datetime
            suffix = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        backup_path = self.yaml_path.with_suffix(f'.{suffix}.yaml.bak')
        
        import shutil
        shutil.copy2(self.yaml_path, backup_path)
        
        return backup_path
    
    def get_case_by_id(self, case_id: int) -> Optional[Dict]:
        """根据ID获取用例"""
        cases = self.read()
        for case in cases:
            if case.get('case_id') == case_id:
                return case
        return None
    
    def get_statistics(self) -> Dict:
        """获取YAML统计信息"""
        cases = self.read()
        
        if not cases:
            return {
                'total_cases': 0,
                'case_ids': [],
                'methods': {},
            }
        
        from collections import Counter
        
        return {
            'total_cases': len(cases),
            'case_ids': [c['case_id'] for c in cases],
            'methods': dict(Counter(c['method'] for c in cases)),
            'min_case_id': min(c['case_id'] for c in cases),
            'max_case_id': max(c['case_id'] for c in cases),
        }
