"""
详细的日志记录系统
用于记录所有 API 调用的详细信息，展示给小米官方查看
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class APICallLog:
    """单次 API 调用日志"""
    timestamp: str
    scenario: str  # 场景类型
    task_description: str  # 任务描述
    input_tokens: int  # 输入 token 数
    output_tokens: int  # 输出 token 数
    total_tokens: int  # 总 token 数
    context_window: int  # 上下文窗口大小
    response_time_ms: int  # 响应时间（毫秒）
    success: bool  # 是否成功
    error_message: Optional[str] = None  # 错误信息
    retry_count: int = 0  # 重试次数
    model: str = ""  # 使用的模型
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AuditLogger:
    """代码审计平台日志记录器"""
    
    def __init__(self, output_dir: str = "./logs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.logs: list[APICallLog] = []
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        
        # 日志文件路径
        self.log_file = self.output_dir / "audit_calls.json"
        self.summary_file = self.output_dir / "summary.txt"
        
    def start_session(self):
        """开始日志会话"""
        self.start_time = datetime.now()
        self.logs = []
        print(f"📊 日志会话开始: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
    def end_session(self):
        """结束日志会话"""
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        print(f"📊 日志会话结束: {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️  总运行时长: {duration:.2f} 秒")
        
    def log_call(
        self,
        scenario: str,
        task_description: str,
        input_tokens: int,
        output_tokens: int,
        context_window: int,
        response_time_ms: int,
        success: bool,
        model: str,
        error_message: Optional[str] = None,
        retry_count: int = 0
    ):
        """记录一次 API 调用"""
        log_entry = APICallLog(
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
            scenario=scenario,
            task_description=task_description,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            context_window=context_window,
            response_time_ms=response_time_ms,
            success=success,
            error_message=error_message,
            retry_count=retry_count,
            model=model
        )
        
        self.logs.append(log_entry)
        
        # 实时打印关键信息
        status = "✅" if success else "❌"
        print(f"{status} [{scenario}] {task_description[:50]}... "
              f"| Tokens: {input_tokens:,}+{output_tokens:,}={input_tokens+output_tokens:,} "
              f"| Context: {context_window:,} "
              f"| Time: {response_time_ms}ms")
        
    def save_logs(self):
        """保存日志到文件"""
        # 保存 JSON 格式的详细日志
        logs_data = [log.to_dict() for log in self.logs]
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(logs_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 日志已保存到: {self.log_file}")
        
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        if not self.logs:
            return {}
            
        total_calls = len(self.logs)
        successful_calls = sum(1 for log in self.logs if log.success)
        failed_calls = total_calls - successful_calls
        
        total_tokens = sum(log.total_tokens for log in self.logs)
        input_tokens = sum(log.input_tokens for log in self.logs)
        output_tokens = sum(log.output_tokens for log in self.logs)
        
        avg_response_time = sum(log.response_time_ms for log in self.logs if log.success) / max(successful_calls, 1)
        
        # 按场景统计
        scenario_stats = {}
        for log in self.logs:
            if log.scenario not in scenario_stats:
                scenario_stats[log.scenario] = {
                    'calls': 0,
                    'tokens': 0,
                    'avg_context': 0
                }
            scenario_stats[log.scenario]['calls'] += 1
            scenario_stats[log.scenario]['tokens'] += log.total_tokens
            scenario_stats[log.scenario]['avg_context'] += log.context_window
        
        # 计算平均上下文
        for scenario in scenario_stats:
            scenario_stats[scenario]['avg_context'] = (
                scenario_stats[scenario]['avg_context'] / scenario_stats[scenario]['calls']
            )
        
        # 计算运行时长
        duration_seconds = 0
        if self.start_time and self.end_time:
            duration_seconds = (self.end_time - self.start_time).total_seconds()
        
        # 估算月度调用量（基于当前频率）
        if duration_seconds > 0:
            calls_per_second = total_calls / duration_seconds
            monthly_calls = calls_per_second * 30 * 24 * 3600  # 30天
            monthly_tokens = monthly_calls * (total_tokens / total_calls)
        else:
            monthly_calls = 0
            monthly_tokens = 0
        
        return {
            'total_calls': total_calls,
            'successful_calls': successful_calls,
            'failed_calls': failed_calls,
            'success_rate': successful_calls / total_calls if total_calls > 0 else 0,
            'total_tokens': total_tokens,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'avg_response_time_ms': avg_response_time,
            'scenario_stats': scenario_stats,
            'duration_seconds': duration_seconds,
            'estimated_monthly_calls': int(monthly_calls),
            'estimated_monthly_tokens': int(monthly_tokens)
        }
    
    def print_summary(self):
        """打印统计摘要"""
        stats = self.get_statistics()
        
        print("\n" + "="*80)
        print("📊 调用统计摘要")
        print("="*80)
        print(f"总调用次数: {stats['total_calls']:,}")
        print(f"成功: {stats['successful_calls']:,} | 失败: {stats['failed_calls']:,}")
        print(f"成功率: {stats['success_rate']:.2%}")
        print(f"\nToken 使用统计:")
        print(f"  输入 Tokens: {stats['input_tokens']:,}")
        print(f"  输出 Tokens: {stats['output_tokens']:,}")
        print(f"  总计 Tokens: {stats['total_tokens']:,}")
        print(f"\n平均响应时间: {stats['avg_response_time_ms']:.2f}ms")
        print(f"运行时长: {stats['duration_seconds']:.2f}秒")
        
        print(f"\n📈 场景分布:")
        for scenario, data in stats['scenario_stats'].items():
            print(f"  {scenario}:")
            print(f"    调用次数: {data['calls']:,}")
            print(f"    Token 使用: {data['tokens']:,}")
            print(f"    平均上下文: {data['avg_context']:,.0f} tokens")
        
        print(f"\n🔮 月度预估:")
        print(f"  预估月度调用: {stats['estimated_monthly_calls']:,}")
        print(f"  预估月度 Token: {stats['estimated_monthly_tokens']:,}")
        print("="*80 + "\n")
