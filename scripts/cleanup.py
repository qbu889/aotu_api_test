"""
项目清理脚本 - 清除临时文件和缓存

使用方法:
    python scripts/cleanup.py          # 清理所有
    python scripts/cleanup.py --cache  # 只清理缓存
    python scripts/cleanup.py --logs   # 只清理旧日志
"""

import os
import sys
import argparse
import shutil
from pathlib import Path
from datetime import datetime, timedelta


def get_project_root():
    """获取项目根目录"""
    return Path(__file__).parent.parent


def remove_pycache(project_root):
    """删除所有 __pycache__ 目录"""
    print("\n[清理 Python 缓存]")
    count = 0
    for pycache_dir in project_root.rglob('__pycache__'):
        try:
            shutil.rmtree(pycache_dir)
            print(f"  删除: {pycache_dir.relative_to(project_root)}")
            count += 1
        except Exception as e:
            print(f"  失败: {pycache_dir} - {e}")
    print(f"共删除 {count} 个缓存目录")


def remove_pytest_cache(project_root):
    """删除 pytest 缓存"""
    print("\n[清理 pytest 缓存]")
    pytest_cache = project_root / '.pytest_cache'
    if pytest_cache.exists():
        try:
            shutil.rmtree(pytest_cache)
            print(f"  删除: .pytest_cache")
        except Exception as e:
            print(f"  失败: {e}")
    else:
        print("  无需清理")


def remove_old_logs(project_root, days=7):
    """删除旧日志文件（默认7天前）"""
    print(f"\n[清理旧日志文件（{days}天前）]")
    logs_dir = project_root / 'logs'
    if not logs_dir.exists():
        print("  日志目录不存在")
        return
    
    cutoff_date = datetime.now() - timedelta(days=days)
    count = 0
    
    for log_file in logs_dir.glob('*.log'):
        try:
            file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
            if file_time < cutoff_date:
                log_file.unlink()
                print(f"  删除: {log_file.name}")
                count += 1
        except Exception as e:
            print(f"  失败: {log_file.name} - {e}")
    
    print(f"共删除 {count} 个日志文件")


def remove_old_reports(project_root, days=7):
    """删除旧测试报告（默认7天前）"""
    print(f"\n[清理旧测试报告（{days}天前）]")
    reports_dir = project_root / 'reports'
    if not reports_dir.exists():
        print("  报告目录不存在")
        return
    
    cutoff_date = datetime.now() - timedelta(days=days)
    count = 0
    
    for report_file in reports_dir.glob('*.html'):
        try:
            file_time = datetime.fromtimestamp(report_file.stat().st_mtime)
            if file_time < cutoff_date:
                report_file.unlink()
                print(f"  删除: {report_file.name}")
                count += 1
        except Exception as e:
            print(f"  失败: {report_file.name} - {e}")
    
    print(f"共删除 {count} 个报告文件")


def remove_backup_files(project_root):
    """删除备份文件"""
    print("\n[清理备份文件]")
    patterns = ['*.bak', '*.backup', '*.tmp', '*~']
    count = 0
    
    for pattern in patterns:
        for backup_file in project_root.rglob(pattern):
            if backup_file.is_file():
                try:
                    backup_file.unlink()
                    print(f"  删除: {backup_file.relative_to(project_root)}")
                    count += 1
                except Exception as e:
                    print(f"  失败: {backup_file.name} - {e}")
    
    print(f"共删除 {count} 个备份文件")


def main():
    parser = argparse.ArgumentParser(description='项目清理工具')
    parser.add_argument('--cache', action='store_true', help='只清理缓存')
    parser.add_argument('--logs', action='store_true', help='只清理旧日志')
    parser.add_argument('--reports', action='store_true', help='只清理旧报告')
    parser.add_argument('--backup', action='store_true', help='只清理备份文件')
    parser.add_argument('--days', type=int, default=7, help='保留最近N天的文件（默认7天）')
    parser.add_argument('--all', action='store_true', help='清理所有')
    
    args = parser.parse_args()
    
    project_root = get_project_root()
    
    print("=" * 60)
    print("项目清理工具")
    print("=" * 60)
    print(f"项目路径: {project_root}")
    
    # 如果没有指定任何选项，默认清理所有
    if not any([args.cache, args.logs, args.reports, args.backup, args.all]):
        args.all = True
    
    if args.cache or args.all:
        remove_pycache(project_root)
        remove_pytest_cache(project_root)
    
    if args.logs or args.all:
        remove_old_logs(project_root, args.days)
    
    if args.reports or args.all:
        remove_old_reports(project_root, args.days)
    
    if args.backup or args.all:
        remove_backup_files(project_root)
    
    print("\n" + "=" * 60)
    print("清理完成！")
    print("=" * 60)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户取消操作")
        sys.exit(0)
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
