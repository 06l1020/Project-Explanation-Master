# Agent Manager 模块说明

## 📋 模块概述

`agent_manager.py` 是知识库管理智能体的核心模块，负责统一管理所有LLM调用和Agent交互。

### 核心功能

1. **统一LLM客户端管理** - 支持OpenAI及兼容API的服务
2. **四大专用Agent** - 项目分析、知识讲解、问答、进度更新
3. **提示词模板管理** - 集中管理所有Prompt模板
4. **动态模型切换** - 运行时更换模型配置

---

## 🏗️ 架构设计

```
┌─────────────────────────────────────┐
│       AgentManager (统一管理器)      │
├─────────────────────────────────────┤
│  LLM Client (ChatOpenAI)            │
│  ├─ OpenAI官方                       │
│  ├─ Azure OpenAI                    │
│  ├─ Ollama (本地)                   │
│  └─ DeepSeek/Qwen等                 │
├─────────────────────────────────────┤
│  Prompt Templates (提示词模板)       │
│  ├─ project_analysis                │
│  ├─ knowledge_teaching              │
│  ├─ qa                              │
│  └─ progress_update                 │
├─────────────────────────────────────┤
│  Chat History Manager               │
└─────────────────────────────────────┘
```

---

## 🚀 快速开始

### 1. 基础使用

```python
from core.agent_manager import AgentManager

# 初始化（API密钥可从环境变量OPENAI_API_KEY读取）
agent_mgr = AgentManager(
    api_key="sk-xxx",  # 可选
    model_name="gpt-4",
    temperature=0.7
)

# 项目分析
overview = agent_mgr.analyze_project(
    project_structure="...",
    dependencies="...",
    framework_detected="Spring Boot"
)

# 知识讲解
knowledge = agent_mgr.teach_knowledge(
    project_overview=overview,
    topic_title="Spring Boot自动配置",
    topic_description="..."
)

# 问答
answer = agent_mgr.answer_question(
    project_overview=overview,
    current_topic="Spring Boot自动配置",
    question="@ConditionalOnClass如何工作？"
)

# 更新进度
progress = agent_mgr.update_progress(
    current_topic="Spring Boot自动配置",
    current_summary="学习了...",
    existing_progress="..."
)
```

### 2. 使用自定义API端点

```python
# 使用Ollama本地服务
agent_mgr = AgentManager(
    api_key="ollama",
    base_url="http://localhost:11434/v1",
    model_name="llama2"
)

# 使用DeepSeek
agent_mgr = AgentManager(
    api_key="sk-xxx",
    base_url="https://api.deepseek.com/v1",
    model_name="deepseek-chat"
)
```

### 3. 动态切换模型

```python
# 运行时切换模型
agent_mgr.update_model_config(
    model_name="gpt-3.5-turbo",
    temperature=0.5
)
```

---

## 📝 API参考

### 初始化参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `api_key` | str | 从环境变量读取 | API密钥 |
| `base_url` | str | None | API基础URL，None则使用OpenAI官方端点 |
| `model_name` | str | "gpt-4" | 模型名称 |
| `temperature` | float | 0.7 | 温度参数(0-1) |

### 核心方法

#### 1. `analyze_project()` - 项目分析Agent

**功能：** 分析Java项目框架和技术栈，生成overview.md

**参数：**
- `project_structure` (str): 项目结构信息
- `dependencies` (str): 依赖项列表
- `framework_detected` (str): 检测到的框架
- `code_samples` (str): 关键代码片段

**返回：** overview.md的完整内容

---

#### 2. `teach_knowledge()` - 知识讲解Agent

**功能：** 结合项目代码讲解知识点，生成note/{topic}.md

**参数：**
- `project_overview` (str): 项目概览（overview.md内容）
- `topic_title` (str): 知识点标题
- `topic_description` (str): 知识点描述
- `learned_topics` (str): 已学习的知识点列表
- `project_code_context` (str): 项目相关代码上下文

**返回：** 知识点讲解的Markdown内容

---

#### 3. `answer_question()` - 问答Agent

**功能：** 回答用户关于当前知识点的问题

**参数：**
- `project_overview` (str): 项目概览
- `current_topic` (str): 当前知识点
- `question` (str): 用户问题
- `conversation_history` (List[Dict]): 对话历史（可选）

**返回：** 结构化的回答内容

**注意：** 自动维护聊天历史，调用`clear_chat_history()`可清除

---

#### 4. `update_progress()` - 进度更新Agent

**功能：** 更新overview.md中的"已学习内容"部分

**参数：**
- `current_topic` (str): 刚完成的知识点
- `current_summary` (str): 知识点总结
- `existing_progress` (str): 现有学习进度内容
- `topic_code_examples` (str): 关键代码示例

**返回：** 更新后的"已学习内容"部分内容

---

#### 5. `clear_chat_history()` - 清除聊天历史

**功能：** 切换知识点时清除对话上下文

**用法：**
```python
agent_mgr.clear_chat_history()
```

---

#### 6. `update_model_config()` - 更新模型配置

**功能：** 运行时动态切换模型配置

**参数：**
- `api_key` (str, 可选): 新的API密钥
- `base_url` (str, 可选): 新的API基础URL
- `model_name` (str, 可选): 新的模型名称
- `temperature` (float, 可选): 新的温度参数

**用法：**
```python
agent_mgr.update_model_config(
    model_name="gpt-3.5-turbo",
    temperature=0.5
)
```

---

## 🎯 提示词模板详解

### 1. 项目分析模板 (`project_analysis`)

**输入变量：**
- `project_structure`: 项目包结构和文件列表
- `dependencies`: Maven/Gradle依赖
- `framework_detected`: 检测到的框架和技术栈
- `code_samples`: 关键代码片段（启动类、Controller等）

**输出格式：**
- 技术栈分析表格
- 分阶段学习路线图
- 代码索引表格
- 初始化的"已学习内容"章节

---

### 2. 知识讲解模板 (`knowledge_teaching`)

**输入变量：**
- `project_overview`: 项目概览全文
- `topic_title`: 知识点标题
- `topic_description`: 知识点描述
- `learned_topics`: 已学知识点列表
- `project_code_context`: 项目相关代码

**输出格式（七段式）：**
1. 概念解释与重要性
2. 核心原理大白话
3. 项目实战演练
4. 常见陷阱与解决方案
5. 进阶技巧
6. 知识扩展
7. 小结与下一步

---

### 3. 问答模板 (`qa`)

**输入变量：**
- `project_overview`: 项目概览
- `current_topic`: 当前知识点
- `question`: 用户问题
- `conversation_history`: 对话历史（最近5轮）

**输出格式：**
- 核心答案（1-2句）
- 详细说明
- 代码示例
- 项目应用
- 常见误区
- 延伸阅读
- 思考题

---

### 4. 进度更新模板 (`progress_update`)

**输入变量：**
- `current_topic`: 刚完成的知识点
- `current_summary`: 知识点总结
- `existing_progress`: 现有进度内容
- `topic_code_examples`: 关键代码示例

**输出格式：**
- 时间倒序的学习历程
- 星级评分（1-5星）
- 精简代码示例（≤30行）
- 掌握程度评估
- 下一步建议

---

## 🔧 最佳实践

### 1. Token优化策略

```python
# ✅ 好的做法：只传递必要的上下文
knowledge = agent_mgr.teach_knowledge(
    project_overview=overview[:5000],  # 截断过长的概览
    topic_title="Spring Boot",
    project_code_context=extract_relevant_code(topic)  # 只提取相关代码
)

# ❌ 避免：传递大量无关数据
knowledge = agent_mgr.teach_knowledge(
    project_overview=huge_overview,  # 可能超过Token限制
    project_code_context=all_project_code  # 包含所有代码
)
```

---

### 2. 错误处理

```python
try:
    overview = agent_mgr.analyze_project(...)
except Exception as e:
    print(f"项目分析失败: {e}")
    # 记录日志或显示用户友好的错误信息
```

---

### 3. 聊天历史管理

```python
# 切换知识点时务必清除历史
def switch_to_next_topic():
    agent_mgr.clear_chat_history()  # ← 重要！
    knowledge = agent_mgr.teach_knowledge(...)
```

---

### 4. 模型选择建议

| 场景 | 推荐模型 | 原因 |
|------|---------|------|
| 项目分析 | gpt-4 / gpt-4-turbo | 需要深度理解和结构化输出 |
| 知识讲解 | gpt-4 / gpt-3.5-turbo | 平衡质量和成本 |
| 问答互动 | gpt-3.5-turbo | 响应速度快，成本低 |
| 本地测试 | ollama/llama2 | 免费，离线可用 |

---

## 📦 依赖要求

```txt
langchain>=0.1.0
langchain-openai>=0.0.5
openai>=1.0.0
tiktoken>=0.5.0
```

安装命令：
```bash
pip install langchain langchain-openai openai tiktoken
```

---

## 🔍 常见问题

### Q1: 如何使用Azure OpenAI？

```python
agent_mgr = AgentManager(
    api_key="your-azure-key",
    base_url="https://your-resource.openai.azure.com/openai/deployments/your-deployment",
    model_name="gpt-4"
)
```

---

### Q2: 如何降低Token消耗？

1. 截断过长的`project_overview`（保留关键部分）
2. 只提取与当前知识点相关的代码
3. 限制`conversation_history`为最近5轮
4. 使用gpt-3.5-turbo进行简单任务

---

### Q3: 提示词输出格式不符合预期怎么办？

1. 检查是否包含了Markdown代码块标记（```）在模板中
2. 确保所有`{variable}`都在`input_variables`中声明
3. 调整`temperature`参数（降低可提高稳定性）
4. 在Prompt中增加更明确的格式说明

---

### Q4: 如何在GUI中使用？

参见 `gui/main_window.py` 中的集成示例，关键点：
- 使用`threading.Thread`在后台执行LLM调用
- 使用`root.after(0, callback)`更新UI
- 禁用按钮防止重复触发

---

## 📚 相关模块

- [`core/project_analyzer.py`](../core/project_analyzer.py) - Java项目静态分析器
- [`core/orchestrator.py`](../core/orchestrator.py) - 业务流程编排器
- [`config/knowledge_tree.json`](../config/knowledge_tree.json) - 知识点配置文件
- [`gui/main_window.py`](../gui/main_window.py) - GUI主界面

---

## 📝 更新日志

### v1.0.0 (2024-01-XX)
- ✅ 实现四大Agent封装
- ✅ 支持动态模型切换
- ✅ 集成LangChain新版API
- ✅ 提供完整的提示词模板
- ✅ 聊天历史自动管理
