"""
Excel用例加载器模块

职责:
- 检测Excel用例文件
- 提供交互式导入功能
- 处理导入策略选择
- 提供导入结果反馈
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any


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
    
    def prompt_user_for_import(self) -> bool:
        """
        询问用户是否导入Excel用例
        
        Returns:
            bool: 用户选择导入返回True,否则返回False
        """
        excel_files = self.get_excel_files()
        
        if not excel_files:
            return False
        
        print("\n" + "="*60)
        print("检测到Excel用例文件:")
        for f in excel_files:
            print(f"  - {f.name}")
        
        try:
            choice = input("\n是否导入Excel用例到YAML? (y/n, 默认y): ").strip().lower()
            
            # 默认为'y'(导入)，只有明确输入'n'才跳过
            if choice == 'n':
                print("跳过Excel导入")
                print("="*60 + "\n")
                return False
            
            return True
        except (EOFError, OSError):
            # 无法获取输入时，自动导入（适配IDE运行）
            print("\n检测到非交互式环境，自动导入Excel用例...")
            print("="*60 + "\n")
            return True
    
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
        检查并导入Excel用例 (完整流程)
        
        Args:
            auto_import: 是否自动导入(True=自动, False=交互式)
            strategy: 导入策略,仅在auto_import为True时使用
        
        Returns:
            bool: 如果成功或用户选择继续返回True,如果用户取消返回False
        """
        # 1. 检查是否有Excel文件
        if not self.has_excel_files():
            return True
        
        # 2. 自动导入模式
        if auto_import:
            # 使用环境变量中的策略,或使用参数指定的策略
            if strategy is None:
                strategy = os.environ.get('EXCEL_IMPORT_STRATEGY', 'skip')
            
            print("\n" + "="*60)
            print("Excel用例自动导入模式")
            excel_files = self.get_excel_files()
            print(f"检测到 {len(excel_files)} 个Excel文件:")
            for f in excel_files:
                print(f"  - {f.name}")
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
        
        # 3. 交互式模式
        if not self.prompt_user_for_import():
            return True
        
        # 4. 选择导入策略
        strategy = self.select_import_strategy()
        
        # 5. 执行导入
        result = self.import_excel_cases(strategy)
        
        # 6. 处理导入结果
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
