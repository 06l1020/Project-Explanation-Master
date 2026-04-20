# 进度持久化功能说明

## 📋 概述

进度持久化功能允许Agent记住对项目的分析结果和学习进度，避免每次启动程序时都重新进行耗时的项目分析。

### 核心优势

1. **智能跳过分析**：检测到已有的`overview.md`时自动跳过重复分析
2. **自动恢复进度**：从`.learning_progress.json`文件加载已完成的学习进度
3. **无缝续学**：从上次中断的知识点继续学习
4. **手动控制**：支持强制重新分析和手动进度管理

---

## 🎯 工作原理

### 1. 初始化时自动加载

当你创建`AgentOrchestrator`实例时，系统会自动：

```python
orchestrator = AgentOrchestrator(
    project_path="path/to/project",
    api_key="your-api-key"
)
# 🆕 自动执行以下操作：
# 1. 检查 .learning_progress.json 是否存在
# 2. 扫描 note/ 目录识别已完成的知识点
# 3. 检测 overview.md 是否有效
# 4. 恢复学习进度到内存
```

### 2. 智能判断是否需要分析

```python
# 方法1：自动判断并恢复
if orchestrator.restore_analysis_if_needed():
    print("✅ 项目分析就绪")

# 方法2：手动检查
if orchestrator.should_analyze_project():
    print("需要重新分析")
    orchestrator.analyze_project()
else:
    print("已有有效的分析结果，可以跳过")
```

### 3. 自动保存进度

每完成一个知识点，系统自动保存进度：

```python
topic = orchestrator.next_topic()
# ✅ 自动保存到 .learning_progress.json
# ✅ 更新 overview.md 中的学习进度部分
```

---

## 📁 生成的文件

### 1. `.learning_progress.json`（进度记录文件）

存储在学习项目的根目录下：

```json
{
  "learned_topics": ["core_java", "spring_boot", "spring_boot_web"],
  "topic_details": {
    "core_java": {
      "completed_at": "2024-01-15 14:30:00",
      "summary": "学习了Java基础语法、面向对象编程...",
      "mastery_level": 4
    },
    "spring_boot": {
      "completed_at": "2024-01-15 15:45:00",
      "summary": "理解了Spring Boot的自动配置原理...",
      "mastery_level": 3
    }
  },
  "progress_percentage": 30.0,
  "last_updated": "2024-01-15 16:00:00"
}
```

### 2. `overview.md`（项目分析报告）

包含"已学习内容"章节，记录学习历程：

```markdown
## 三、已学习内容

**当前状态：** 🚀 学习中  
**学习统计：** 已完成 3/10 个知识点（30%）

### 学习历程

#### 1. Java核心基础 ✅
**完成时间：** 2024-01-15 14:30:00  
**核心收获：** 掌握了Java基础语法和OOP思想  
**掌握程度：** ⭐⭐⭐⭐☆ (4/5)

---

#### 2. Spring Boot框架 ✅
...
```

### 3. `note/` 目录

每个知识点的详细讲解文件：

```
note/
├── core_java.md
├── spring_boot.md
└── spring_boot_web.md
```

---

## 💡 使用示例

### 示例1：智能恢复（推荐）

```python
from core.orchestrator import AgentOrchestrator

# 第一次运行
print("【第一次运行】")
orchestrator = AgentOrchestrator(
    project_path="my-java-project",
    api_key="sk-xxx"
)

# 自动检测并分析项目
orchestrator.restore_analysis_if_needed()

# 学习几个知识点
for i in range(3):
    topic = orchestrator.next_topic()
    if topic:
        print(f"完成: {topic['topic']['title']}")

# 程序退出，进度已自动保存


# ========================================
# 第二次运行（重启程序）
# ========================================
print("\n【第二次运行】")
orchestrator2 = AgentOrchestrator(
    project_path="my-java-project",
    api_key="sk-xxx"
)

# 🎯 关键：自动跳过分析，恢复进度
orchestrator2.restore_analysis_if_needed()
# 输出：
# 📂 检测到进度文件: my-java-project/.learning_progress.json
# ✅ 已加载进度: 3 个知识点已完成
# 📄 检测到已有项目分析结果: my-java-project/overview.md
# ✅ 检测到有效的 overview.md，跳过项目分析
# 📊 当前学习进度: 3/10 (30.0%)

# 继续学习下一个知识点（从第4个开始）
topic = orchestrator2.next_topic()
print(f"继续学习: {topic['topic']['title']}")
```

### 示例2：强制重新分析

当项目代码发生重大变化时：

```python
orchestrator = AgentOrchestrator(
    project_path="my-java-project",
    api_key="sk-xxx"
)

# 🔄 强制重新分析（忽略已有的overview.md）
result = orchestrator.analyze_project(force=True)
print(f"重新分析完成: {result}")
```

### 示例3：手动进度管理

```python
orchestrator = AgentOrchestrator(
    project_path="my-java-project",
    api_key="sk-xxx"
)

# 1. 检查是否需要分析
if orchestrator.should_analyze_project():
    orchestrator.analyze_project()

# 2. 查看当前进度
progress = orchestrator.get_progress()
print(f"完成率: {progress['progress_percentage']:.1f}%")
print(f"已学习: {', '.join(progress['learned_topics'])}")

# 3. 手动保存进度（通常不需要，因为会自动保存）
orchestrator._save_progress()
```

---

## 🔧 API参考

### AgentOrchestrator 新增方法

#### 1. `restore_analysis_if_needed() -> bool`

智能恢复项目分析结果。

**返回值：**
- `True`: 成功恢复或无需恢复
- `False`: 恢复失败

**用法：**
```python
if orchestrator.restore_analysis_if_needed():
    print("✅ 项目分析就绪")
```

---

#### 2. `should_analyze_project() -> bool`

判断是否需要重新分析项目。

**返回逻辑：**
- `True`: 需要分析（overview.md不存在、为空或包含错误）
- `False`: 可以跳过（已有有效的overview.md）

**用法：**
```python
if orchestrator.should_analyze_project():
    orchestrator.analyze_project()
```

---

#### 3. `analyze_project(force: bool = False) -> Dict`

分析Java项目并生成overview.md。

**参数：**
- `force` (bool): 是否强制重新分析，默认`False`

**行为：**
- `force=False`（默认）：如果已有有效的overview.md，自动跳过分析
- `force=True`：无论是否有overview.md，都重新分析

**返回：**
```python
{
    'status': 'success',
    'timestamp': '2024-01-15T14:30:00',
    'restored': False  # True表示从已有文件恢复，False表示新分析
}
```

---

#### 4. `_save_progress()`

保存当前学习进度到`.learning_progress.json`文件。

**注意：** 通常在`next_topic()`完成后自动调用，无需手动调用。

---

#### 5. `_load_existing_progress()`

从文件加载已有的学习进度。

**注意：** 在`__init__`中自动调用，无需手动调用。

---

## 📊 工作流程图

```
程序启动
   ↓
创建 AgentOrchestrator
   ↓
🆕 自动加载进度 (_load_existing_progress)
   ├─ 读取 .learning_progress.json
   ├─ 扫描 note/ 目录
   └─ 检测 overview.md
   ↓
用户调用 restore_analysis_if_needed()
   ↓
should_analyze_project() 判断
   ├─ 需要分析 → analyze_project() → 生成 overview.md
   └─ 无需分析 → 跳过分析（节省时间）
   ↓
用户调用 next_topic()
   ├─ 获取下一个知识点
   ├─ 生成讲解内容
   ├─ 保存 note/{topic}.md
   ├─ 更新 overview.md
   ├─ 标记知识点完成
   └─ 🆕 自动保存进度 (_save_progress)
   ↓
程序退出
   ↓
下次启动时自动恢复进度 ✨
```

---

## 🎯 最佳实践

### 1. 常规使用（推荐）

```python
# 每次启动程序时
orchestrator = AgentOrchestrator(project_path, api_key)
orchestrator.restore_analysis_if_needed()  # 智能恢复

# 循环学习
while True:
    topic = orchestrator.next_topic()
    if not topic:
        break
    # 问答环节...
```

### 2. 项目代码更新后

```python
# 检测到项目代码有重大变化
orchestrator.analyze_project(force=True)  # 强制重新分析
```

### 3. 多项目管理

```python
projects = {
    "project_a": "path/to/project_a",
    "project_b": "path/to/project_b"
}

for name, path in projects.items():
    print(f"\n处理项目: {name}")
    orchestrator = AgentOrchestrator(path, api_key)
    orchestrator.restore_analysis_if_needed()
    
    progress = orchestrator.get_progress()
    print(f"进度: {progress['progress_percentage']:.1f}%")
```

---

## ⚠️ 注意事项

### 1. 进度文件的优先级

系统按以下顺序识别已完成的知识点：

1. `.learning_progress.json` 中的记录（最高优先级）
2. `note/` 目录下的`.md`文件（补充识别）

**建议：** 不要手动删除`.learning_progress.json`，除非你想从头开始学习。

### 2. overview.md的有效性判断

系统认为overview.md无效的情况：

- 文件不存在
- 文件大小为0
- 文件内容包含"❌ 项目分析失败"或"分析失败"

### 3. 并发安全

目前不支持多个进程同时操作同一个项目的进度文件。如果需要并发访问，请确保：

- 同一时间只有一个程序实例在写入进度
- 或者使用文件锁机制（未来版本可能添加）

### 4. 迁移旧项目

如果你之前使用过没有进度持久化功能的版本：

```python
# 首次启用新功能时
orchestrator = AgentOrchestrator(project_path, api_key)

# 系统会自动：
# 1. 扫描 note/ 目录
# 2. 识别已有的知识点文件
# 3. 生成 .learning_progress.json
# 4. 后续启动即可正常恢复
```

---

## 🚀 性能提升

### 典型场景对比

| 操作 | 旧版本（无持久化） | 新版本（有持久化） | 提升 |
|------|------------------|------------------|------|
| 首次启动 | 分析10-30秒 | 分析10-30秒 | - |
| 第二次启动 | 分析10-30秒 | <1秒（跳过） | **95%+** |
| 第三次启动 | 分析10-30秒 | <1秒（跳过） | **95%+** |

**结论：** 对于经常重启程序的场景，可节省大量等待时间！

---

## 📝 更新日志

### v1.1.0 (2024-01-XX)
- ✅ 新增进度持久化功能
- ✅ 自动检测和恢复学习进度
- ✅ 智能跳过重复的项目分析
- ✅ 支持强制重新分析（force参数）
- ✅ 自动生成`.learning_progress.json`文件
- ✅ 扫描note目录补充识别已完成的知识点

---

## 🔗 相关文档

- [`AGENT_MANAGER_README.md`](./AGENT_MANAGER_README.md) - LLM代理管理器
- [`CONTEXT_MANAGER_README.md`](./CONTEXT_MANAGER_README.md) - 上下文管理器
- [`progress_persistence_example.py`](./progress_persistence_example.py) - 完整使用示例
