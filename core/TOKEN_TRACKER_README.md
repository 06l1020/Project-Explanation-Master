# Token消耗记录功能说明

## 概述

Token消耗记录功能用于追踪和管理所有LLM调用的token使用情况，帮助用户：
- 实时监控API调用成本
- 分析不同操作的token消耗模式
- 优化模型使用策略，节省API费用
- 生成详细的消耗报告

---

## 核心组件

### 1. TokenUsageRecord 类

**位置：** `core/token_tracker.py`

**功能：** 表示单次token使用记录

**属性：**
- `operation`: 操作类型（项目分析/知识点讲解/问答/进度更新）
- `model`: 使用的模型名称
- `prompt_tokens`: 输入token数
- `completion_tokens`: 输出token数
- `total_tokens`: 总token数
- `timestamp`: 时间戳（ISO格式）

**方法：**
- `to_dict()`: 转换为字典格式
- `from_dict(data)`: 从字典创建记录

---

### 2. TokenUsageTracker 类

**位置：** `core/token_tracker.py`

**功能：** 管理和追踪所有token使用记录

**主要方法：**

#### add_record()
添加token使用记录
```python
tracker.add_record(
    operation="项目分析",
    model="gpt-4",
    prompt_tokens=1000,
    completion_tokens=500,
    total_tokens=1500
)
```

#### get_total_usage()
获取累计token使用量
```python
total = tracker.get_total_usage()
# 返回: {
#     'total_prompt_tokens': 1200,
#     'total_completion_tokens': 800,
#     'total_tokens': 2000,
#     'call_count': 2
# }
```

#### get_usage_by_operation()
按操作类型统计
```python
stats = tracker.get_usage_by_operation()
# 返回按操作类型分组的统计信息
```

#### generate_report()
生成Markdown格式的详细报告
```python
report = tracker.generate_report()
```

#### clear_records()
清空所有记录

---

## 集成到系统

### AgentManager 集成

在 `AgentManager.__init__()` 中初始化：
```python
self.token_tracker = TokenUsageTracker(project_path=project_path)
```

在每个LLM调用方法中记录token消耗：
```python
response = self.llm.invoke(prompt)

# 记录token消耗
if hasattr(response, 'response_metadata') and 'token_usage' in response.response_metadata:
    token_usage = response.response_metadata['token_usage']
    self.token_tracker.add_record(
        operation="项目分析",
        model=self.model_name,
        prompt_tokens=token_usage.get('prompt_tokens', 0),
        completion_tokens=token_usage.get('completion_tokens', 0),
        total_tokens=token_usage.get('total_tokens', 0)
    )
```

### Orchestrator 集成

提供获取token信息的方法：
```python
def get_token_usage(self) -> Dict:
    """获取token使用情况"""
    return self.agent_mgr.token_tracker.get_total_usage()

def get_token_records(self) -> List[Dict]:
    """获取token使用记录列表"""
    return self.agent_mgr.token_tracker.get_records()

def get_token_report(self) -> str:
    """获取token使用报告"""
    return self.agent_mgr.token_tracker.generate_report()
```

---

## GUI 实现

### Token消耗Tab

**位置：** GUI主窗口的第4个Tab

**界面元素：**
1. **统计信息标签**：显示总调用次数和总Token消耗
2. **Treeview表格**：展示详细记录
   - 时间
   - 操作类型
   - 模型名称
   - 输入Token
   - 输出Token
   - 总Token
3. **功能按钮**：
   - 生成Token报告
   - 清空记录

### 自动更新时机

Token消耗显示在以下操作后自动更新：
- 项目分析完成
- 知识点讲解完成
- 问答回答完成

---

## 数据持久化

### 存储位置

Token记录保存到项目根目录的 `token_usage.json` 文件：
```
java-project/
├── overview.md
├── token_usage.json    # Token消耗记录
└── note/
    └── ...
```

### 文件格式

```json
[
  {
    "operation": "项目分析",
    "model": "gpt-4",
    "prompt_tokens": 1234,
    "completion_tokens": 567,
    "total_tokens": 1801,
    "timestamp": "2024-01-15T10:30:00"
  },
  ...
]
```

### 自动加载

创建 `TokenUsageTracker` 实例时，如果 `token_usage.json` 存在，会自动加载历史记录。

---

## 使用示例

### 代码示例

```python
from core.orchestrator import AgentOrchestrator

# 创建编排器
orchestrator = AgentOrchestrator(
    project_path="/path/to/project",
    api_key="sk-xxx"
)

# 执行项目分析
orchestrator.analyze_project()

# 查看token使用情况
token_usage = orchestrator.get_token_usage()
print(f"总调用次数: {token_usage['call_count']}")
print(f"总Token消耗: {token_usage['total_tokens']}")

# 查看详细记录
records = orchestrator.get_token_records()
for record in records:
    print(f"{record['operation']}: {record['total_tokens']} tokens")

# 生成报告
report = orchestrator.get_token_report()
print(report)
```

---

## Token成本估算

### OpenAI 模型定价（参考）

| 模型 | 输入Token价格 | 输出Token价格 |
|------|--------------|--------------|
| GPT-4 | $0.03/1K | $0.06/1K |
| GPT-4-turbo | $0.01/1K | $0.03/1K |
| GPT-3.5-turbo | $0.001/1K | $0.002/1K |

### 典型操作消耗

| 操作 | 预估Token | GPT-4成本 | GPT-3.5成本 |
|------|-----------|-----------|-------------|
| 项目分析 | 5000-8000 | $0.15-$0.24 | $0.01-$0.016 |
| 知识点讲解 | 4000-6000 | $0.12-$0.18 | $0.008-$0.012 |
| 回答问题 | 1500-3000 | $0.045-$0.09 | $0.003-$0.006 |
| 进度更新 | 2000-3000 | $0.06-$0.09 | $0.004-$0.006 |

---

## 优化建议

### 1. 模型选择策略
- **项目分析**：使用GPT-4（质量优先）
- **知识点讲解**：使用GPT-3.5-turbo（成本优化）
- **问答互动**：使用GPT-3.5-turbo（速度快、成本低）

### 2. 避免重复调用
- 项目只需分析一次
- 使用缓存的overview.md作为上下文
- 切换知识点时清除聊天历史

### 3. 监控和报告
- 定期检查Token消耗Tab
- 使用"生成Token报告"功能导出记录
- 根据消耗情况调整使用策略

---

## 故障排除

### 问题1：Token记录未保存

**原因：**
- 项目路径未正确设置
- 文件权限问题

**解决方案：**
```python
# 确保创建orchestrator时传入project_path
orchestrator = AgentOrchestrator(
    project_path="/path/to/project",
    api_key="sk-xxx"
)
```

### 问题2：Token信息显示为0

**原因：**
- LangChain版本不支持token_usage元数据
- 模型提供商不返回token使用信息

**解决方案：**
- 确保使用 `langchain-openai>=0.0.5`
- 检查 `response.response_metadata` 中是否有 `token_usage` 字段

### 问题3：报告生成失败

**原因：**
- 记录数据格式不正确

**解决方案：**
- 检查 `token_usage.json` 文件格式
- 确保所有必需字段都存在

---

## 单元测试

运行测试验证功能：
```bash
python -m pytest tests/test_token_tracker.py -v
```

测试覆盖：
- TokenUsageRecord 创建和序列化
- TokenUsageTracker 添加记录
- 累计统计计算
- 按操作类型分组统计
- 数据持久化（保存/加载）
- 报告生成
- 记录清空

---

## 未来改进方向

1. **实时成本计算**
   - 根据当前模型定价自动计算美元成本
   - 显示预估费用

2. **可视化图表**
   - Token消耗趋势图
   - 操作类型饼图
   - 模型使用对比图

3. **告警功能**
   - 设置Token消耗阈值
   - 超出阈值时发出警告

4. **导出功能**
   - 导出为CSV格式
   - 导出为Excel报表
   - 支持自定义报告模板

5. **批量操作优化**
   - 批量分析多个项目
   - 汇总统计报告

---

## 相关文档

- [`GUI_USAGE_GUIDE.md`](../gui/GUI_USAGE_GUIDE.md) - GUI使用指南
- [`AGENT_MANAGER_README.md`](../core/AGENT_MANAGER_README.md) - Agent管理器文档
- [`ORCHESTRATOR_README.md`](../core/ORCHESTRATOR_README.md) - 编排器文档
