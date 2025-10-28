"""
检查Excel中的JSON格式错误 - 详细版
"""
# 终端输入：python scripts/check_excel_json.py
# 运行这个脚本进行格式检查的时候要注意：
# 该脚本只会读取excel_cases文件夹下的test_case文件，用例文件统一叫这个名字才可以生效
import pandas as pd
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class ExcelJsonChecker:
    """Excel JSON格式检查器 - 支持多种 Content-Type"""
    
    REQUIRED_COLUMNS = [
        'case_id', 'description', 'method', 'url',
        'expected_http_code', 'expected_res_code'
    ]
    
    JSON_COLUMNS = ['headers', 'request_data', 'expected_response']
    
    # 支持的 Content-Type
    CONTENT_TYPES = {
        'json': 'application/json',
        'form': 'application/x-www-form-urlencoded',
        'multipart': 'multipart/form-data',
        'xml': 'application/xml',
        'text': 'text/plain'
    }
    
    def __init__(self, excel_path: str):
        self.excel_path = excel_path
        self.df = None
        self.errors = []
        self.warnings = []
        
    def load_excel(self) -> bool:
        """加载Excel文件"""
        try:
            self.df = pd.read_excel(self.excel_path, sheet_name=0)
            return True
        except Exception as e:
            print(f"[ERROR] 读取Excel失败: {e}")
            return False
    
    def check_columns(self) -> bool:
        """检查必需列是否存在"""
        missing_cols = set(self.REQUIRED_COLUMNS) - set(self.df.columns)
        if missing_cols:
            self.errors.append(f"缺少必需列: {', '.join(missing_cols)}")
            return False
        return True
    
    def check_empty_required_fields(self):
        """检查必需字段是否有空值"""
        for col in self.REQUIRED_COLUMNS:
            null_rows = self.df[self.df[col].isnull()].index.tolist()
            if null_rows:
                excel_rows = [r + 2 for r in null_rows]  # +2 因为Excel从1开始且有表头
                self.errors.append(f"列 '{col}' 在第 {excel_rows} 行存在空值")
    
    def parse_json_with_detail(self, value: str, field_name: str, row_num: int, content_type: str = '') -> Tuple[bool, str, str]:
        """
        详细解析数据并根据 Content-Type 验证格式
        Args:
            value: 字段值
            field_name: 字段名
            row_num: 行号
            content_type: Content-Type 类型
        """
        if pd.isna(value) or value == '':
            return True, "", ""
        
        original = str(value).strip()
        
        # 检查是否是字符串类型
        if not isinstance(value, str):
            return False, f"类型错误: 应为字符串，实际为 {type(value).__name__}", original
        
        # headers 和 expected_response 必须是 JSON 格式
        if field_name in ['headers', 'expected_response']:
            return self._validate_json_format(value, original)
        
        # request_data 根据 Content-Type 验证
        if field_name == 'request_data':
            return self._validate_request_data(value, original, content_type)
        
        return True, "", original
    
    def _validate_json_format(self, value: str, original: str) -> Tuple[bool, str, str]:
        """验证 JSON 格式"""
        try:
            parsed = json.loads(value)
            return True, "", original
        except json.JSONDecodeError as e:
            error_detail = self._analyze_json_error(value, e)
            return False, error_detail, original
    
    def _validate_request_data(self, value: str, original: str, content_type: str) -> Tuple[bool, str, str]:
        """
        根据 Content-Type 验证 request_data 格式
        
        支持的格式:
        1. application/json - 必须是有效的 JSON
        2. application/x-www-form-urlencoded - 必须是有效的 JSON (会被转换为表单)
        3. multipart/form-data - 必须是有效的 JSON (会被转换为 multipart)
        4. application/xml - 可以是字符串或 JSON
        5. text/* - 可以是任意字符串
        """
        ct_lower = content_type.lower()
        
        # JSON 格式 - 严格要求 JSON
        if 'application/json' in ct_lower:
            return self._validate_json_format(value, original)
        
        # Form 和 Multipart 格式 - 要求 JSON (框架会自动转换)
        elif 'application/x-www-form-urlencoded' in ct_lower or 'multipart/form-data' in ct_lower:
            is_valid, error_msg, _ = self._validate_json_format(value, original)
            if not is_valid:
                error_msg += "\n      说明: Form/Multipart 格式的 request_data 需要用 JSON 表示，框架会自动转换"
            return is_valid, error_msg, original
        
        # XML 格式 - 可以是 JSON 或纯字符串
        elif 'application/xml' in ct_lower or 'text/xml' in ct_lower:
            # 先尝试作为 JSON 解析
            try:
                json.loads(value)
                return True, "", original
            except json.JSONDecodeError:
                # 如果不是 JSON，作为纯文本也是有效的
                return True, "", original
        
        # 纯文本格式 - 任意字符串都可以
        elif 'text/' in ct_lower:
            return True, "", original
        
        # 默认情况 - 尝试作为 JSON 解析
        else:
            try:
                json.loads(value)
                return True, "", original
            except json.JSONDecodeError:
                # 如果不是 JSON，给出警告但不算错误
                warning = f"Content-Type 为 '{content_type}'，数据不是有效 JSON，将作为字符串处理"
                return True, warning, original
    
    def _analyze_json_error(self, value: str, error: json.JSONDecodeError) -> str:
        """分析JSON错误并给出详细说明"""
        msg = error.msg
        line = error.lineno
        col = error.colno
        
        # 获取错误位置附近的内容
        lines = value.split('\n')
        if line <= len(lines):
            error_line = lines[line - 1]
            start = max(0, col - 20)
            end = min(len(error_line), col + 20)
            context = error_line[start:end]
            
            # 标记错误位置
            marker_pos = min(col - start, len(context))
            marker = ' ' * marker_pos + '^'
            
            error_detail = f"{msg}\n"
            error_detail += f"      位置: 第{line}行第{col}列\n"
            error_detail += f"      上下文: ...{context}...\n"
            error_detail += f"              {marker}\n"
            
            # 根据错误类型给出修复建议
            if "Unterminated string" in msg:
                error_detail += "      建议: 字符串缺少结束引号，请检查是否有未闭合的引号"
            elif "Expecting ',' delimiter" in msg:
                error_detail += "      建议: 缺少逗号分隔符，检查键值对之间是否有逗号"
            elif "Expecting ':' delimiter" in msg:
                error_detail += "      建议: 缺少冒号分隔符，检查键和值之间是否有冒号"
            elif "Expecting property name" in msg:
                error_detail += "      建议: 属性名缺少双引号，JSON中所有键必须用双引号包围"
            elif "Expecting value" in msg:
                error_detail += "      建议: 缺少值，检查冒号后面是否有对应的值"
            elif "Extra data" in msg:
                error_detail += "      建议: 存在多余数据，检查是否有多余的字符或未闭合的括号"
            
            return error_detail
        else:
            return f"{msg} (位置: 第{line}行第{col}列)"
    
    def check_all_rows(self):
        """检查所有行的JSON格式"""
        print("\n" + "=" * 80)
        print("开始逐行检查数据格式（支持多种 Content-Type）...")
        print("=" * 80)
        
        error_count = 0
        success_count = 0
        warning_count = 0
        
        for idx, row in self.df.iterrows():
            excel_row = idx + 2  # Excel行号（包含表头）
            case_id = row.get('case_id', 'N/A')
            description = row.get('description', 'N/A')
            method = row.get('method', 'N/A')
            
            row_has_error = False
            row_has_warning = False
            row_errors = []
            row_warnings = []
            
            # 解析 headers 获取 Content-Type
            content_type = 'application/json'  # 默认
            if 'headers' in self.df.columns and pd.notna(row['headers']):
                try:
                    headers = json.loads(row['headers'])
                    # 查找 Content-Type（不区分大小写）
                    for key, value in headers.items():
                        if key.lower() == 'content-type':
                            content_type = value
                            break
                except:
                    pass
            
            # 检查每个字段
            for col in self.JSON_COLUMNS:
                if col in self.df.columns:
                    value = row[col]
                    is_valid, error_msg, original = self.parse_json_with_detail(
                        value, col, excel_row, content_type
                    )
                    
                    if not is_valid:
                        row_has_error = True
                        row_errors.append({
                            'field': col,
                            'error': error_msg,
                            'original': original[:100] + ('...' if len(original) > 100 else '')
                        })
                    elif error_msg:  # 有警告信息
                        row_has_warning = True
                        row_warnings.append({
                            'field': col,
                            'warning': error_msg,
                            'original': original[:100] + ('...' if len(original) > 100 else '')
                        })
            
            # 输出结果
            if row_has_error:
                error_count += 1
                print(f"\n[X] 第 {excel_row} 行错误 (case_id={case_id})")
                print(f"   描述: {description}")
                print(f"   方法: {method} | Content-Type: {content_type}")
                print("-" * 80)
                
                for err in row_errors:
                    print(f"   【{err['field']}】字段:")
                    print(f"      原始值: {err['original']}")
                    print(f"      错误: {err['error']}")
                    print()
            elif row_has_warning:
                warning_count += 1
                print(f"\n[!] 第 {excel_row} 行警告 (case_id={case_id})")
                print(f"   描述: {description}")
                print(f"   方法: {method} | Content-Type: {content_type}")
                print("-" * 80)
                
                for warn in row_warnings:
                    print(f"   【{warn['field']}】字段:")
                    print(f"      原始值: {warn['original']}")
                    print(f"      警告: {warn['warning']}")
                    print()
            else:
                success_count += 1
                # 显示 Content-Type 信息
                ct_display = content_type if content_type != 'application/json' else 'JSON'
                print(f"[OK] 第 {excel_row} 行 (case_id={case_id}) [{ct_display}] - 格式正确")
        
        return error_count, success_count, warning_count
    
    def check_data_validity(self):
        """检查数据有效性（非JSON格式问题）"""
        print("\n" + "=" * 80)
        print("检查数据有效性...")
        print("=" * 80 + "\n")
        
        # 检查HTTP方法是否有效
        valid_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']
        for idx, row in self.df.iterrows():
            method = str(row.get('method', '')).upper().strip()
            if method and method not in valid_methods:
                self.warnings.append(
                    f"第 {idx + 2} 行: HTTP方法 '{method}' 可能无效，常见方法: {', '.join(valid_methods)}"
                )
        
        # 检查URL格式
        for idx, row in self.df.iterrows():
            url = str(row.get('url', '')).strip()
            if url and not (url.startswith('http://') or url.startswith('https://') or url.startswith('/')):
                self.warnings.append(
                    f"第 {idx + 2} 行: URL '{url}' 格式可能有误，建议以 http://, https:// 或 / 开头"
                )
        
        # 检查状态码范围
        for idx, row in self.df.iterrows():
            http_code = row.get('expected_http_code')
            if pd.notna(http_code):
                try:
                    code = int(http_code)
                    if code < 100 or code > 599:
                        self.warnings.append(
                            f"第 {idx + 2} 行: HTTP状态码 {code} 超出有效范围 (100-599)"
                        )
                except (ValueError, TypeError):
                    self.warnings.append(
                        f"第 {idx + 2} 行: HTTP状态码 '{http_code}' 不是有效数字"
                    )
    
    def generate_report(self, error_count: int, success_count: int, warning_count: int = 0):
        """生成检查报告"""
        print("\n" + "=" * 80)
        print("检查报告汇总")
        print("=" * 80)
        
        total = len(self.df)
        print(f"\n[统计信息]")
        print(f"   总行数: {total}")
        print(f"   [OK] 正确: {success_count} ({success_count/total*100:.1f}%)")
        if warning_count > 0:
            print(f"   [!] 警告: {warning_count} ({warning_count/total*100:.1f}%)")
        print(f"   [X] 错误: {error_count} ({error_count/total*100:.1f}%)")
        
        if self.errors:
            print(f"\n[严重错误] ({len(self.errors)}):")
            for i, err in enumerate(self.errors, 1):
                print(f"   {i}. {err}")
        
        if self.warnings:
            print(f"\n[警告信息] ({len(self.warnings)}):")
            for i, warn in enumerate(self.warnings, 1):
                print(f"   {i}. {warn}")
        
        print("\n" + "=" * 80)
        
        if error_count == 0 and len(self.errors) == 0:
            print("[SUCCESS] 恭喜！所有检查通过，Excel文件格式正确！")
            if warning_count > 0:
                print("[WARNING] 但有一些警告信息，建议查看")
        else:
            print("[FAIL] 发现问题，请根据上述错误信息修复Excel文件")
        
        print("=" * 80)
        
        return error_count == 0 and len(self.errors) == 0
    
    def run_full_check(self) -> bool:
        """运行完整检查流程"""
        print("=" * 80)
        print("Excel 数据格式检查工具 (支持多种 Content-Type)")
        print("=" * 80)
        print(f"\n[*] 文件路径: {self.excel_path}")
        
        # 1. 加载Excel
        if not self.load_excel():
            return False
        
        print(f"[OK] Excel加载成功")
        print(f"   行数: {len(self.df)}")
        print(f"   列数: {len(self.df.columns)}")
        print(f"   列名: {', '.join(self.df.columns.tolist())}")
        
        # 2. 检查列结构
        if not self.check_columns():
            print("\n[ERROR] 列结构检查失败")
            self.generate_report(0, 0, 0)
            return False
        
        # 3. 检查必需字段
        self.check_empty_required_fields()
        
        # 4. 检查数据格式（根据 Content-Type）
        error_count, success_count, warning_count = self.check_all_rows()
        
        # 5. 检查数据有效性
        self.check_data_validity()
        
        # 6. 生成报告
        return self.generate_report(error_count, success_count, warning_count)


def main():
    """主函数"""
    excel_path = project_root / 'data' / 'excel_cases' / 'test_case.xlsx'
    
    if not excel_path.exists():
        print(f"[ERROR] 文件不存在: {excel_path}")
        return False
    
    checker = ExcelJsonChecker(str(excel_path))
    result = checker.run_full_check()
    
    return result


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
