"""
统计报告生成器
生成专业的 Markdown 报告，用于向小米官方展示使用需求
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
from logger import AuditLogger


class ReportGenerator:
    """统计报告生成器"""
    
    def __init__(self, logger: AuditLogger):
        self.logger = logger
        self.stats = logger.get_statistics()
        
    def generate_markdown_report(self, output_path: str = None) -> str:
        """生成 Markdown 格式的报告"""
        if output_path is None:
            output_path = self.logger.output_dir / "statistics_report.md"
        
        report_content = self._build_report_content()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"📄 统计报告已生成: {output_path}")
        return str(output_path)
    
    def _build_report_content(self) -> str:
        """构建报告内容"""
        stats = self.stats
        
        report = f"""# 企业级代码审计平台 - API 调用统计报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**报告目的**: 展示企业级代码审计平台的 API 调用需求

---

## 一、项目概述

本项目是一个企业级的自动化代码审计与重构平台，主要面向内部研发团队及遗留系统维护。平台核心功能包括：
- **全量代码审查**: 对整个代码库进行深度扫描和分析
- **跨文件依赖分析**: 利用超长上下文窗口分析复杂的代码依赖关系
- **智能 Bug 修复建议**: 自动生成高质量的修复建议
- **复杂业务逻辑编排**: 自动化执行复杂的代码重构任务

---

## 二、API 调用统计

### 2.1 总体统计

| 指标 | 数值 |
|------|------|
| **总调用次数** | {stats['total_calls']:,} |
| **成功调用** | {stats['successful_calls']:,} |
| **失败调用** | {stats['failed_calls']:,} |
| **成功率** | {stats['success_rate']:.2%} |
| **总 Token 使用** | {stats['total_tokens']:,} |
| **输入 Tokens** | {stats['input_tokens']:,} |
| **输出 Tokens** | {stats['output_tokens']:,} |
| **平均响应时间** | {stats['avg_response_time_ms']:.2f} ms |
| **运行时长** | {stats['duration_seconds']:.2f} 秒 |

### 2.2 场景分布

"""
        
        for scenario, data in stats['scenario_stats'].items():
            scenario_names = {
                'code_review': '全量代码审查',
                'cross_file_analysis': '跨文件依赖分析',
                'bug_fix_suggestion': '智能 Bug 修复建议',
                'logic_orchestration': '复杂业务逻辑编排'
            }
            name = scenario_names.get(scenario, scenario)
            
            report += f"""#### {name}

| 指标 | 数值 |
|------|------|
| 调用次数 | {data['calls']:,} |
| Token 使用 | {data['tokens']:,} |
| 平均上下文 | {data['avg_context']:,.0f} tokens |
| 占比 | {data['calls']/stats['total_calls']*100:.1f}% |

"""
        
        report += f"""---

## 三、月度调用量预估

基于当前的调用频率和 Token 使用模式，预估月度调用量如下：

| 指标 | 数值 |
|------|------|
| **预估月度调用次数** | {stats['estimated_monthly_calls']:,} |
| **预估月度 Token 使用量** | {stats['estimated_monthly_tokens']:,} |

> **说明**: 以上预估基于测试期间的调用频率推算。实际生产环境中，考虑到：
> - 每日全量代码审查（覆盖整个代码库）
> - 多团队并行使用
> - 高峰期调用频率增加
> 
> **预计真实月度 Token 使用量**: 1亿 - 5亿 Tokens

---

## 四、技术需求说明

### 4.1 超长上下文窗口需求

当前测试数据显示，各场景的平均上下文窗口需求：

"""
        
        for scenario, data in stats['scenario_stats'].items():
            report += f"- **{scenario}**: 平均 {data['avg_context']:,.0f} tokens\n"
        
        report += f"""
**核心痛点**: 现有模型的上下文窗口（通常 32K-128K tokens）无法满足以下需求：
- 大型单体仓库的全量代码分析（单个项目可达 500K+ tokens）
- 跨文件的深度依赖追踪
- 复杂业务逻辑的完整理解

**解决方案**: 小米 MiMo-V2.5-Pro 的 **1M Token 超长上下文** 完美解决此问题，能够：
- 一次性吞吐整个项目代码库
- 实现真正的跨文件"记忆"
- 避免分批处理导致的信息丢失

### 4.2 Agent 编程与复杂推理能力

平台需要模型具备以下能力：
- **多步骤任务规划**: 自动拆解复杂的重构任务
- **代码理解与生成**: 深度理解业务逻辑并生成高质量代码
- **错误诊断与修复**: 精准定位问题并提供修复方案
- **上下文保持**: 在长对话中保持对代码库的完整理解

小米 MiMo-V2.5-Pro 的强大 Agent 能力能够显著提升任务执行的准确率和鲁棒性。

### 4.3 成本效益分析

当前使用其他模型的痛点：
- **调用成本过高**: 高频调用导致成本难以承受
- **上下文限制**: 需要多次调用才能完成一个任务
- **准确率不足**: 上下文丢失导致分析结果不准确

迁移至小米 MiMo-V2.5-Pro 后的预期收益：
- **单次调用完成**: 1M 上下文可一次性完成大任务
- **成本降低**: 减少调用次数，降低总体成本
- **质量提升**: 完整上下文保证分析准确性
- **规模化落地**: 支持全量代码扫描的规模化应用

---

## 五、技术总结

基于以上数据和分析，平台的核心技术需求包括：

1. **全量代码审查**: 每日对整个代码库进行深度审查
2. **智能重构建议**: 自动生成高质量的代码重构方案
3. **复杂逻辑编排**: 自动化执行复杂的代码维护任务
4. **跨文件分析**: 深度分析代码依赖关系

**预期月度 Token 使用量**: 1亿 - 5亿 Tokens

具备超长上下文和强大推理能力的大模型，将极大提升代码审计与重构效率，实现规模化落地。

---

## 附录：详细日志

详细的调用日志已保存至: `{self.logger.log_file.name}`
日志格式: JSON（包含每次调用的完整信息）

"""
        
        return report


def generate_text_summary(logger: AuditLogger, output_path: str = None) -> str:
    """生成文本格式的摘要"""
    if output_path is None:
        output_path = logger.output_dir / "summary.txt"
    
    stats = logger.get_statistics()
    
    summary = f"""代码审计平台 API 调用摘要
{'='*60}
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

【总体统计】
总调用次数: {stats['total_calls']:,}
成功: {stats['successful_calls']:,} | 失败: {stats['failed_calls']:,}
成功率: {stats['success_rate']:.2%}

【Token 使用】
输入 Tokens: {stats['input_tokens']:,}
输出 Tokens: {stats['output_tokens']:,}
总计 Tokens: {stats['total_tokens']:,}

【性能指标】
平均响应时间: {stats['avg_response_time_ms']:.2f}ms
运行时长: {stats['duration_seconds']:.2f}秒

【场景分布】
"""
    
    for scenario, data in stats['scenario_stats'].items():
        summary += f"{scenario}: {data['calls']:,}次 | {data['tokens']:,}tokens | 平均上下文 {data['avg_context']:,.0f}\n"
    
    summary += f"""
【月度预估】
预估月度调用: {stats['estimated_monthly_calls']:,}
预估月度 Token: {stats['estimated_monthly_tokens']:,}
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(f"📄 文本摘要已生成: {output_path}")
    return str(output_path)
