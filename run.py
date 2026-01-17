#!/usr/bin/env python3
"""
微信年度报告生成器 - 主启动脚本

使用方法:
  python run.py --backup "备份目录" --output "输出目录" --year 2025
  python run.py --db "数据库路径" --output "输出目录" --year 2025
  python run.py --json "report_data.json" --output "输出目录"
"""

import sys
import os
import argparse
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.extractor import BackupExtractor
from src.decryptor import WeChatDecryptor
from src.analyzer import WeChatAnalyzer
from src.reporter import ReportGenerator


def run_full_pipeline(backup_path: str, output_dir: str, year: int = None):
    """
    完整流程：从备份文件到生成报告

    Args:
        backup_path: vivo互传备份目录路径
        output_dir: 输出目录
        year: 分析年份

    Returns:
        bool: 是否成功
    """
    if year is None:
        year = datetime.now().year - 1

    os.makedirs(output_dir, exist_ok=True)

    print("=" * 60)
    print(f"微信年度报告生成器 - {year} 年度")
    print("=" * 60)

    # 1. 提取数据库
    print("\n[1/4] 提取数据库...")
    extractor = BackupExtractor(backup_path, output_dir)
    db_path, uin, sns_db_path = extractor.extract_wechat_db()

    if not db_path or not uin:
        print("错误: 无法提取数据库或UIN")
        return False

    print(f"✓ 数据库: {db_path}")
    print(f"✓ UIN: {uin}")
    if sns_db_path:
        print(f"✓ 朋友圈数据库: {sns_db_path}")

    # 2. 解密数据库
    print("\n[2/4] 解密数据库...")
    decryptor = WeChatDecryptor(db_path)
    decrypted_path = os.path.join(output_dir, "EnMicroMsg_decrypted.db")
    success, result = decryptor.decrypt(uin, output_path=decrypted_path)

    if not success:
        print(f"错误: 解密失败 - {result}")
        return False

    print(f"✓ 解密成功: {decrypted_path}")

    # 3. 分析数据
    print(f"\n[3/4] 分析 {year} 年数据...")
    analyzer = WeChatAnalyzer(decrypted_path, year, sns_db_path)
    json_path = os.path.join(output_dir, f"report_data_{year}.json")
    report_data = analyzer.save_report(json_path)

    print(f"✓ 数据分析完成: {json_path}")

    # 4. 生成报告
    print("\n[4/4] 生成HTML报告...")
    generator = ReportGenerator(report_data)
    html_path = os.path.join(output_dir, f"wechat_wrapped_{year}.html")
    generator.generate(html_path)

    print(f"✓ 报告生成完成: {html_path}")

    print("\n" + "=" * 60)
    print("✓ 全部完成!")
    print(f"📄 JSON数据: {json_path}")
    print(f"🌐 HTML报告: {html_path}")
    print("=" * 60)

    return True


def run_from_db(db_path: str, output_dir: str, year: int = None, sns_db_path: str = None):
    """
    从已解密的数据库生成报告

    Args:
        db_path: 解密后的数据库路径
        output_dir: 输出目录
        year: 分析年份
        sns_db_path: 朋友圈数据库路径 (可选)

    Returns:
        bool: 是否成功
    """
    if year is None:
        year = datetime.now().year - 1

    os.makedirs(output_dir, exist_ok=True)

    print("=" * 60)
    print(f"微信年度报告生成器 - {year} 年度")
    print("=" * 60)

    # 1. 分析数据
    print(f"\n[1/2] 分析 {year} 年数据...")
    analyzer = WeChatAnalyzer(db_path, year, sns_db_path)
    json_path = os.path.join(output_dir, f"report_data_{year}.json")
    report_data = analyzer.save_report(json_path)

    print(f"✓ 数据分析完成: {json_path}")

    # 2. 生成报告
    print("\n[2/2] 生成HTML报告...")
    generator = ReportGenerator(report_data)
    html_path = os.path.join(output_dir, f"wechat_wrapped_{year}.html")
    generator.generate(html_path)

    print(f"✓ 报告生成完成: {html_path}")

    print("\n" + "=" * 60)
    print("✓ 全部完成!")
    print(f"📄 JSON数据: {json_path}")
    print(f"🌐 HTML报告: {html_path}")
    print("=" * 60)

    return True


def run_from_json(json_path: str, output_dir: str):
    """
    从JSON数据生成报告

    Args:
        json_path: 报告数据JSON路径
        output_dir: 输出目录

    Returns:
        bool: 是否成功
    """
    import json

    os.makedirs(output_dir, exist_ok=True)

    print("=" * 60)
    print("微信年度报告生成器 - 从JSON生成")
    print("=" * 60)

    print(f"\n读取数据: {json_path}")
    with open(json_path, 'r', encoding='utf-8') as f:
        report_data = json.load(f)

    year = report_data.get('year', datetime.now().year - 1)

    print(f"\n生成 {year} 年度报告...")
    generator = ReportGenerator(report_data)
    html_path = os.path.join(output_dir, f"wechat_wrapped_{year}.html")
    generator.generate(html_path)

    print(f"✓ 报告生成完成: {html_path}")

    print("\n" + "=" * 60)
    print("✓ 完成!")
    print(f"🌐 HTML报告: {html_path}")
    print("=" * 60)

    return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="微信年度报告生成器 - 一键生成 Spotify Wrapped 风格的微信年度报告",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:

  # 从vivo互传备份生成（完整流程）
  python run.py --backup "F:\\vivo X100 Pro 20260108_061606" --output "F:\\report" --year 2025

  # 从已解密数据库生成
  python run.py --db "F:\\EnMicroMsg_decrypted.db" --output "F:\\report" --year 2025

  # 从已解密数据库生成（包含朋友圈）
  python run.py --db "F:\\EnMicroMsg_decrypted.db" --sns-db "F:\\SnsMicroMsg.db" --output "F:\\report"

  # 从JSON数据生成报告
  python run.py --json "F:\\report_data_2025.json" --output "F:\\report"
        """
    )

    parser.add_argument("--backup", "-b", help="vivo互传备份目录路径")
    parser.add_argument("--db", "-d", help="已解密的数据库路径")
    parser.add_argument("--sns-db", help="朋友圈数据库路径 (可选)")
    parser.add_argument("--json", "-j", help="报告数据JSON路径")
    parser.add_argument("--output", "-o", default="./output", help="输出目录 (默认: ./output)")
    parser.add_argument("--year", "-y", type=int, help="分析年份 (默认: 去年)")

    args = parser.parse_args()

    # 根据参数选择运行模式
    try:
        if args.backup:
            success = run_full_pipeline(args.backup, args.output, args.year)
        elif args.db:
            success = run_from_db(args.db, args.output, args.year, args.sns_db)
        elif args.json:
            success = run_from_json(args.json, args.output)
        else:
            parser.print_help()
            return False

        return success

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
