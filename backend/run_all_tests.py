#!/usr/bin/env python3
"""
综合测试脚本
运行所有测试并生成综合测试报告
"""

import subprocess
import sys
from typing import Dict, List
from datetime import datetime

def run_test(test_name: str, test_command: List[str]) -> Dict:
    """运行测试并返回结果"""
    print(f"\n{'='*60}")
    print(f"🧪 运行测试: {test_name}")
    print('='*60)
    
    start_time = datetime.now()
    
    try:
        result = subprocess.run(
            test_command,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        success = result.returncode == 0
        
        return {
            'name': test_name,
            'success': success,
            'duration': duration,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            'name': test_name,
            'success': False,
            'duration': 60,
            'stdout': '',
            'stderr': '测试超时',
            'returncode': -1
        }

def parse_test_output(output: str) -> Dict[str, int]:
    """解析测试输出"""
    stats = {
        'pass': 0,
        'fail': 0,
        'warn': 0,
        'error': 0
    }
    
    stats['pass'] = output.count('[OK]')
    stats['pass'] += output.count('[PASS]')
    stats['pass'] += output.count('✅')
    
    stats['fail'] = output.count('[FAIL]')
    stats['fail'] += output.count('❌')
    
    stats['warn'] = output.count('[WARN]')
    stats['warn'] += output.count('⚠️')
    
    stats['error'] = output.count('[ERROR]')
    stats['error'] += output.count('🔴')
    
    return stats

def generate_report(results: List[Dict]) -> str:
    """生成测试报告"""
    report = []
    report.append("="*80)
    report.append("综合测试报告")
    report.append("="*80)
    report.append(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # 汇总信息
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r['success'])
    failed_tests = total_tests - passed_tests
    pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    report.append("📊 测试汇总")
    report.append("-"*80)
    report.append(f"总测试数: {total_tests}")
    report.append(f"通过测试: {passed_tests}")
    report.append(f"失败测试: {failed_tests}")
    report.append(f"通过率: {pass_rate:.1f}%")
    report.append("")
    
    # 详细结果
    report.append("📋 详细测试结果")
    report.append("-"*80)
    
    for result in results:
        status = "✅ 通过" if result['success'] else "❌ 失败"
        duration = f"{result['duration']:.2f}秒"
        
        report.append(f"{status} | {result['name']:30s} | {duration:>10s}")
        
        if not result['success']:
            report.append(f"      返回码: {result['returncode']}")
            report.append(f"      错误: {result['stderr'][:100] if result['stderr'] else '无错误信息'}")
        
        stats = parse_test_output(result['stdout'])
        if sum(stats.values()) > 0:
            report.append(f"      统计: {stats}")
        
        report.append("")
    
    # 测试结论
    report.append("="*80)
    report.append("测试结论")
    report.append("="*80)
    
    if pass_rate == 100:
        report.append("🎉 所有测试通过！代码质量优秀，可以放心使用。")
    elif pass_rate >= 80:
        report.append("✅ 大部分测试通过，代码质量良好，建议修复失败的测试。")
    elif pass_rate >= 60:
        report.append("⚠️  部分测试失败，代码质量一般，需要修复问题。")
    else:
        report.append("❌ 多数测试失败，代码质量较差，需要重点修复。")
    
    report.append("")
    report.append("下一步建议:")
    
    if failed_tests > 0:
        report.append("1. 查看失败测试的详细信息")
        report.append("2. 修复失败的问题")
        report.append("3. 重新运行测试验证修复效果")
    else:
        report.append("1. 代码可以继续开发")
        report.append("2. 可以开始部署测试环境")
        report.append("3. 可以进行集成测试")
    
    report.append("")
    report.append("="*80)
    
    return "\n".join(report)

def main():
    """主测试函数"""
    print("🚀 开始综合测试...")
    
    # 定义测试列表
    tests = [
        {
            'name': '音频文件处理测试',
            'command': ['python3', 'test_audio_service.py']
        },
        {
            'name': '自动组卷算法测试',
            'command': ['python3', 'test_paper_generator.py']
        }
    ]
    
    # 运行所有测试
    results = []
    total_duration = 0
    
    for test in tests:
        result = run_test(test['name'], test['command'])
        results.append(result)
        total_duration += result['duration']
    
    # 生成报告
    report = generate_report(results)
    
    print(report)
    print(f"\n⏱️  总测试时间: {total_duration:.2f}秒")
    
    # 判断整体结果
    success = all(r['success'] for r in results)
    
    if success:
        print("\n✅ 所有测试通过！")
        return 0
    else:
        print("\n❌ 部分测试失败，请查看详细报告。")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 测试过程出错: {str(e)}")
        sys.exit(1)
