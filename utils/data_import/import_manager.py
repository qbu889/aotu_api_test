"""
导入管理器 - 统一管理各种数据源的导入
"""
from typing import List, Dict, Optional
from pathlib import Path
from .excel_importer import ExcelImporter
from .yaml_handler import YAMLHandler


class ImportManager:
    """导入管理器 - 统一入口"""
    
    def __init__(self, yaml_path: str = 'data/test_cases.yaml'):
        """
        初始化导入管理器
        
        Args:
            yaml_path: 目标YAML文件路径
        """
        self.yaml_handler = YAMLHandler(yaml_path)
    
    def import_from_excel(
        self,
        excel_path: str,
        strategy: str = 'skip',
        backup: bool = True,
        validate: bool = True
    ) -> Dict:
        """
        从Excel导入用例
        
        Args:
            excel_path: Excel文件路径
            strategy: 合并策略 ('skip', 'replace', 'append')
            backup: 是否备份原YAML文件
            validate: 是否验证Excel格式
        
        Returns:
            导入结果统计
        """
        result = {
            'success': False,
            'imported_count': 0,
            'total_count': 0,
            'skipped_count': 0,
            'errors': []
        }
        
        try:
            # 1. 创建Excel导入器
            importer = ExcelImporter(excel_path)
            
            # 2. 验证格式
            if validate and not importer.validate_format():
                result['errors'].append('Excel格式验证失败')
                return result
            
            # 3. 读取用例
            new_cases = importer.read_cases()
            result['total_count'] = len(new_cases)
            
            if not new_cases:
                result['errors'].append('没有读取到有效用例')
                return result
            
            # 4. 备份原文件
            if backup:
                backup_path = self.yaml_handler.backup()
                if backup_path:
                    print(f"已备份原文件: {backup_path}")
            
            # 5. 合并用例
            before_count = len(self.yaml_handler.read())
            merged_cases = self.yaml_handler.merge_cases(new_cases, strategy=strategy)
            after_count = len(merged_cases)
            
            # 6. 写入YAML
            self.yaml_handler.write(merged_cases)
            
            # 7. 统计结果
            result['success'] = True
            result['imported_count'] = after_count - before_count
            result['skipped_count'] = result['total_count'] - result['imported_count']
            
            return result
        
        except Exception as e:
            result['errors'].append(str(e))
            return result
    
    def batch_import_from_directory(
        self,
        directory: str,
        pattern: str = '*.xlsx',
        strategy: str = 'skip'
    ) -> Dict:
        """
        批量导入目录下的所有Excel文件
        
        Args:
            directory: 目录路径
            pattern: 文件匹配模式
            strategy: 合并策略
        
        Returns:
            批量导入结果
        """
        dir_path = Path(directory)
        
        if not dir_path.exists():
            return {
                'success': False,
                'errors': [f'目录不存在: {directory}']
            }
        
        excel_files = list(dir_path.glob(pattern))
        
        if not excel_files:
            return {
                'success': False,
                'errors': [f'未找到匹配的文件: {pattern}']
            }
        
        print(f"\n找到 {len(excel_files)} 个Excel文件:")
        for f in excel_files:
            print(f"  - {f.name}")
        
        total_imported = 0
        total_skipped = 0
        errors = []
        
        for excel_file in excel_files:
            print(f"\n导入: {excel_file.name}")
            result = self.import_from_excel(
                str(excel_file),
                strategy=strategy,
                backup=False  # 批量导入时只备份一次
            )
            
            if result['success']:
                total_imported += result['imported_count']
                total_skipped += result['skipped_count']
                print(f"成功导入 {result['imported_count']} 条用例")
            else:
                errors.extend(result['errors'])
                print(f"导入失败: {result['errors']}")
        
        return {
            'success': len(errors) == 0,
            'total_files': len(excel_files),
            'total_imported': total_imported,
            'total_skipped': total_skipped,
            'errors': errors
        }
    
    def get_yaml_info(self) -> Dict:
        """获取当前YAML文件信息"""
        return self.yaml_handler.get_statistics()
    
    def print_import_summary(self, result: Dict):
        """打印导入摘要"""
        print("\n" + "="*60)
        print("导入摘要")
        print("="*60)
        
        if result['success']:
            print(f"导入状态: 成功")
            if 'imported_count' in result:
                print(f"新增用例: {result['imported_count']} 条")
                print(f"跳过用例: {result['skipped_count']} 条")
                print(f"读取用例: {result['total_count']} 条")
            if 'total_files' in result:
                print(f"处理文件: {result['total_files']} 个")
                print(f"总新增: {result['total_imported']} 条")
                print(f"总跳过: {result['total_skipped']} 条")
        else:
            print(f"导入状态: 失败")
            for error in result['errors']:
                print(f"   {error}")
        
        print("="*60 + "\n")


def quick_import(
    excel_path: str,
    yaml_path: str = 'data/test_cases.yaml',
    strategy: str = 'skip'
) -> bool:
    """
    快速导入函数 - 简化调用
    
    Args:
        excel_path: Excel文件路径
        yaml_path: 目标YAML路径
        strategy: 合并策略
    
    Returns:
        是否成功
    """
    manager = ImportManager(yaml_path)
    result = manager.import_from_excel(excel_path, strategy=strategy)
    manager.print_import_summary(result)
    return result['success']
