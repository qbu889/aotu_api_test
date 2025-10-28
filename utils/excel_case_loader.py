"""
Excel用例加载器模块

职责:
- 检测Excel用例文件
- 格式验证 (集成 ExcelJsonChecker)
- 提供交互式导入功能
- 处理导入策略选择
- 提供导入结果反馈
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List


class ExcelCaseLoader:
    """Excel用例加载器"""
    
    def __init__(self, excel_dir: str = 'data/excel_cases', yaml_file: str = 'data/test_cases.yaml'):
        """
        初始化加载器
        
        Args:
            excel_dir: Excel文件目录路径
            yaml_file: 目标YAML文件路径
        """
        # 获取当前文件所在目录的上上级目录（项目根目录）
        current_file = Path(__file__)
        project_root = current_file.parent.parent
        
        # 如果是相对路径，转换为绝对路径
        if not Path(excel_dir).is_absolute():
            self.excel_dir = project_root / excel_dir
        else:
            self.excel_dir = Path(excel_dir)
        
        if not Path(yaml_file).is_absolute():
            self.yaml_file = str(project_root / yaml_file)
        else:
            self.yaml_file = yaml_file
            
        self.strategy_map = {
            '1': 'skip',
            '2': 'replace',
            '3': 'append'
        }
    
    def has_excel_files(self) -> bool:
        """
        检查是否存在Excel文件
        
        Returns:
            bool: 如果存在Excel文件返回True,否则返回False
        """
        if not self.excel_dir.exists():
            return False
        
        excel_files = list(self.excel_dir.glob('*.xlsx'))
        return len(excel_files) > 0
    
    def get_excel_files(self) -> list:
        """
        获取所有Excel文件
        
        Returns:
            list: Excel文件列表
        """
        if not self.excel_dir.exists():
            return []
        
        return list(self.excel_dir.glob('*.xlsx'))
    
    def validate_excel_files(self) -> Dict[str, Any]:
        """
        验证所有Excel文件的格式
        
        Returns:
            Dict: 验证结果
                {
                    'all_valid': bool,
                    'results': List[Dict],  # 每个文件的验证结果
                    'valid_files': List[Path],
                    'invalid_files': List[Path]
                }
        """
        excel_files = self.get_excel_files()
        
        if not excel_files:
            return {
                'all_valid': True,
                'results': [],
                'valid_files': [],
                'invalid_files': []
            }
        
        print("\n" + "="*60)
        print("📋 开始 Excel 格式验证...")
        print("="*60)
        
        valid_files = []
        invalid_files = []
        results = []
        
        for excel_file in excel_files:
            print(f"\n正在检查: {excel_file.name}")
            print("-" * 60)
            
            try:
                # 导入 ExcelJsonChecker
                from scripts.check_excel_json import ExcelJsonChecker
                
                # 创建检查器并运行检查
                checker = ExcelJsonChecker(str(excel_file))
                is_valid = checker.run_full_check()
                
                result = {
                    'file': excel_file,
                    'valid': is_valid,
                    'errors': checker.errors,
                    'warnings': checker.warnings
                }
                
                results.append(result)
                
                if is_valid:
                    valid_files.append(excel_file)
                    print(f"✅ {excel_file.name} - 格式验证通过")
                else:
                    invalid_files.append(excel_file)
                    print(f"❌ {excel_file.name} - 格式验证失败")
                    
            except ImportError as e:
                print(f"⚠️  警告: 无法导入格式检查器: {e}")
                print(f"   跳过 {excel_file.name} 的格式验证")
                # 如果无法导入检查器，假定文件有效（向后兼容）
                valid_files.append(excel_file)
                results.append({
                    'file': excel_file,
                    'valid': True,
                    'errors': [],
                    'warnings': [f'格式检查器不可用: {e}']
                })
            except Exception as e:
                print(f"❌ 检查 {excel_file.name} 时发生错误: {e}")
                invalid_files.append(excel_file)
                results.append({
                    'file': excel_file,
                    'valid': False,
                    'errors': [str(e)],
                    'warnings': []
                })
        
        print("\n" + "="*60)
        print(f"📊 验证汇总:")
        print(f"   总文件数: {len(excel_files)}")
        print(f"   ✅ 有效: {len(valid_files)}")
        print(f"   ❌ 无效: {len(invalid_files)}")
        print("="*60)
        
        return {
            'all_valid': len(invalid_files) == 0,
            'results': results,
            'valid_files': valid_files,
            'invalid_files': invalid_files
        }
    
    def select_import_strategy(self) -> str:
        """
        让用户选择导入策略
        
        Returns:
            str: 导入策略 ('skip', 'replace', 'append')
        """
        print("\n请选择导入策略:")
        print("  1. skip    - 跳过重复ID (推荐)")
        print("  2. replace - 替换重复ID")
        print("  3. append  - 追加所有用例")
        
        try:
            strategy_choice = input("请输入策略编号 (1/2/3, 默认1): ").strip() or '1'
            strategy = self.strategy_map.get(strategy_choice, 'skip')
            return strategy
        except (EOFError, OSError):
            # 无法获取输入时，使用默认策略
            print("使用默认策略: skip (跳过重复ID)")
            return 'skip'
    
    def import_excel_cases(self, strategy: str = 'skip') -> Dict[str, Any]:
        """
        执行Excel用例导入
        
        Args:
            strategy: 导入策略
            
        Returns:
            Dict: 导入结果
        """
        try:
            from utils.data_import import ImportManager
            
            manager = ImportManager(self.yaml_file)
            result = manager.batch_import_from_directory(
                str(self.excel_dir),
                strategy=strategy
            )
            
            manager.print_import_summary(result)
            return result
            
        except Exception as e:
            print(f"\n❌ 导入失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def handle_import_failure(self) -> bool:
        """
        处理导入失败情况
        
        Returns:
            bool: 如果用户选择继续返回True,否则返回False
        """
        try:
            print("是否继续执行测试? (y/n, 默认y): ", end='')
            continue_choice = input().strip().lower()
            
            if continue_choice == 'n':
                print("已取消测试执行")
                return False
            
            return True
        except (EOFError, OSError):
            # 无法获取输入时，默认继续
            print("继续执行测试...")
            return True
    
    def check_and_import(self, auto_import: bool = False, strategy: Optional[str] = None) -> bool:
        """
        检查并导入Excel用例 (完整流程: 存在性检查 → 格式验证 → 导入)
        
        Args:
            auto_import: 是否自动导入(True=自动, False=交互式)
            strategy: 导入策略,仅在auto_import为True时使用
        
        Returns:
            bool: 如果成功或用户选择继续返回True,如果用户取消返回False
        """
        # 1. 检查是否有Excel文件
        if not self.has_excel_files():
            return True
        
        # 2. 格式验证（关键步骤）
        validation_result = self.validate_excel_files()
        
        # 2.1 如果格式验证失败，退出系统
        if not validation_result['all_valid']:
            print("\n" + "="*60)
            print("❌ Excel 文件格式验证失败！")
            print("="*60)
            print("\n无效文件列表:")
            for invalid_file in validation_result['invalid_files']:
                print(f"  ❌ {invalid_file.name}")
            
            print("\n" + "="*60)
            print("请修复上述文件中的格式错误后重试")
            print("提示: 可以单独运行格式检查脚本:")
            print("      python scripts/check_excel_json.py")
            print("="*60)
            
            # 格式验证失败，退出系统
            sys.exit(1)
        
        # 2.2 如果没有有效文件，提示并返回
        if not validation_result['valid_files']:
            print("\n⚠️  没有有效的Excel文件可以导入")
            return True
        
        print(f"\n✅ 所有 Excel 文件格式验证通过！")
        
        # 3. 自动导入模式
        if auto_import:
            # 使用环境变量中的策略,或使用参数指定的策略
            if strategy is None:
                strategy = os.environ.get('EXCEL_IMPORT_STRATEGY', 'skip')
            
            print("\n" + "="*60)
            print("Excel用例自动导入模式")
            print(f"有效文件数: {len(validation_result['valid_files'])}")
            for f in validation_result['valid_files']:
                print(f"  ✓ {f.name}")
            print(f"导入策略: {strategy}")
            print("="*60)
            
            # 执行导入
            result = self.import_excel_cases(strategy)
            
            # 处理导入结果
            if not result['success']:
                if not self.handle_import_failure():
                    return False
            
            print("="*60 + "\n")
            return True
        
        # 4. 交互式模式
        print("\n" + "="*60)
        print("检测到有效的Excel用例文件:")
        for f in validation_result['valid_files']:
            print(f"  ✓ {f.name}")
        
        try:
            choice = input("\n是否导入Excel用例到YAML? (y/n, 默认y): ").strip().lower()
            
            if choice == 'n':
                print("跳过Excel导入")
                print("="*60 + "\n")
                return True
        except (EOFError, OSError):
            print("\n检测到非交互式环境，自动导入Excel用例...")
        
        # 5. 选择导入策略
        strategy = self.select_import_strategy()
        
        # 6. 执行导入
        result = self.import_excel_cases(strategy)
        
        # 7. 处理导入结果
        if not result['success']:
            if not self.handle_import_failure():
                return False
        
        print("="*60 + "\n")
        return True


def check_and_import_excel_cases(auto_import: bool = False, strategy: Optional[str] = None) -> bool:
    """
    便捷函数: 检查并导入Excel用例
    
    这是一个向后兼容的接口函数,保持与原有代码的兼容性
    
    Args:
        auto_import: 是否自动导入(True=自动, False=交互式)
        strategy: 导入策略,仅在auto_import为True时使用
    
    Returns:
        bool: 如果成功或用户选择继续返回True,如果用户取消返回False
    """
    loader = ExcelCaseLoader()
    success = loader.check_and_import(auto_import=auto_import, strategy=strategy)
    
    if not success:
        sys.exit(1)
    
    return success


# 提供模块级别的便捷接口
__all__ = ['ExcelCaseLoader', 'check_and_import_excel_cases']
