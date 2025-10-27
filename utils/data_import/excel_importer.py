"""
Excel导入器 - 支持从Excel导入测试用例
"""
import pandas as pd
import json
from typing import List, Dict, Optional
from .base_importer import BaseImporter


class ExcelImporter(BaseImporter):
    """Excel用例导入器"""
    
    REQUIRED_COLUMNS = [
        'case_id', 'description', 'method', 'url',
        'expected_http_code', 'expected_res_code'
    ]
    
    OPTIONAL_COLUMNS = [
        'headers', 'request_data', 'expected_response'
    ]
    
    def __init__(self, excel_path: str, sheet_name: str = 0):
        """
        初始化Excel导入器
        
        Args:
            excel_path: Excel文件路径
            sheet_name: 工作表名称或索引
        """
        super().__init__(excel_path)
        self.sheet_name = sheet_name
        self.df: Optional[pd.DataFrame] = None
    
    def validate_format(self) -> bool:
        """验证Excel格式"""
        try:
            df = pd.read_excel(self.source_path, sheet_name=self.sheet_name)
            
            # 检查必需列
            missing_cols = set(self.REQUIRED_COLUMNS) - set(df.columns)
            if missing_cols:
                print(f"❌ 缺少必需列: {missing_cols}")
                return False
            
            # 检查必需列是否有空值
            for col in self.REQUIRED_COLUMNS:
                if df[col].isnull().any():
                    print(f"❌ 列 '{col}' 存在空值")
                    return False
            
            return True
        except Exception as e:
            print(f"❌ Excel格式验证失败: {e}")
            return False
    
    def _parse_json_field(self, value) -> Dict:
        """解析JSON字符串字段"""
        if pd.isna(value) or value == '':
            return {}
        if isinstance(value, dict):
            return value
        try:
            return json.loads(str(value))
        except json.JSONDecodeError as e:
            print(f"⚠️  JSON解析失败: {value}, 错误: {e}")
            return {}
    
    def _convert_row_to_case(self, row: pd.Series) -> Optional[Dict]:
        """将Excel行转换为用例字典"""
        try:
            case = {
                'case_id': int(row['case_id']),
                'description': str(row['description']).strip(),
                'method': str(row['method']).upper().strip(),
                'url': str(row['url']).strip(),
                'expected_http_code': int(row['expected_http_code']),
                'expected_res_code': int(row['expected_res_code']),
            }
            
            # 处理可选字段
            if 'headers' in row and not pd.isna(row['headers']):
                case['headers'] = self._parse_json_field(row['headers'])
            
            if 'request_data' in row and not pd.isna(row['request_data']):
                case['request_data'] = self._parse_json_field(row['request_data'])
            
            if 'expected_response' in row and not pd.isna(row['expected_response']):
                case['expected_response'] = self._parse_json_field(row['expected_response'])
            
            return case
        except Exception as e:
            print(f"⚠️  行转换失败: {e}")
            return None
    
    def read_cases(self) -> List[Dict]:
        """读取Excel中的所有用例"""
        if self.df is None:
            self.df = pd.read_excel(self.source_path, sheet_name=self.sheet_name)
        
        cases = []
        for idx, row in self.df.iterrows():
            case = self._convert_row_to_case(row)
            if case:
                cases.append(case)
            else:
                print(f"⚠️  第 {idx + 2} 行数据无效,已跳过")
        
        return cases
    
    def get_statistics(self) -> Dict:
        """获取Excel统计信息"""
        if self.df is None:
            self.df = pd.read_excel(self.source_path, sheet_name=self.sheet_name)
        
        return {
            'total_rows': len(self.df),
            'case_ids': self.df['case_id'].tolist(),
            'methods': self.df['method'].value_counts().to_dict(),
            'has_headers': self.df['headers'].notna().sum(),
            'has_request_data': self.df['request_data'].notna().sum(),
        }
