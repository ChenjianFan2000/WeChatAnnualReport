"""
报告生成器
生成 Spotify Wrapped 风格的微信年度报告
"""

import os
import json
import html as html_lib
from typing import Dict, Any


class ReportGenerator:
    """HTML 报告生成器"""

    def __init__(self, report_data: Dict[str, Any]):
        """
        初始化生成器

        Args:
            report_data: 分析报告数据 (JSON格式)
        """
        self.data = report_data

    @classmethod
    def from_json_file(cls, json_path: str) -> "ReportGenerator":
        """从JSON文件创建生成器"""
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls(data)

    def generate(self, output_path: str):
        """
        生成HTML报告

        Args:
            output_path: 输出HTML文件路径
        """
        # 使用模板生成器
        from templates.wrapped_template import generate_wrapped_report_from_data
        html_content = generate_wrapped_report_from_data(self.data)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"报告已生成: {output_path}")
        return output_path

    @staticmethod
    def escape(text):
        """HTML转义"""
        if text is None:
            return ""
        return html_lib.escape(str(text))

    @staticmethod
    def format_num(n):
        """格式化数字"""
        if n is None:
            return "0"
        return f"{int(n):,}"


def generate_report(json_path: str, output_path: str) -> str:
    """
    便捷函数: 从JSON生成报告

    Args:
        json_path: 报告数据JSON路径
        output_path: 输出HTML路径

    Returns:
        生成的HTML文件路径
    """
    generator = ReportGenerator.from_json_file(json_path)
    return generator.generate(output_path)
