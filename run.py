import os
import sys
import argparse
import pytest
from datetime import datetime
from config.settings import REPORT_DIR
from utils.excel_case_loader import check_and_import_excel_cases


def run_tests(auto_import=False):
    """执行测试并生成报告
    
    Args:
        auto_import: 是否自动导入Excel用例 (默认False为交互式)
    """
    # 1. 检查并导入Excel用例
    check_and_import_excel_cases(auto_import=auto_import)
    
    # 2. 生成报告文件名
    now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    report_file = os.path.join(REPORT_DIR, f'report_{now}.html')

    # 3. 获取测试用例目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    test_case_dir = os.path.join(script_dir, 'TestCase')

    # 4. 构建pytest命令
    pytest_args = [
        test_case_dir,  # 使用绝对路径
        '--html=' + report_file,
        '--self-contained-html',
        '-v'
    ]

    # 5. 执行测试
    print(f" 开始执行测试，报告将保存至: {report_file}")
    exit_code = pytest.main(pytest_args)

    # 6. 输出结果
    if exit_code == 0:
        print(f"\n 测试执行成功！报告已生成: {report_file}")
    else:
        print(f"\n 测试执行完成，存在失败用例。报告已生成: {report_file}")

    return exit_code


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='API自动化测试框架')
    parser.add_argument(
        '-i', '--import',
        action='store_true',
        dest='auto_import',
        help='自动导入Excel用例 (使用 -i 或 --import)'
    )
    parser.add_argument(
        '-s', '--strategy',
        choices=['skip', 'replace', 'append'],
        default='skip',
        help='导入策略: skip(跳过重复ID), replace(替换), append(追加) [默认: skip]'
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    
    # 将策略保存到环境变量，供excel_case_loader使用
    if args.auto_import:
        os.environ['EXCEL_IMPORT_STRATEGY'] = args.strategy
    
    run_tests(auto_import=args.auto_import)
