# 企业级代码审计平台 - 小米模型 Token 申请测试

本项目用于测试企业级代码审计平台的使用场景，产生详细的 API 调用日志，展示平台在大规模代码分析场景下的实际需求。

## 项目背景

我们正在开发一个企业级的自动化代码审计与重构平台，核心痛点包括：
- 现有模型在处理大型单体仓库时，上下文窗口严重不足
- 高频 API 调用成本过高，限制了全量代码扫描的规模化落地
- 跨文件依赖分析经常"失忆"

计划迁移至小米 **MiMo-V2.5-Pro**，利用其 **1M Token 超长上下文** 和强大的 **Agent 编程能力**。

## 功能特性

- 🚀 **全自动运行**: 一键启动，无需手动干预
- 📊 **详细日志**: 记录所有 API 调用的关键指标
- 📈 **统计报告**: 自动生成专业的 Markdown 报告
- 🎯 **场景模拟**: 覆盖代码审查、跨文件分析、Bug 修复、逻辑编排等核心场景
- 🔧 **灵活配置**: 支持多种运行模式和参数调整

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

编辑 `config.yaml` 文件，替换 `YOUR_API_KEY_HERE` 为你的 API Key：

```yaml
api:
  provider: "openai"
  api_key: "sk-xxxxxxxxxxxxxxxxxxxxxxxx"  # 替换为实际的 API Key
  model: "gpt-4-turbo-preview"
```

### 3. 运行测试

```bash
python demo_audit_platform.py
```

## 配置说明

### 运行模式

在 `config.yaml` 中配置运行模式：

```yaml
runtime:
  mode: "count"  # 或 "duration"
  call_limit: 100  # 按次数模式时的调用次数
  duration_limit: 3600  # 按时长模式时的运行时长（秒）
```

### 场景配置

可以启用/禁用不同的场景，并调整权重：

```yaml
scenarios:
  code_review:
    enabled: true
    weight: 0.4  # 占总调用的 40%
    context_size: 100000  # 测试 100K tokens 上下文
  
  cross_file_analysis:
    enabled: true
    weight: 0.3
    context_size: 200000  # 测试 200K tokens 上下文
```

## 输出结果

运行后会在 `logs/` 目录下生成：

- `audit_calls.json`: 详细的 API 调用日志（JSON 格式）
- `statistics_report.md`: 专业的统计报告（Markdown 格式）
- `summary.txt`: 文本格式的统计摘要

## 统计报告内容

报告包含以下信息：

1. **项目概述**: 平台功能和核心场景
2. **API 调用统计**: 总调用次数、成功率、Token 使用量等
3. **场景分布**: 各场景的调用次数和 Token 使用
4. **月度预估**: 基于当前频率推算的月度调用量
5. **技术需求说明**: 超长上下文需求、Agent 能力需求、成本效益分析
6. **技术总结**: 平台架构和预期收益

## 预期调用量

基于测试数据的预估：
- **月度调用次数**: 数十万至数百万次
- **月度 Token 使用量**: 1亿 - 5亿 Tokens

## 文件结构

```
审查/
├── demo_audit_platform.py    # 主测试脚本
├── logger.py                  # 日志系统
├── report_generator.py        # 报告生成器
├── config.yaml                # 配置文件
├── requirements.txt           # 依赖
├── README.md                  # 本文件
└── logs/                      # 日志输出目录
    ├── audit_calls.json
    ├── statistics_report.md
    └── summary.txt
```

## 注意事项

1. **API Key 安全**: 请勿将包含真实 API Key 的配置文件提交到版本控制
2. **成本控制**: 根据实际预算调整 `call_limit` 或 `duration_limit`
3. **网络稳定**: 确保网络连接稳定，避免调用失败
4. **日志备份**: 重要日志建议定期备份

## 技术栈

- Python 3.8+
- OpenAI API (临时替代)
- YAML (配置管理)
- Rich (终端美化)

## 后续计划

后续优化方向：
1. 集成支持超长上下文的大模型接口
2. 利用大上下文能力进行真实的大规模代码分析
3. 优化 Agent 工作流，提升任务执行效率

## 联系方式

如有问题或需要技术支持，请联系项目团队。
