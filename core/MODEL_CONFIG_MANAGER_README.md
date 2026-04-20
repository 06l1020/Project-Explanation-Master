# 模型配置管理器使用说明

## 概述

模型配置管理器（ModelConfigManager）用于管理多个LLM模型配置的本地存储和读取，支持配置的保存、加载、删除和切换。

---

## 核心功能

### 1. 配置持久化
- ✅ 自动保存到 `config/model_configs.json`
- ✅ 程序启动时自动加载
- ✅ 支持JSON格式，易于查看和编辑

### 2. 多配置管理
- ✅ 保存多个模型配置
- ✅ 快速切换不同配置
- ✅ 设置默认配置

### 3. 使用统计
- ✅ 记录配置使用次数
- ✅ 记录最后使用时间
- ✅ 支持按使用频率排序

### 4. GUI集成
- ✅ 工具栏配置下拉框
- ✅ 配置管理对话框
- ✅ 一键切换配置

---

## 文件结构

### 配置文件位置
```
klgm1/
└── config/
    └── model_configs.json    # 模型配置文件
```

### 配置文件格式
```json
{
  "configs": [
    {
      "name": "OpenAI GPT-4",
      "api_key": "sk-xxx",
      "base_url": "",
      "model_name": "gpt-4",
      "created_at": "2024-01-15T10:30:00",
      "last_used": "2024-01-15T14:20:00",
      "use_count": 5
    },
    {
      "name": "Ollama Local",
      "api_key": "ollama",
      "base_url": "http://localhost:11434/v1",
      "model_name": "llama2",
      "created_at": "2024-01-15T10:35:00",
      "last_used": null,
      "use_count": 0
    }
  ],
  "default_config_index": 0,
  "version": "1.0",
  "last_updated": "2024-01-15T14:20:00"
}
```

---

## API 使用指南

### 初始化

```python
from core.model_config_manager import ModelConfigManager, get_config_manager

# 方式1：使用全局单例（推荐）
config_manager = get_config_manager()

# 方式2：创建新实例
config_manager = ModelConfigManager()

# 方式3：指定配置文件路径
config_manager = ModelConfigManager(config_file="/path/to/config.json")
```

### 添加配置

```python
# 添加新配置
config = config_manager.add_config(
    name="OpenAI GPT-4",
    api_key="sk-xxx",
    base_url="",
    model_name="gpt-4",
    set_as_default=True  # 设为默认配置
)
```

### 获取配置

```python
# 获取所有配置名称
names = config_manager.get_config_names()
# 返回: ['OpenAI GPT-4', 'Ollama Local', ...]

# 获取指定配置
config = config_manager.get_config("OpenAI GPT-4")
if config:
    print(f"API Key: {config.api_key}")
    print(f"Model: {config.model_name}")

# 获取默认配置
default_config = config_manager.get_default_config()

# 获取所有配置（字典列表）
all_configs = config_manager.get_all_configs()
```

### 删除配置

```python
success = config_manager.remove_config("Ollama Local")
if success:
    print("配置已删除")
```

### 设置默认配置

```python
success = config_manager.set_default_config("OpenAI GPT-4")
if success:
    print("已设为默认配置")
```

### 记录使用

```python
# 记录配置使用（自动更新使用次数和最后使用时间）
config_manager.record_usage("OpenAI GPT-4")
```

### 获取常用配置

```python
# 获取最常用的5个配置
frequent_configs = config_manager.get_frequently_used(limit=5)
```

---

## 默认配置

首次启动时，系统会自动创建3个默认配置：

### 1. OpenAI GPT-4
```json
{
  "name": "OpenAI GPT-4",
  "api_key": "",
  "base_url": "",
  "model_name": "gpt-4"
}
```

### 2. OpenAI GPT-3.5
```json
{
  "name": "OpenAI GPT-3.5",
  "api_key": "",
  "base_url": "",
  "model_name": "gpt-3.5-turbo"
}
```

### 3. Ollama Local
```json
{
  "name": "Ollama Local",
  "api_key": "ollama",
  "base_url": "http://localhost:11434/v1",
  "model_name": "llama2"
}
```

---

## GUI 使用

### 工具栏配置选择

```
┌──────────────────────────────────────────┐
│ [项目路径] [选择项目] [模型配置▼] [管理]  │
│                         ↑                │
│                    点击切换配置           │
└──────────────────────────────────────────┘
```

**操作步骤：**
1. 点击下拉框
2. 选择已保存的配置
3. 系统自动加载该配置的所有参数

### 配置管理对话框

点击 **"⚙️ 管理配置"** 按钮打开配置管理对话框：

**左侧 - 配置列表：**
- 显示所有已保存的配置
- 默认配置标注 "⭐ (默认)"
- 支持选择、编辑、删除

**右侧 - 编辑区：**
- 配置名称
- API Key（密码框）
- Base URL
- 模型名称（下拉框）

**操作按钮：**
- 📝 编辑：加载选中配置到编辑区
- ⭐ 设为默认：将选中配置设为默认
- 🗑️ 删除：删除选中配置
- 💾 保存配置：保存新配置或更新现有配置

---

## 使用场景

### 场景1：多模型切换

**需求：** 在项目分析时使用GPT-4，在知识点讲解时使用GPT-3.5

**操作：**
1. 创建两个配置：
   - "GPT-4 分析"：model_name="gpt-4"
   - "GPT-3.5 讲解"：model_name="gpt-3.5-turbo"
2. 分析项目前选择 "GPT-4 分析"
3. 讲解知识点时切换到 "GPT-3.5 讲解"

### 场景2：本地与云端切换

**需求：** 开发时使用本地Ollama，生产时使用OpenAI

**操作：**
1. 创建两个配置：
   - "Ollama 开发"：base_url="http://localhost:11434/v1"
   - "OpenAI 生产"：base_url=""
2. 根据环境快速切换

### 场景3：团队协作

**需求：** 团队成员共享配置

**操作：**
1. 将 `model_configs.json` 加入版本控制（注意：API Key应该排除）
2. 团队成员拉取配置模板
3. 各自填写自己的API Key

---

## 安全建议

### 1. API Key 保护
```python
# ✅ 推荐：使用环境变量
import os
api_key = os.getenv("OPENAI_API_KEY")

# ❌ 不推荐：硬编码在配置文件中
# api_key = "sk-xxx"  # 明文存储
```

### 2. Git 忽略配置
在 `.gitignore` 中添加：
```
config/model_configs.json
```

### 3. 配置文件备份
定期备份配置文件，但注意移除敏感的API Key：
```bash
# 导出配置（不含API Key）
python -c "
import json
from core.model_config_manager import get_config_manager
cm = get_config_manager()
configs = cm.get_all_configs()
for c in configs:
    c['api_key'] = '***'  # 隐藏API Key
print(json.dumps(configs, indent=2))
"
```

---

## 故障排除

### 问题1：配置文件未加载

**原因：**
- 配置文件路径不正确
- 文件格式错误

**解决方案：**
```python
# 检查配置文件是否存在
from pathlib import Path
config_file = Path("config/model_configs.json")
if config_file.exists():
    print("配置文件存在")
else:
    print("配置文件不存在，将创建默认配置")
```

### 问题2：配置切换后未生效

**原因：**
- 未重新初始化 Orchestrator
- 配置参数未正确传递

**解决方案：**
```python
# 切换配置后重新初始化
config_manager.set_default_config("New Config")
# 重新选择项目或点击"分析项目"触发重新初始化
```

### 问题3：无法删除默认配置

**原因：**
- 系统设计保护机制

**解决方案：**
- 先设置其他配置为默认
- 再删除原默认配置

---

## 最佳实践

### 1. 配置命名规范
```python
# ✅ 推荐：清晰描述配置用途
"OpenAI GPT-4 生产"
"Ollama Llama2 开发"
"Azure GPT-3.5 测试"

# ❌ 不推荐：模糊命名
"配置1"
"测试"
"新配置"
```

### 2. 定期清理
```python
# 清理长期未使用的配置
from datetime import datetime

all_configs = config_manager.get_all_configs()
for config in all_configs:
    if config['last_used'] is None:
        print(f"配置 '{config['name']}' 从未使用")
    else:
        last_used = datetime.fromisoformat(config['last_used'])
        days_since = (datetime.now() - last_used).days
        if days_since > 90:
            print(f"配置 '{config['name']}' 已超过90天未使用")
```

### 3. 配置模板
创建常用配置模板文件 `config_templates.json`：
```json
{
  "templates": [
    {
      "name": "OpenAI GPT-4",
      "api_key": "",
      "base_url": "",
      "model_name": "gpt-4"
    },
    {
      "name": "Ollama Local",
      "api_key": "ollama",
      "base_url": "http://localhost:11434/v1",
      "model_name": "llama2"
    }
  ]
}
```

---

## 相关文档

- [`GUI_USAGE_GUIDE.md`](../gui/GUI_USAGE_GUIDE.md) - GUI使用指南
- [`AGENT_MANAGER_README.md`](../core/AGENT_MANAGER_README.md) - Agent管理器文档
- [`TOKEN_TRACKER_README.md`](../core/TOKEN_TRACKER_README.md) - Token追踪器文档

---

**更新日期：** 2026-04-20  
**版本：** v1.0  
**状态：** ✅ 已完成
