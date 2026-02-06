#!/usr/bin/env python3
"""JSON测试报告分析工具"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


class JsonReportAnalyzer:
    """JSON报告分析器"""
    
    def __init__(self, json_file: str):
        """初始化分析器"""
        self.json_file = Path(json_file)
        self.data = self._load_json()
    
    def _load_json(self) -> Dict[str, Any]:
        """加载JSON报告文件"""
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"错误: 找不到文件 {self.json_file}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"错误: JSON格式错误 - {e}")
            sys.exit(1)
    
    def get_summary(self) -> Dict[str, Any]:
        """获取测试摘要"""
        summary = self.data.get('summary', {})
        return {
            'total': summary.get('total', 0),
            'passed': summary.get('passed', 0),
            'failed': summary.get('failed', 0),
            'skipped': summary.get('skipped', 0),
            'error': summary.get('error', 0),
            'duration': self.data.get('duration', 0),
            'outcome': summary.get('outcome', 'unknown')
        }
    
    def get_failed_tests(self) -> List[Dict[str, Any]]:
        """获取失败的测试用例"""
        failed_tests = []
        for test in self.data.get('tests', []):
            if test.get('outcome') == 'failed':
                failed_tests.append({
                    'nodeid': test.get('nodeid'),
                    'duration': test.get('duration', 0),
                    'setup_duration': test.get('setup', {}).get('duration', 0),
                    'call_duration': test.get('call', {}).get('duration', 0),
                    'teardown_duration': test.get('teardown', {}).get('duration', 0),
                    'longrepr': test.get('call', {}).get('longrepr', ''),
                    'keywords': test.get('keywords', [])
                })
        return failed_tests
    
    def get_slowest_tests(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取最慢的测试用例"""
        tests = []
        for test in self.data.get('tests', []):
            tests.append({
                'nodeid': test.get('nodeid'),
                'duration': test.get('duration', 0),
                'outcome': test.get('outcome')
            })
        
        # 按执行时间排序
        tests.sort(key=lambda x: x['duration'], reverse=True)
        return tests[:limit]
    
    def get_test_by_markers(self, marker: str) -> List[Dict[str, Any]]:
        """根据标记获取测试用例"""
        marked_tests = []
        for test in self.data.get('tests', []):
            keywords = test.get('keywords', [])
            if marker in keywords:
                marked_tests.append({
                    'nodeid': test.get('nodeid'),
                    'outcome': test.get('outcome'),
                    'duration': test.get('duration', 0)
                })
        return marked_tests
    
    def get_environment_info(self) -> Dict[str, Any]:
        """获取环境信息"""
        return self.data.get('environment', {})
    
    def print_summary_report(self):
        """打印摘要报告"""
        summary = self.get_summary()
        env = self.get_environment_info()
        
        print("=" * 60)
        print("📊 测试执行摘要报告")
        print("=" * 60)
        
        # 基本信息
        print(f"📅 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️  总耗时: {summary['duration']:.2f}秒")
        print(f"🎯 测试结果: {summary['outcome'].upper()}")
        print()
        
        # 测试统计
        print("📈 测试统计:")
        print(f"  总计: {summary['total']}")
        print(f"  ✅ 通过: {summary['passed']}")
        print(f"  ❌ 失败: {summary['failed']}")
        print(f"  ⏭️  跳过: {summary['skipped']}")
        print(f"  💥 错误: {summary['error']}")
        
        # 成功率
        if summary['total'] > 0:
            success_rate = (summary['passed'] / summary['total']) * 100
            print(f"  📊 成功率: {success_rate:.1f}%")
        print()
        
        # 环境信息
        print("🔧 环境信息:")
        print(f"  Python: {env.get('Python', 'Unknown')}")
        print(f"  平台: {env.get('Platform', 'Unknown')}")
        
        packages = env.get('Packages', {})
        if packages:
            print("  📦 主要包版本:")
            for pkg, version in packages.items():
                print(f"    {pkg}: {version}")
        print()
        
        # 失败测试详情
        failed_tests = self.get_failed_tests()
        if failed_tests:
            print("❌ 失败测试详情:")
            for i, test in enumerate(failed_tests[:5], 1):  # 只显示前5个
                print(f"  {i}. {test['nodeid']}")
                print(f"     耗时: {test['duration']:.2f}秒")
                if test['longrepr']:
                    # 只显示错误信息的第一行
                    error_line = test['longrepr'].split('\n')[0]
                    if len(error_line) > 80:
                        error_line = error_line[:77] + "..."
                    print(f"     错误: {error_line}")
                print()
        
        # 最慢测试
        slowest = self.get_slowest_tests(5)
        if slowest:
            print("🐌 最慢的测试:")
            for i, test in enumerate(slowest, 1):
                print(f"  {i}. {test['nodeid']} - {test['duration']:.2f}秒 ({test['outcome']})")
            print()
        
        print("=" * 60)
    
    def export_csv(self, output_file: str):
        """导出CSV格式报告"""
        import csv
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['nodeid', 'outcome', 'duration', 'setup_duration', 
                         'call_duration', 'teardown_duration', 'keywords']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for test in self.data.get('tests', []):
                writer.writerow({
                    'nodeid': test.get('nodeid', ''),
                    'outcome': test.get('outcome', ''),
                    'duration': test.get('duration', 0),
                    'setup_duration': test.get('setup', {}).get('duration', 0),
                    'call_duration': test.get('call', {}).get('duration', 0),
                    'teardown_duration': test.get('teardown', {}).get('duration', 0),
                    'keywords': ','.join(test.get('keywords', []))
                })
        
        print(f"CSV报告已导出到: {output_file}")
    
    def generate_markdown_report(self, output_file: str):
        """生成Markdown格式报告"""
        summary = self.get_summary()
        failed_tests = self.get_failed_tests()
        slowest_tests = self.get_slowest_tests(10)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# 测试执行报告\n\n")
            
            # 摘要
            f.write("## 📊 执行摘要\n\n")
            f.write(f"- **总耗时**: {summary['duration']:.2f}秒\n")
            f.write(f"- **测试结果**: {summary['outcome'].upper()}\n")
            f.write(f"- **总计**: {summary['total']}\n")
            f.write(f"- **✅ 通过**: {summary['passed']}\n")
            f.write(f"- **❌ 失败**: {summary['failed']}\n")
            f.write(f"- **⏭️ 跳过**: {summary['skipped']}\n")
            f.write(f"- **💥 错误**: {summary['error']}\n\n")
            
            if summary['total'] > 0:
                success_rate = (summary['passed'] / summary['total']) * 100
                f.write(f"- **📊 成功率**: {success_rate:.1f}%\n\n")
            
            # 失败测试
            if failed_tests:
                f.write("## ❌ 失败测试\n\n")
                f.write("| 测试用例 | 耗时(秒) | 错误信息 |\n")
                f.write("|----------|----------|----------|\n")
                for test in failed_tests:
                    error = test['longrepr'].split('\n')[0] if test['longrepr'] else 'N/A'
                    if len(error) > 50:
                        error = error[:47] + "..."
                    f.write(f"| {test['nodeid']} | {test['duration']:.2f} | {error} |\n")
                f.write("\n")
            
            # 最慢测试
            if slowest_tests:
                f.write("## 🐌 最慢的测试\n\n")
                f.write("| 排名 | 测试用例 | 耗时(秒) | 结果 |\n")
                f.write("|------|----------|----------|------|\n")
                for i, test in enumerate(slowest_tests, 1):
                    f.write(f"| {i} | {test['nodeid']} | {test['duration']:.2f} | {test['outcome']} |\n")
                f.write("\n")
        
        print(f"Markdown报告已生成: {output_file}")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法: python json_report_analyzer.py <json_file> [options]")
        print("选项:")
        print("  --csv <file>      导出CSV格式")
        print("  --markdown <file> 生成Markdown报告")
        print("  --marker <name>   按标记筛选测试")
        sys.exit(1)
    
    json_file = sys.argv[1]
    analyzer = JsonReportAnalyzer(json_file)
    
    # 默认显示摘要报告
    analyzer.print_summary_report()
    
    # 处理其他选项
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--csv' and i + 1 < len(sys.argv):
            analyzer.export_csv(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == '--markdown' and i + 1 < len(sys.argv):
            analyzer.generate_markdown_report(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == '--marker' and i + 1 < len(sys.argv):
            marker = sys.argv[i + 1]
            tests = analyzer.get_test_by_markers(marker)
            print(f"\n🏷️  标记为 '{marker}' 的测试:")
            for test in tests:
                print(f"  {test['nodeid']} - {test['outcome']} ({test['duration']:.2f}秒)")
            i += 2
        else:
            i += 1


if __name__ == "__main__":
    main()