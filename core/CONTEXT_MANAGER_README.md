# Context Manager 模块说明

## 📋 模块概述

`context_manager.py` 提供智能的上下文管理功能，包括代码索引缓存和学习进度跟踪，用于优化LLM调用效率和提升学习体验。

### 核心组件

1. **CodeIndexCache** - 代码索引缓存
2. **LearningProgressTracker** - 学习进度跟踪器
3. **ContextManager** - 统一上下文管理器（整合上述两个组件）

---

## 🏗️ 架构设计

```
┌──────────────────────────────────────┐
│      ContextManager (统一入口)        │
├──────────────────┬───────────────────┤
│ CodeIndexCache   │ LearningProgress  │
│                  │ Tracker           │
├──────────────────┼───────────────────┤
│ • 代码索引构建    │ • 知识点状态管理   │
│ • 智能代码提取    │ • 依赖关系检查     │
│ • Token优化      │ • 进度计算         │
│ • 层级识别       │ • 持久化存储       │
└──────────────────┴───────────────────┘
```

---

## 🚀 快速开始

### 1. 基础使用

```python
from core.context_manager import ContextManager

# 初始化
context_mgr = ContextManager(
    project_path="path/to/java/project",
    knowledge_tree_path="config/knowledge_tree.json"
)

# 构建代码索引
context_mgr.initialize()

# 获取下一个知识点
next_topic = context_mgr.get_next_topic()
print(f"建议学习: {next_topic['title']}")

# 获取相关代码上下文
code_context = context_mgr.get_code_context(
    topic=next_topic['title'],
    max_files=3
)

# 完成知识点后更新进度
context_mgr.complete_topic(
    topic_id=next_topic['id'],
    summary="学习了核心概念",
    mastery_level=4
)

# 查看进度
progress = context_mgr.get_progress()
print(f"进度: {progress['progress_percentage']:.1f}%")
```

---

## 📝 API参考

### CodeIndexCache

#### 初始化

```python
cache = CodeIndexCache(project_path: str)
```

**参数：**
- `project_path`: Java项目根目录路径

---

#### build_index()

构建代码索引

```python
cache.build_index(
    max_files: int = 50,      # 最大索引文件数
    max_file_size: int = 3000  # 单文件最大字符数
)
```

**功能：**
- 扫描 `src/main/java` 目录
- 按优先级排序（启动类 > Controller > Service > Model > Config）
- 提取包名、类名、层级类型
- 生成文件摘要
- 截断过长的代码内容

---

#### get_relevant_code()

根据主题获取相关代码

```python
code = cache.get_relevant_code(
    topic: str,          # 知识点主题
    max_files: int = 5   # 最多返回文件数
) -> str
```

**返回：** Markdown格式的代码上下文

**示例输出：**
```markdown
### 文件: `src/main/java/com/example/UserController.java`
**类名:** UserController
**层级:** controller
**摘要:** 用户管理控制器

```java
@RestController
@RequestMapping("/users")
public class UserController {
    // ...
}
```
```

---

#### get_file_content()

获取指定文件的完整代码

```python
content = cache.get_file_content(file_path: str) -> Optional[str]
```

**参数：**
- `file_path`: 相对路径（如 `"src/main/java/com/example/DemoApplication.java"`）

---

#### get_index_summary()

获取索引统计信息

```python
summary = cache.get_index_summary() -> Dict
```

**返回示例：**
```python
{
    "total_files": 25,
    "layer_distribution": {
        "controller": 5,
        "service": 8,
        "model": 10,
        "application": 1,
        "config": 1
    },
    "total_size": 45000
}
```

---

### LearningProgressTracker

#### 初始化

```python
tracker = LearningProgressTracker(knowledge_tree_path: str)
```

**参数：**
- `knowledge_tree_path`: [knowledge_tree.json](file://d:\pyproject\klgm1\config\knowledge_tree.json) 文件路径

---

#### mark_topic_completed()

标记知识点已完成

```python
tracker.mark_topic_completed(
    topic_id: str,              # 知识点ID
    summary: str = "",          # 学习总结
    mastery_level: int = 3      # 掌握程度 (1-5)
)
```

---

#### get_next_topic()

获取下一个应该学习的知识点

```python
next_topic = tracker.get_next_topic() -> Optional[Dict]
```

**逻辑：**
1. 过滤出未学习的知识点
2. 检查前置条件是否满足
3. 按难度排序（简单→复杂）
4. 返回第一个可用的知识点

**返回示例：**
```python
{
    "id": "spring_boot",
    "title": "Spring Boot框架",
    "difficulty": 2,
    "prerequisites": ["core_java"],
    "description": "..."
}
```

---

#### get_progress_percentage()

获取学习进度百分比

```python
percentage = tracker.get_progress_percentage() -> float
```

**返回：** 0.0 - 100.0

---

#### get_progress_summary()

获取完整的进度摘要

```python
summary = tracker.get_progress_summary() -> Dict
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

#### save_to_file() / load_from_file()

持久化进度到文件

```python
# 保存
tracker.save_to_file("learning_progress.json")

# 加载
tracker.load_from_file("learning_progress.json")
```

**保存的数据格式：**
```json
{
    "learned_topics": ["core_java", "spring_boot"],
    "topic_details": {
        "core_java": {
            "completed_at": "2024-01-15 14:30:00",
            "summary": "掌握了Java基础",
            "mastery_level": 5
        }
    },
    "progress_percentage": 20.0,
    "last_updated": "2024-01-15 14:30:00"
}
```

---

### ContextManager（统一入口）

#### 初始化

```python
context_mgr = ContextManager(
    project_path: str,
    knowledge_tree_path: str
)
```

---

#### initialize()

初始化（构建代码索引）

```python
context_mgr.initialize()
```

---

#### get_code_context()

获取知识点相关的代码上下文

```python
code = context_mgr.get_code_context(
    topic: str,
    max_files: int = 5
) -> str
```

---

#### get_next_topic()

获取下一个知识点

```python
next_topic = context_mgr.get_next_topic() -> Optional[Dict]
```

---

#### complete_topic()

完成一个知识点

```python
context_mgr.complete_topic(
    topic_id: str,
    summary: str = "",
    mastery_level: int = 3
)
```

---

#### get_progress()

获取学习进度

```python
progress = context_mgr.get_progress() -> Dict
```

---

## 🎯 最佳实践

### 1. Token优化策略

```python
# ✅ 好的做法：限制代码提取数量
code_context = context_mgr.get_code_context(
    topic="Spring Boot自动配置",
    max_files=3  # 只取最相关的3个文件
)

# ❌ 避免：提取过多代码
code_context = context_mgr.get_code_context(
    topic="Spring Boot",
    max_files=20  # Token消耗过大
)
```

---

### 2. 代码索引构建时机

```python
# ✅ 在项目分析完成后立即构建
def analyze_project(project_path):
    analyzer = ProjectAnalyzer(project_path)
    result = analyzer.analyze()
    
    # 构建代码索引供后续使用
    context_mgr = ContextManager(project_path, knowledge_tree_path)
    context_mgr.initialize()
    
    return result, context_mgr
```

---

### 3. 进度持久化

```python
# 每次完成知识点后保存
def on_topic_completed(topic_id, summary):
    context_mgr.complete_topic(topic_id, summary, mastery_level=4)
    context_mgr.progress_tracker.save_to_file("learning_progress.json")
    
    # GUI中显示进度
    progress = context_mgr.get_progress()
    update_progress_bar(progress['progress_percentage'])
```

---

### 4. 智能推荐下一个知识点

```python
def recommend_next_topic():
    next_topic = context_mgr.get_next_topic()
    
    if next_topic is None:
        return "🎉 恭喜！你已完成所有知识点！"
    
    # 检查前置条件
    missing_prereqs = []
    for prereq in next_topic.get('prerequisites', []):
        if prereq not in context_mgr.progress_tracker.learned_topics:
            missing_prereqs.append(prereq)
    
    if missing_prereqs:
        return f"请先完成前置知识点: {', '.join(missing_prereqs)}"
    
    return f"建议学习: {next_topic['title']} (难度: {next_topic.get('difficulty', 'N/A')})"
```

---

## 🔍 代码索引工作原理

### 文件优先级排序

```
优先级1: 启动类 (@SpringBootApplication)
优先级2: Controller (@RestController, @Controller)
优先级3: Service (@Service)
优先级4: Repository (@Repository)
优先级5: Model/Entity (@Entity, @Table)
优先级6: Config (@Configuration)
优先级7: 其他
```

### 层级检测策略

1. **注解检测**（优先）
   - 扫描类上的Spring注解
   
2. **路径检测**（备选）
   - `/controller/` → controller层
   - `/service/` → service层
   - `/repository/` 或 `/dao/` → repository层
   - `/model/` 或 `/entity/` → model层
   - `/config/` → config层

### 代码截断策略

```
原始代码长度 ≤ 3000字符: 完整保留
原始代码长度 > 3000字符: 
  - 保留前1500字符
  - 中间插入省略标记
  - 保留后1500字符
```

---

## 📊 性能指标

| 操作 | 典型耗时 | 说明 |
|------|---------|------|
| 构建索引（50文件） | 0.5-2秒 | 取决于文件大小 |
| 获取相关代码 | <10ms | 从缓存读取 |
| 进度计算 | <1ms | 内存操作 |
| 保存进度到文件 | <50ms | JSON序列化 |

---

## 🔧 扩展建议

### 1. 语义匹配增强

当前使用关键词匹配，可升级为：
- 使用Embedding向量相似度搜索
- 集成FAISS或Chroma向量数据库
- 基于AST语法树分析代码结构

### 2. 增量索引更新

```python
def update_index_incrementally(changed_files: List[str]):
    """只更新变化的文件，而非全量重建"""
    for file_path in changed_files:
        if file_path in cache.index:
            del cache.index[file_path]
            del cache.code_cache[file_path]
    
    # 重新索引变化的文件
    cache._index_files(changed_files)
```

### 3. 多项目支持

```python
class MultiProjectContextManager:
    """支持同时管理多个项目的上下文"""
    
    def __init__(self):
        self.projects: Dict[str, ContextManager] = {}
    
    def add_project(self, project_id: str, project_path: str):
        self.projects[project_id] = ContextManager(...)
```

---

## 📦 依赖要求

本模块仅使用Python标准库，无需额外依赖：
- `pathlib` - 路径处理
- `json` - 进度持久化
- `tempfile` - 测试支持

---

## 📚 相关模块

- [`core/agent_manager.py`](./agent_manager.py) - LLM统一管理器
- [`core/project_analyzer.py`](./project_analyzer.py) - Java项目分析器
- [`core/orchestrator.py`](./orchestrator.py) - 业务流程编排器
- [`config/knowledge_tree.json`](../config/knowledge_tree.json) - 知识点配置

---

## 📝 更新日志

### v1.0.0 (2024-01-XX)
- ✅ 实现CodeIndexCache代码索引缓存
- ✅ 实现LearningProgressTracker进度跟踪
- ✅ 实现ContextManager统一入口
- ✅ 支持智能代码提取和Token优化
- ✅ 支持进度持久化和依赖检查
