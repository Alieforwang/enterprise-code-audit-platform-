"""
企业级代码审计平台 - 测试脚本
全自动运行代码审计测试，产生详细日志用于申请小米模型 Token
"""

import time
import random
import yaml
import asyncio
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from openai import OpenAI
except ImportError:
    print("请先安装依赖: pip install -r requirements.txt")
    exit(1)

from logger import AuditLogger
from report_generator import ReportGenerator, generate_text_summary


class CodeAuditDemo:
    """代码审计平台测试"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self.logger = AuditLogger(self.config['logging']['output_dir'])
        
        # 初始化 API 客户端
        api_config = self.config['api']
        if api_config['provider'] == 'openai':
            self.client = OpenAI(
                base_url=api_config['base_url'],
                api_key=api_config['api_key']
            )
        self.model = api_config['model']
        
        # 加载代码库（真实路径或模拟数据）
        self.codebase = self._load_codebase()
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _load_codebase(self) -> List[Dict[str, Any]]:
        """加载代码库（真实路径或模拟数据）"""
        codebase_config = self.config['codebase']
        codebase_path = codebase_config.get('path', '').strip()
        
        if codebase_path:
            # 读取真实代码库
            return self._load_real_codebase(codebase_path)
        else:
            # 使用模拟数据
            return self._generate_mock_codebase()
    
    def _load_real_codebase(self, codebase_path: str) -> List[Dict[str, Any]]:
        """读取真实代码库"""
        from pathlib import Path
        import fnmatch
        
        codebase_config = self.config['codebase']
        exclude_patterns = codebase_config.get('exclude', [])
        extensions = codebase_config.get('extensions', ['.py', '.js', '.ts', '.java', '.go'])
        
        base_path = Path(codebase_path)
        if not base_path.exists():
            print(f"⚠️  代码库路径不存在: {codebase_path}，使用模拟数据")
            return self._generate_mock_codebase()
        
        codebase = []
        
        # 遍历文件
        for file_path in base_path.rglob('*'):
            if not file_path.is_file():
                continue
            
            # 检查扩展名
            if file_path.suffix.lower() not in extensions:
                continue
            
            # 检查排除规则
            relative_path = file_path.relative_to(base_path)
            should_exclude = False
            for pattern in exclude_patterns:
                if fnmatch.fnmatch(str(relative_path), pattern) or fnmatch.fnmatch(file_path.name, pattern):
                    should_exclude = True
                    break
            
            if should_exclude:
                continue
            
            # 读取文件内容
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except Exception as e:
                print(f"⚠️  无法读取文件 {file_path}: {e}")
                continue
            
            # 估算 token 数量（粗略估算：字符数 / 4）
            estimated_tokens = len(content) // 4
            
            codebase.append({
                'id': str(file_path),
                'name': str(relative_path),
                'tokens': estimated_tokens,
                'content': content
            })
        
        if not codebase:
            print(f"⚠️  未找到符合条件的代码文件，使用模拟数据")
            return self._generate_mock_codebase()
        
        total_tokens = sum(f['tokens'] for f in codebase)
        print(f"📁 已加载真实代码库: {len(codebase)} 个文件，总 {total_tokens:,} tokens")
        print(f"   路径: {codebase_path}")
        
        return codebase
    
    def _generate_mock_codebase(self) -> List[Dict[str, Any]]:
        """生成模拟代码库"""
        codebase_config = self.config['codebase'].get('mock', {})
        file_count = codebase_config.get('file_count', 50)
        avg_tokens = codebase_config.get('avg_tokens_per_file', 5000)
        
        codebase = []
        file_types = ['.py', '.js', '.java', '.go', '.ts']
        
        for i in range(file_count):
            file_tokens = int(avg_tokens * random.uniform(0.5, 2.0))
            codebase.append({
                'id': f"file_{i}",
                'name': f"module_{i // 10}/feature_{i % 10}/code{file_types[i % len(file_types)]}",
                'tokens': file_tokens,
                'content': f"# Mock code content for file {i}\n" + "# " * (file_tokens // 10)
            })
        
        print(f"📁 已生成模拟代码库: {file_count} 个文件，总 {sum(f['tokens'] for f in codebase):,} tokens")
        return codebase
    
    def _select_scenario(self) -> str:
        """根据权重随机选择场景"""
        scenarios = self.config['scenarios']
        enabled_scenarios = [(k, v) for k, v in scenarios.items() if v['enabled']]
        
        if not enabled_scenarios:
            return 'code_review'
        
        total_weight = sum(v['weight'] for _, v in enabled_scenarios)
        r = random.uniform(0, total_weight)
        
        current = 0
        for scenario, config in enabled_scenarios:
            current += config['weight']
            if r <= current:
                return scenario
        
        return enabled_scenarios[0][0]
    
    def _generate_prompt(self, scenario: str, context_size: int) -> tuple[str, str]:
        """生成提示词"""
        # 选择文件以构建上下文
        selected_files = random.sample(
            self.codebase, 
            min(len(self.codebase), max(1, context_size // 5000))
        )
        
        # 构建上下文
        context = "\n".join([
            f"// File: {f['name']}\n{f['content'][:500]}"
            for f in selected_files
        ])
        
        # 根据场景生成不同的任务描述
        task_descriptions = {
            'code_review': (
                "请对以下代码进行全面的代码审查，识别潜在的安全漏洞、"
                "性能问题、代码规范违规，并提供改进建议。"
            ),
            'cross_file_analysis': (
                "分析以下多个文件之间的依赖关系，识别循环依赖、"
                "耦合度过高的问题，并给出重构建议。"
            ),
            'bug_fix_suggestion': (
                "以下代码中存在潜在的 Bug，请分析问题并提供修复方案。"
            ),
            'logic_orchestration': (
                "基于以下代码的业务逻辑，设计一个自动化重构方案，"
                "包括具体的重构步骤和验证方法。"
            )
        }
        
        task_desc = task_descriptions.get(scenario, "代码分析任务")
        
        prompt = f"""{task_desc}

代码上下文：
{context}

请提供详细的分析结果和建议。"""
        
        return prompt, task_desc
    
    def _call_api(self, scenario: str, context_size: int) -> Dict[str, Any]:
        """调用 API"""
        prompt, task_desc = self._generate_prompt(scenario, context_size)
        
        start_time = time.time()
        success = True
        error_message = None
        retry_count = 0
        input_tokens = len(prompt) // 4  # 估算
        output_tokens = 0
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的代码审计专家。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=min(4096, context_size // 2),
                temperature=0.7
            )
            
            output_tokens = response.usage.completion_tokens
            input_tokens = response.usage.prompt_tokens
            
        except Exception as e:
            success = False
            error_message = str(e)
            print(f"❌ API 调用失败: {error_message}")
        
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # 记录日志
        self.logger.log_call(
            scenario=scenario,
            task_description=task_desc,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            context_window=context_size,
            response_time_ms=response_time_ms,
            success=success,
            model=self.model,
            error_message=error_message,
            retry_count=retry_count
        )
        
        return {
            'success': success,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'response_time_ms': response_time_ms
        }
    
    def run_demo(self):
        """运行测试"""
        print("\n" + "="*80)
        print("🚀 企业级代码审计平台 - 测试开始")
        print("="*80)
        print(f"📅 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🤖 使用模型: {self.model}")
        print(f"📋 运行模式: {self.config['runtime']['mode']}")
        
        runtime_config = self.config['runtime']
        scenarios_config = self.config['scenarios']
        
        self.logger.start_session()
        
        call_count = 0
        start_time = time.time()
        
        try:
            if runtime_config['mode'] == 'count':
                # 按调用次数运行
                call_limit = runtime_config['call_limit']
                print(f"🎯 目标调用次数: {call_limit:,}")
                
                for i in range(call_limit):
                    scenario = self._select_scenario()
                    context_size = scenarios_config[scenario]['context_size']
                    
                    print(f"\n[{i+1}/{call_limit}] 执行场景: {scenario}")
                    self._call_api(scenario, context_size)
                    call_count += 1
                    
                    # 避免过快调用
                    if i < call_limit - 1:
                        time.sleep(random.uniform(0.5, 2.0))
                
            elif runtime_config['mode'] == 'duration':
                # 按时长运行
                duration_limit = runtime_config['duration_limit']
                print(f"⏱️  目标运行时长: {duration_limit} 秒")
                
                while (time.time() - start_time) < duration_limit:
                    scenario = self._select_scenario()
                    context_size = scenarios_config[scenario]['context_size']
                    
                    print(f"\n[{call_count+1}] 执行场景: {scenario}")
                    self._call_api(scenario, context_size)
                    call_count += 1
                    
                    time.sleep(random.uniform(0.5, 2.0))
            
        except KeyboardInterrupt:
            print("\n\n⚠️  用户中断测试")
        
        self.logger.end_session()
        self.logger.save_logs()
        self.logger.print_summary()
        
        # 生成报告
        if self.config['logging']['generate_report']:
            print("\n📊 生成统计报告...")
            generator = ReportGenerator(self.logger)
            generator.generate_markdown_report()
            generate_text_summary(self.logger)
        
        print("\n" + "="*80)
        print("✅ 测试完成")
        print("="*80)


def main():
    """主函数"""
    import sys
    
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
    
    if not Path(config_path).exists():
        print(f"❌ 配置文件不存在: {config_path}")
        print("请先创建 config.yaml 文件并配置 API Key")
        return
    
    demo = CodeAuditDemo(config_path)
    demo.run_demo()


if __name__ == "__main__":
    main()
