"""
Agent统一管理器
负责管理所有LLM调用、提示词模板和Agent实例
支持动态切换模型提供商（OpenAI、DeepSeek、Ollama等）
"""

import os
from typing import Optional, Dict, Any, List
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from core.token_tracker import TokenUsageTracker


class AgentManager:
    """
    Agent统一管理器
    
    功能：
    1. 统一管理LLM客户端配置
    2. 提供四大专用Agent（项目分析、知识讲解、问答、进度更新）
    3. 管理提示词模板
    4. 支持动态切换模型
    5. 记录token使用情况
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model_name: str = "gpt-4",
        temperature: float = 0.7,
        project_path: Optional[str] = None
    ):
        """
        初始化Agent管理器
        
        Args:
            api_key: API密钥，默认从环境变量OPENAI_API_KEY读取
            base_url: API基础URL，None则使用OpenAI官方端点
            model_name: 模型名称，默认gpt-4
            temperature: 温度参数，控制输出随机性
            project_path: 项目路径（用于保存token记录）
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "未提供API密钥！请通过以下方式之一配置：\n"
                "1. 构造函数传入api_key参数\n"
                "2. 设置环境变量OPENAI_API_KEY"
            )
        
        self.base_url = base_url
        self.model_name = model_name
        self.temperature = temperature
        
        # 初始化LLM客户端
        self.llm = self._create_llm_client()
        
        # 加载提示词模板
        self.prompts = self._load_prompts()
        
        # 聊天历史管理（用于问答Agent）
        self.chat_history: List[Dict[str, str]] = []
        
        # 初始化token追踪器
        self.token_tracker = TokenUsageTracker(project_path=project_path)
    
    def _create_llm_client(self) -> ChatOpenAI:
        """
        创建LLM客户端
        
        支持OpenAI官方及兼容OpenAI API格式的服务
        
        Returns:
            ChatOpenAI实例
        """
        kwargs = {
            "model": self.model_name,
            "temperature": self.temperature,
            "openai_api_key": self.api_key,
        }
        
        # 如果提供了自定义base_url，则配置
        if self.base_url:
            kwargs["openai_api_base"] = self.base_url
        
        return ChatOpenAI(**kwargs)
    
    def _load_prompts(self) -> Dict[str, PromptTemplate]:
        """
        加载所有提示词模板
        
        Returns:
            包含四个Agent的PromptTemplate字典
        """
        prompts = {}
        
        # 1. 项目分析Agent提示词
        prompts["project_analysis"] = PromptTemplate(
            input_variables=["project_structure", "dependencies", "framework_detected", "code_samples"],
            template=self._get_project_analysis_template()
        )
        
        # 2. 知识讲解Agent提示词
        prompts["knowledge_teaching"] = PromptTemplate(
            input_variables=[
                "project_overview", 
                "topic_title", 
                "topic_description", 
                "learned_topics",
                "project_code_context"
            ],
            template=self._get_knowledge_teaching_template()
        )
        
        # 3. 问答Agent提示词
        prompts["qa"] = PromptTemplate(
            input_variables=[
                "project_overview",
                "current_topic",
                "question",
                "conversation_history"
            ],
            template=self._get_qa_template()
        )
        
        # 4. 进度更新Agent提示词
        prompts["progress_update"] = PromptTemplate(
            input_variables=[
                "current_topic",
                "current_summary",
                "existing_progress",
                "topic_code_examples"
            ],
            template=self._get_progress_update_template()
        )
        
        return prompts
    
    def analyze_project(
        self,
        project_structure: str,
        dependencies: str,
        framework_detected: str,
        code_samples: str = ""
    ) -> str:
        """
        项目分析Agent - 分析Java项目框架和技术栈
        
        Args:
            project_structure: 项目结构信息（包结构、文件列表等）
            dependencies: 依赖项列表（Maven/Gradle依赖）
            framework_detected: 检测到的框架（Spring Boot、MyBatis等）
            code_samples: 关键代码片段（启动类、Controller等）
            
        Returns:
            生成的overview.md内容
        """
        prompt = self.prompts["project_analysis"].format(
            project_structure=project_structure,
            dependencies=dependencies,
            framework_detected=framework_detected,
            code_samples=code_samples
        )
        
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
        
        return response.content
    
    def teach_knowledge(
        self,
        project_overview: str,
        topic_title: str,
        topic_description: str,
        learned_topics: str = "",
        project_code_context: str = ""
    ) -> str:
        """
        知识讲解Agent - 结合项目代码讲解知识点
        
        Args:
            project_overview: 项目概览（overview.md内容）
            topic_title: 知识点标题
            topic_description: 知识点描述
            learned_topics: 已学习的知识点列表
            project_code_context: 项目相关代码上下文
            
        Returns:
            生成的知识点讲解Markdown内容
        """
        prompt = self.prompts["knowledge_teaching"].format(
            project_overview=project_overview,
            topic_title=topic_title,
            topic_description=topic_description,
            learned_topics=learned_topics,
            project_code_context=project_code_context
        )
        
        response = self.llm.invoke(prompt)
        
        # 记录token消耗
        if hasattr(response, 'response_metadata') and 'token_usage' in response.response_metadata:
            token_usage = response.response_metadata['token_usage']
            self.token_tracker.add_record(
                operation="知识点讲解",
                model=self.model_name,
                prompt_tokens=token_usage.get('prompt_tokens', 0),
                completion_tokens=token_usage.get('completion_tokens', 0),
                total_tokens=token_usage.get('total_tokens', 0)
            )
        
        return response.content
    
    def answer_question(
        self,
        project_overview: str,
        current_topic: str,
        question: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        问答Agent - 回答用户关于当前知识点的问题
        
        Args:
            project_overview: 项目概览
            current_topic: 当前正在讲解的知识点
            question: 用户问题
            conversation_history: 对话历史（可选）
            
        Returns:
            结构化的回答内容
        """
        # 格式化对话历史
        if conversation_history is None:
            conversation_history = self.chat_history
        
        history_text = "\n".join([
            f"用户: {msg['user']}\n助手: {msg['assistant']}"
            for msg in conversation_history[-5:]  # 只保留最近5轮
        ])
        
        prompt = self.prompts["qa"].format(
            project_overview=project_overview,
            current_topic=current_topic,
            question=question,
            conversation_history=history_text
        )
        
        response = self.llm.invoke(prompt)
        answer = response.content
        
        # 记录token消耗
        if hasattr(response, 'response_metadata') and 'token_usage' in response.response_metadata:
            token_usage = response.response_metadata['token_usage']
            self.token_tracker.add_record(
                operation="问答",
                model=self.model_name,
                prompt_tokens=token_usage.get('prompt_tokens', 0),
                completion_tokens=token_usage.get('completion_tokens', 0),
                total_tokens=token_usage.get('total_tokens', 0)
            )
        
        # 更新聊天历史
        self.chat_history.append({
            "user": question,
            "assistant": answer
        })
        
        return answer
    
    def update_progress(
        self,
        current_topic: str,
        current_summary: str,
        existing_progress: str = "",
        topic_code_examples: str = ""
    ) -> str:
        """
        进度更新Agent - 更新overview.md中的"已学习内容"部分
        
        Args:
            current_topic: 刚完成的知识点
            current_summary: 该知识点的总结
            existing_progress: 现有的学习进度内容
            topic_code_examples: 关键代码示例
            
        Returns:
            更新后的"已学习内容"部分内容
        """
        prompt = self.prompts["progress_update"].format(
            current_topic=current_topic,
            current_summary=current_summary,
            existing_progress=existing_progress,
            topic_code_examples=topic_code_examples
        )
        
        response = self.llm.invoke(prompt)
        
        # 记录token消耗
        if hasattr(response, 'response_metadata') and 'token_usage' in response.response_metadata:
            token_usage = response.response_metadata['token_usage']
            self.token_tracker.add_record(
                operation="进度更新",
                model=self.model_name,
                prompt_tokens=token_usage.get('prompt_tokens', 0),
                completion_tokens=token_usage.get('completion_tokens', 0),
                total_tokens=token_usage.get('total_tokens', 0)
            )
        
        return response.content
    
    def clear_chat_history(self):
        """清除聊天历史（切换知识点时调用）"""
        self.chat_history = []
    
    def update_model_config(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None
    ):
        """
        动态更新模型配置
        
        Args:
            api_key: 新的API密钥
            base_url: 新的API基础URL
            model_name: 新的模型名称
            temperature: 新的温度参数
        """
        if api_key:
            self.api_key = api_key
        if base_url is not None:
            self.base_url = base_url
        if model_name:
            self.model_name = model_name
        if temperature is not None:
            self.temperature = temperature
        
        # 重新创建LLM客户端
        self.llm = self._create_llm_client()
    
    # ==================== 提示词模板 ====================
    
    def _get_project_analysis_template(self) -> str:
        """项目分析提示词模板"""
        return """你是一位经验丰富的Java企业级开发导师，擅长分析项目架构并制定学习路线。

请分析以下Java项目的技术栈和结构，生成一份详细的学习指南。

## 项目信息

### 项目结构
{project_structure}

### 依赖项
{dependencies}

### 检测到的框架
{framework_detected}

### 关键代码片段
{code_samples}

## 输出要求

请严格按照以下格式输出（不要包含```

# [项目名称] - Java企业级项目学习指南

> 📋 **文档说明**：本文档是基于实际项目分析生成的个性化学习指南，将帮助你由浅入深掌握Java企业级开发。

---

## 一、项目框架及技术栈分析

### 1.1 核心框架
[分析项目使用的核心框架，如Spring Boot版本、构建工具等]

### 1.2 企业级组件
| 组件类型 | 技术选型 | 版本 | 用途说明 |
|---------|---------|------|---------|
| [组件名] | [技术] | [版本] | [说明] |

### 1.3 技术栈优势与挑战
**优势：**
- [列出2-3个技术栈优势]

**挑战：**
- [列出1-2个需要注意的技术难点]

### 1.4 架构风格
[分析项目采用的架构风格，如MVC、分层架构等]

---

## 二、学习路线图

### 2.1 第一阶段：基础巩固（预计X天）
**目标：** [阶段目标]
**知识点：**
1. [知识点1] - [简要说明]
2. [知识点2] - [简要说明]

### 2.2 第二阶段：框架深入（预计X天）
**目标：** [阶段目标]
**知识点：**
1. [知识点1] - [简要说明]
2. [知识点2] - [简要说明]

### 2.3 第三阶段：实战进阶（预计X天）
**目标：** [阶段目标]
**知识点：**
1. [知识点1] - [简要说明]
2. [知识点2] - [简要说明]

---

## 三、已学习内容

> 📝 **说明**：此部分将在你完成每个知识点后自动更新，记录你的学习历程。

**当前状态：** 🆕 尚未开始学习
**学习统计：** 已完成 0/X 个知识点

### 学习历程
*暂无学习内容，点击"下一个知识点"开始学习之旅！*

---

## 四、项目代码索引

### Controller层
| 类名 | 路径 | 主要功能 |
|------|------|---------|
| [类名] | [路径] | [功能] |

### Service层
| 类名 | 路径 | 主要功能 |
|------|------|---------|
| [类名] | [路径] | [功能] |

### Model层
| 类名 | 路径 | 主要功能 |
|------|------|---------|
| [类名] | [路径] | [功能] |

---

> 💡 **提示**：现在可以点击"下一个知识点"按钮，开始你的第一个知识点学习！
"""

    def _get_knowledge_teaching_template(self) -> str:
        """知识讲解提示词模板"""
        return """你是一位富有激情且耐心的Java企业级开发导师，善于用通俗易懂的方式讲解复杂概念。

## 背景信息

### 项目概览
{project_overview}

### 当前知识点
**标题：** {topic_title}
**描述：** {topic_description}

### 已学习的知识点
{learned_topics}

### 项目相关代码
{project_code_context}

## 教学要求

请以自然聊天的口吻，结合上述项目的实际代码，深入浅出地讲解这个知识点。

### 输出格式（严格按照以下结构，使用```

# {topic_title}

> 🎯 **学习目标**：[用1-2句话说明学完本节后能掌握什么]

---

## 一、这是什么？为什么重要？

### 1.1 概念解释
[用通俗语言解释概念，避免教科书式表述]

### 1.2 为什么需要它？
[说明这个技术解决了什么问题，不使用它会怎样]

### 1.3 在我们的项目中哪里用到了？
**代码位置：** [明确指出项目中的具体类或方法路径]

**实际代码：**
[展示项目中的真实代码片段，并标注语言类型如java]

**代码解读：**
[逐行或分块解读关键逻辑]

---

## 二、核心原理大白话

### 2.1 工作原理
[用生活类比或比喻解释工作原理]

### 2.2 关键概念
| 术语 | 通俗解释 | 技术定义 |
|------|---------|---------|
| [术语] | [类比] | [定义] |

### 2.3 心理模型
[帮助理解的思维模型或可视化描述]

---

## 三、项目实战演练

### 3.1 项目中的实际应用
[详细分析项目中如何使用这个知识点]

### 3.2 从零实现
[如果项目缺少此功能，提供完整的从零实现步骤]

**步骤1：** [步骤说明]
``java
[代码示例，包含中文注释]
```

**步骤2：** [步骤说明]
```java
[代码示例]
```

### 3.3 运行效果
[描述运行后的预期结果]

---

## 四、常见陷阱与解决方案

### ⚠️ 陷阱1：[陷阱名称]
**错误示例：**
```java
[错误代码]
```

**正确做法：**
```java
[正确代码]
```

**原因分析：** [解释为什么会出错]

### ⚠️ 陷阱2：[陷阱名称]
[同上格式]

---

## 五、进阶技巧

### 💡 技巧1：[技巧名称]
[高级用法或优化建议]

### 📊 性能优化建议
[如果有性能相关的优化点]

---

## 六、知识扩展

### 🔗 相关知识点
- [知识点1] - [关系说明]
- [知识点2] - [关系说明]

### 📚 延伸阅读
- [推荐文章/文档链接]

### 🤔 思考题
1. [思考题1]
2. [思考题2]

---

## 七、小结与下一步

### ✅ 核心要点回顾
1. [要点1]
2. [要点2]
3. [要点3]

### 🎉 恭喜你！
你已经掌握了[知识点名称]的核心内容！

### ➡️ 下一步学习
建议接下来学习：[下一个知识点建议]

---

> 💬 **有问题？** 在下方输入框中提问，我会为你详细解答！
"""

    def _get_qa_template(self) -> str:
        """问答提示词模板"""
        return """你是一位耐心细致的Java导师，正在回答学生关于[{current_topic}]的问题。

## 上下文信息

### 项目概览
{project_overview}

### 当前知识点
{current_topic}

### 对话历史
{conversation_history}

## 用户问题
{question}

## 回答要求

请提供结构化、清晰的回答，遵循以下格式：

## 💬 问题解答

### 核心答案
[用1-2句话直接回答问题的核心]

---

### 详细说明
[展开详细解释，结合项目实际情况]

---

### 代码示例
[如果适用，提供代码示例]
``java
[代码，包含中文注释]
```

---

### 在项目中的应用
[说明这个知识点在当前项目中如何应用，或应该在哪里应用]

---

### 常见误区
❌ **错误理解：** [常见错误]
✅ **正确理解：** [正确方式]

---

### 延伸阅读
- [相关资源1]
- [相关资源2]

---

### 🤔 进一步思考
[提出一个相关的思考问题，引导深入学习]

---

> 💡 **提示**：如果还有疑问，继续提问吧！
"""

    def _get_progress_update_template(self) -> str:
        """进度更新提示词模板"""
        return """你是一个学习进度记录助手，负责更新学习者的进度信息。

## 输入信息

### 刚完成的知识点
{current_topic}

### 知识点总结
{current_summary}

### 现有学习进度
{existing_progress}

### 关键代码示例
{topic_code_examples}

## 任务

请生成更新后的"已学习内容"部分，遵循以下规则：

1. **时间倒序**：最新完成的内容放在最前面
2. **星级评分**：根据总结内容评估掌握程度（1-5星）
3. **精简代码**：从代码示例中提取最关键的部分（不超过30行）
4. **保持格式**：严格遵循下方的输出格式

## 输出格式

## 三、已学习内容

> 📝 **说明**：这里记录了你的学习历程，每次完成知识点后会自动更新。

**当前状态：** 🚀 学习中
**学习统计：** 已完成 X/Y 个知识点（Z%）

### 学习历程

#### [序号]. [知识点名称] ✅

**完成时间：** [当前日期]

**核心收获：**
1. [收获1]
2. [收获2]
3. [收获3]

**关键代码：**
``java
[精简后的关键代码，包含注释]
```

**掌握程度：** ⭐⭐⭐⭐☆ (4/5)

**下一步建议：** [简短建议]

---

[之前的学习内容，按原样保留]

---

> 💡 **提示**：继续保持！点击"下一个知识点"开始新的学习。
"""
