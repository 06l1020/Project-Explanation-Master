# Agent Orchestrator 模块说明

## 📋 模块概述

`orchestrator.py` 是业务流程编排器，整合AgentManager和ContextManager，实现完整的智能教学流程。

### 核心职责

1. **流程管理** - 协调项目分析、知识讲解、问答互动
2. **状态机** - 管理业务状态转换（IDLE → ANALYZING → TEACHING → QA）
3. **文件IO** - 生成和更新Markdown文件
4. **错误处理** - 统一的异常处理和用户反馈

---

## 🏗️ 架构设计

```
┌──────────────────────────────────────┐
│      AgentOrchestrator (编排器)       │
├──────────────────────────────────────┤
│  State Machine                       │
│  IDLE → ANALYZING → TEACHING → QA   │
├──────────────┬───────────────────────┤
│ AgentManager │  ContextManager       │
│              │                       │
│ • 项目分析    │ • 代码索引            │
│ • 知识讲解    │ • 进度跟踪            │
│ • 问答       │ • 智能推荐            │
│ • 进度更新    │                       │
├──────────────┴───────────────────────┤
│  File System                         │
│  • overview.md                       │
│  • note/{topic}.md                   │
│  • learning_progress.json            │
└──────────────────────────────────────┘
```

---

## 🚀 快速开始

### 1. 基础使用

```python
from core.orchestrator import AgentOrchestrator

# 初始化
orchestrator = AgentOrchestrator(
    project_path="path/to/java/project",
    api_key="your-api-key",
    model_name="gpt-4"
)

# 分析项目
result = orchestrator.analyze_project()
print(f"框架: {result['framework']}")

# 学习知识点
topic = orchestrator.next_topic()
if topic:
    print(f"学习了: {topic['topic']['title']}")
    
    # 提问
    answer = orchestrator.answer_question("这个知识点如何工作？")
    print(answer)

# 查看进度
progress = orchestrator.get_progress()
print(f"完成度: {progress['progress_percentage']}%")
```

---

### 2. 完整工作流程

```python
orchestrator = AgentOrchestrator(
    project_path="path/to/java/project",
    api_key="your-api-key"
)

# 阶段1: 项目分析
orchestrator.analyze_project()

# 阶段2: 循环学习知识点
while True:
    topic = orchestrator.next_topic()
    
    if topic is None:
        print("🎉 所有知识点已完成！")
        break
    
    print(f"📚 当前知识点: {topic['topic']['title']}")
    
    # 问答环节
    while True:
        question = input("你的问题（输入'next'继续）: ")
        
        if question.lower() == 'next':
            break
        
        answer = orchestrator.answer_question(question)
        print(f"🤖 {answer}\n")

# 阶段3: 查看总结
progress = orchestrator.get_progress()
print(f"学习完成度: {progress['progress_percentage']}%")
```

---

## 📝 API参考

### 初始化

```python
orchestrator = AgentOrchestrator(
    project_path: str,              # Java项目根目录
    api_key: Optional[str] = None,  # API密钥（可从环境变量读取）
    base_url: Optional[str] = None, # API基础URL
    model_name: str = "gpt-4",      # 模型名称
    temperature: float = 0.7,       # 温度参数
    knowledge_tree_path: Optional[str] = None  # 知识点配置文件路径
)
```

---

### analyze_project()

分析Java项目并生成overview.md

```python
result = orchestrator.analyze_project() -> Dict
```

**返回示例：**
```python
{
    "status": "success",
    "framework": "Spring Boot",
    "build_tool": "Maven",
    "timestamp": "2024-01-15T14:30:00"
}
```

**生成的文件：**
- `project_path/overview.md` - 项目分析报告

**异常：**
- `RuntimeError`: 分析失败时抛出

---

### next_topic()

获取并讲解下一个知识点

```python
topic_result = orchestrator.next_topic() -> Optional[Dict]
```

**返回示例：**
```python
{
    "topic": {
        "id": "spring_boot",
        "title": "Spring Boot框架",
        "difficulty": 2
    },
    "note_file": "/path/to/note/spring_boot.md",
    "content": "# Spring Boot框架\n\n..."
}
```

**无更多知识点时返回：** `None`

**生成的文件：**
- `project_path/note/{topic_id}.md` - 知识点讲解
- 更新 `project_path/overview.md` 中的进度部分

---

### answer_question()

回答用户关于当前知识点的问题

```python
answer = orchestrator.answer_question(question: str) -> str
```

**参数：**
- `question`: 用户问题

**返回：** AI的结构化回答

**前置条件：**
- 必须先调用 `next_topic()`
- 状态必须为 `QA`

**异常：**
- `RuntimeError`: 状态不正确时抛出

---

### update_model_config()

动态更新模型配置

```python
orchestrator.update_model_config(
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    model_name: Optional[str] = None,
    temperature: Optional[float] = None
)
```

**用途：**
- 运行时切换模型（如GPT-4 → GPT-3.5）
- 调整温度参数
- 更换API端点

---

### get_progress()

获取学习进度

```python
progress = orchestrator.get_progress() -> Dict
```

**返回示例：**
```python
{
    "total_topics": 10,
    "completed_topics": 3,
    "progress_percentage": 30.0,
    "learned_topics": ["core_java", "maven", "spring_boot"],
    "next_topic": {...}
}
```

---

### get_current_state()

获取当前状态

```python
state = orchestrator.get_current_state() -> str
```

**可能的状态：**
- `"idle"` - 空闲
- `"analyzing"` - 分析中
- `"teaching"` - 讲解中
- `"qa"` - 问答模式
- `"error"` - 错误状态

---

### reset()

重置编排器状态

```python
orchestrator.reset()
```

**效果：**
- 状态回到 `IDLE`
- 清除当前知识点
- 清空聊天历史

---

## 🔄 状态机流转

```
     ┌─────────┐
     │  IDLE   │◄──────────────────┐
     └────┬────┘                   │
          │ analyze_project()      │
          ▼                        │
   ┌──────────────┐                │
   │  ANALYZING   │                │
   └──────┬───────┘                │
          │ 成功                    │ reset()
          ▼                        │
     ┌──────────┐                  │
     │  IDLE    │                  │
     └────┬─────┘                  │
          │ next_topic()           │
          ▼                        │
   ┌─────────────┐                 │
   │  TEACHING   │                 │
   └──────┬──────┘                 │
          │ 完成                    │
          ▼                        │
     ┌─────────┐                   │
     │   QA    │───────────────────┘
     └────┬────┘
          │ next_topic()
          │ 或所有知识点完成
          ▼
     ┌─────────┐
     │  IDLE   │
     └─────────┘
```

---

## 📂 生成的文件结构

```
java-project/
├── overview.md                    # 项目分析报告
├── note/                          # 知识点讲解目录
│   ├── core_java.md
│   ├── spring_boot.md
│   ├── spring_boot_web.md
│   └── ...
└── learning_progress.json         # 学习进度（由ContextManager生成）
```

### overview.md 结构

```markdown
# [项目名称] - Java企业级项目学习指南

## 一、项目框架及技术栈分析
...

## 二、学习路线图
...

## 三、已学习内容
> 📝 **说明**：...

**当前状态：** 🚀 学习中
**学习统计：** 已完成 3/10 个知识点（30%）

### 学习历程

#### 1. Java核心基础 ✅
**完成时间：** 2024-01-15 14:30:00
**核心收获：** ...
**掌握程度：** ⭐⭐⭐⭐☆ (4/5)

---

#### 2. Maven构建工具 ✅
...

## 四、项目代码索引
...
```

### note/{topic}.md 结构

参见 [`AGENT_MANAGER_README.md`](./AGENT_MANAGER_README.md) 中的知识点讲解模板。

---

## 🎯 最佳实践

### 1. 分阶段使用不同模型

```python
# 项目分析使用高质量模型
orchestrator = AgentOrchestrator(
    project_path=path,
    model_name="gpt-4",
    temperature=0.7
)
orchestrator.analyze_project()

# 知识点讲解切换到快速模型
orchestrator.update_model_config(
    model_name="gpt-3.5-turbo",
    temperature=0.7
)

# 循环讲解知识点
while True:
    topic = orchestrator.next_topic()
    if not topic:
        break
```

**优势：**
- GPT-4用于复杂分析（质量优先）
- GPT-3.5用于常规讲解（成本优化）
- 预计节省 **60%** 的API费用

---

### 2. 错误处理

```python
try:
    orchestrator.analyze_project()
except RuntimeError as e:
    print(f"❌ 分析失败: {e}")
    print("建议: 检查项目路径和API密钥")
except FileNotFoundError as e:
    print(f"❌ 文件缺失: {e}")
    print("建议: 确认knowledge_tree.json存在")
```

---

### 3. 进度持久化

```python
import json

# 定期保存进度
def save_checkpoint():
    progress = orchestrator.get_progress()
    with open("checkpoint.json", "w") as f:
        json.dump(progress, f)

# 每完成一个知识点保存
topic = orchestrator.next_topic()
if topic:
    save_checkpoint()
```

---

### 4. GUI集成要点

```python
import threading
import tkinter as tk

class MainWindow:
    def __init__(self):
        self.orchestrator = None
        self.root = tk.Tk()
    
    def start_analysis(self):
        """异步启动分析"""
        # 禁用按钮
        self.analyze_btn.config(state=tk.DISABLED)
        
        # 后台线程执行
        thread = threading.Thread(target=self._do_analysis, daemon=True)
        thread.start()
    
    def _do_analysis(self):
        try:
            result = self.orchestrator.analyze_project()
            
            # 主线程更新UI
            self.root.after(0, lambda: self._on_analysis_complete(result))
        except Exception as e:
            self.root.after(0, lambda: self._on_error(str(e)))
    
    def _on_analysis_complete(self, result):
        """分析完成回调（主线程）"""
        self.analyze_btn.config(state=tk.NORMAL)
        self.status_label.config(text="✅ 分析完成")
```

**关键点：**
- 使用 `threading.Thread` 避免阻塞UI
- 使用 `root.after(0, callback)` 安全更新UI
- 任务开始前禁用按钮防止重复触发

---

## 🔧 扩展建议

### 1. 添加撤销功能

```python
def undo_last_topic(self):
    """撤销上一个知识点的学习记录"""
    if self.context_mgr.progress_tracker.learned_topics:
        last_topic = self.context_mgr.progress_tracker.learned_topics.pop()
        
        # 删除对应的note文件
        note_file = self.note_dir / f"{last_topic}.md"
        if note_file.exists():
            note_file.unlink()
        
        # 更新overview
        self._rebuild_overview_progress()
```

### 2. 支持多项目切换

```python
class MultiProjectOrchestrator:
    """支持同时管理多个项目"""
    
    def __init__(self):
        self.projects: Dict[str, AgentOrchestrator] = {}
        self.current_project: Optional[str] = None
    
    def add_project(self, project_id: str, project_path: str, api_key: str):
        self.projects[project_id] = AgentOrchestrator(...)
    
    def switch_project(self, project_id: str):
        self.current_project = project_id
    
    def get_current_orchestrator(self) -> AgentOrchestrator:
        return self.projects[self.current_project]
```

### 3. 学习数据统计

```python
def get_learning_analytics(self) -> Dict:
    """获取学习数据分析"""
    progress = self.get_progress()
    
    # 计算平均掌握程度
    avg_mastery = sum(
        self.context_mgr.progress_tracker.topic_details[tid]['mastery_level']
        for tid in progress['learned_topics']
    ) / len(progress['learned_topics'])
    
    return {
        "completion_rate": progress['progress_percentage'],
        "average_mastery": avg_mastery,
        "learning_velocity": "...",  # 每天完成的知识点数
        "time_spent": "..."  # 总学习时间
    }
```

---

## 📊 性能指标

| 操作 | 典型耗时 | 说明 |
|------|---------|------|
| 项目分析 | 10-30秒 | 取决于项目大小和LLM响应速度 |
| 知识点讲解 | 5-15秒 | 单次LLM调用 |
| 回答问题 | 2-5秒 | 单次LLM调用 |
| 进度更新 | <1秒 | 本地文件操作 |

---

## 📦 依赖要求

```txt
langchain>=0.1.0
langchain-openai>=0.0.5
openai>=1.0.0
```

---

## 📚 相关模块

- [`core/agent_manager.py`](./agent_manager.py) - LLM统一管理器
- [`core/context_manager.py`](./context_manager.py) - 上下文管理器
- [`core/project_analyzer.py`](./project_analyzer.py) - Java项目分析器
- [`gui/main_window.py`](../gui/main_window.py) - GUI主界面

---

## 📝 更新日志

### v1.0.0 (2024-01-XX)
- ✅ 实现完整的业务流程编排
- ✅ 状态机管理（IDLE/ANALYZING/TEACHING/QA）
- ✅ 整合AgentManager和ContextManager
- ✅ 自动生成overview.md和note文件
- ✅ 支持动态模型切换
- ✅ 完善的错误处理机制
