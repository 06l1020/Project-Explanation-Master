"""
业务流程编排器 (Agent Orchestrator)

整合AgentManager和ContextManager，实现完整的业务流程：
1. 项目分析 → 生成overview.md
2. 知识点讲解 → 生成note/{topic}.md
3. 进度更新 → 更新overview.md
4. 问答互动 → 回答用户问题

状态机管理：
IDLE → ANALYZING → TEACHING → QA → TEACHING (循环)
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime

from core.agent_manager import AgentManager
from core.context_manager import ContextManager


class OrchestratorState:
    """编排器状态枚举"""
    IDLE = "idle"                    # 空闲状态
    ANALYZING = "analyzing"          # 正在分析项目
    TEACHING = "teaching"            # 正在讲解知识点
    QA = "qa"                        # 问答模式
    ERROR = "error"                  # 错误状态


class AgentOrchestrator:
    """
    业务流程编排器
    
    职责：
    1. 管理整体业务流程
    2. 协调AgentManager和ContextManager
    3. 文件IO操作（生成和更新Markdown文件）
    4. 状态管理
    5. 错误处理
    """
    
    def __init__(
        self,
        project_path: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model_name: str = "gpt-4",
        temperature: float = 0.7,
        knowledge_tree_path: Optional[str] = None
    ):
        """
        初始化编排器
        
        Args:
            project_path: Java项目根目录
            api_key: LLM API密钥
            base_url: LLM API基础URL
            model_name: 模型名称
            temperature: 温度参数
            knowledge_tree_path: 知识点配置文件路径（可选，默认使用config/knowledge_tree.json）
        """
        self.project_path = Path(project_path)
        self.state = OrchestratorState.IDLE
        
        # 确定knowledge_tree路径
        if knowledge_tree_path is None:
            # 默认使用项目根目录下的config/knowledge_tree.json
            # 如果不存在，使用代码所在目录的config
            current_dir = Path(__file__).parent.parent
            knowledge_tree_path = current_dir / "config" / "knowledge_tree.json"
        
        self.knowledge_tree_path = Path(knowledge_tree_path)
        
        # 初始化核心组件
        try:
            self.agent_mgr = AgentManager(
                api_key=api_key,
                base_url=base_url,
                model_name=model_name,
                temperature=temperature,
                project_path=str(self.project_path)
            )
            
            self.context_mgr = ContextManager(
                project_path=str(self.project_path),
                knowledge_tree_path=str(self.knowledge_tree_path)
            )
            
        except Exception as e:
            self.state = OrchestratorState.ERROR
            raise RuntimeError(f"初始化失败: {e}")
        
        # 文件路径
        self.overview_path = self.project_path / "overview.md"
        self.note_dir = self.project_path / "note"
        
        # 当前状态
        self.current_topic: Optional[Dict] = None
        self.analysis_result: Optional[Dict] = None
    
    def analyze_project(self) -> Dict:
        """
        分析Java项目并生成overview.md
        
        Returns:
            分析结果字典
            
        Raises:
            RuntimeError: 分析失败时抛出
        """
        self.state = OrchestratorState.ANALYZING
        
        try:
            print("🔍 开始分析项目...")
            
            # 1. 构建代码索引（扫描项目结构）
            print("📦 构建代码索引...")
            self.context_mgr.initialize()
            
            # 2. 提取关键代码样本
            code_samples = self._extract_code_samples()
            
            # 3. 获取项目基本信息
            project_info = self._get_project_basic_info()
            
            # 4. 调用Agent进行深度分析（完全基于LLM）
            print("🤖 AI分析中...")
            overview_content = self.agent_mgr.analyze_project(
                project_structure=project_info['structure'],
                dependencies=project_info['dependencies'],
                framework_detected=project_info['framework_hint'],
                code_samples=code_samples
            )
            
            # 5. 保存overview.md
            self._save_overview(overview_content)
            
            # 6. 保存分析结果
            self.analysis_result = {
                'status': 'success',
                'timestamp': datetime.now().isoformat()
            }
            
            self.state = OrchestratorState.IDLE
            print("✅ 项目分析完成！")
            
            return self.analysis_result
            
        except Exception as e:
            self.state = OrchestratorState.ERROR
            error_msg = f"项目分析失败: {str(e)}"
            print(f"❌ {error_msg}")
            
            # 保存错误信息到overview.md
            self._save_error_overview(error_msg)
            
            raise RuntimeError(error_msg) from e
    
    def next_topic(self) -> Optional[Dict]:
        """
        获取并讲解下一个知识点
        
        Returns:
            知识点信息字典，无可用知识点则返回None
        """
        self.state = OrchestratorState.TEACHING
        
        try:
            # 1. 获取下一个知识点
            next_topic = self.context_mgr.get_next_topic()
            
            if next_topic is None:
                print("🎉 所有知识点已完成学习！")
                self.state = OrchestratorState.IDLE
                return None
            
            self.current_topic = next_topic
            print(f"📚 开始讲解: {next_topic['title']}")
            
            # 2. 读取overview.md作为上下文
            overview_content = self._read_overview()
            
            # 3. 获取相关代码上下文
            code_context = self.context_mgr.get_code_context(
                topic=next_topic['title'],
                max_files=5
            )
            
            # 4. 获取已学习的知识点列表
            learned_topics = self._get_learned_topics_text()
            
            # 5. 调用Agent生成讲解内容
            print("🤖 AI生成讲解内容...")
            knowledge_content = self.agent_mgr.teach_knowledge(
                project_overview=overview_content,
                topic_title=next_topic['title'],
                topic_description=next_topic.get('description', ''),
                learned_topics=learned_topics,
                project_code_context=code_context
            )
            
            # 6. 保存知识点讲解文件
            note_file = self._save_knowledge_note(next_topic['id'], knowledge_content)
            
            # 7. 更新overview.md中的进度
            self._update_overview_progress(next_topic['title'], knowledge_content)
            
            # 8. 标记知识点为已完成
            self.context_mgr.complete_topic(
                topic_id=next_topic['id'],
                summary=self._extract_summary(knowledge_content),
                mastery_level=3
            )
            
            # 9. 清除聊天历史（为问答环节准备）
            self.agent_mgr.clear_chat_history()
            
            self.state = OrchestratorState.QA
            print(f"✅ 知识点讲解完成！文件: {note_file}")
            
            return {
                'topic': next_topic,
                'note_file': str(note_file),
                'content': knowledge_content
            }
            
        except Exception as e:
            self.state = OrchestratorState.ERROR
            error_msg = f"知识点讲解失败: {str(e)}"
            print(f"❌ {error_msg}")
            raise RuntimeError(error_msg) from e
    
    def answer_question(self, question: str) -> str:
        """
        回答用户关于当前知识点的问题
        
        Args:
            question: 用户问题
            
        Returns:
            AI回答内容
        """
        if self.state != OrchestratorState.QA:
            raise RuntimeError("当前不在问答模式，请先调用next_topic()")
        
        if not self.current_topic:
            raise RuntimeError("没有当前知识点")
        
        try:
            # 1. 读取overview.md
            overview_content = self._read_overview()
            
            # 2. 调用Agent回答问题
            answer = self.agent_mgr.answer_question(
                project_overview=overview_content,
                current_topic=self.current_topic['title'],
                question=question
            )
            
            return answer
            
        except Exception as e:
            error_msg = f"回答问题失败: {str(e)}"
            print(f"❌ {error_msg}")
            raise RuntimeError(error_msg) from e
    
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
            api_key: API密钥
            base_url: API基础URL
            model_name: 模型名称
            temperature: 温度参数
        """
        self.agent_mgr.update_model_config(
            api_key=api_key,
            base_url=base_url,
            model_name=model_name,
            temperature=temperature
        )
        print(f"✅ 模型配置已更新: {model_name or self.agent_mgr.model_name}")
    
    def get_progress(self) -> Dict:
        """
        获取学习进度
        
        Returns:
            进度信息字典
        """
        return self.context_mgr.get_progress()
    
    def get_token_usage(self) -> Dict:
        """
        获取token使用情况
        
        Returns:
            token使用信息字典
        """
        return self.agent_mgr.token_tracker.get_total_usage()
    
    def get_token_records(self) -> List[Dict]:
        """
        获取token使用记录列表
        
        Returns:
            token使用记录列表
        """
        return self.agent_mgr.token_tracker.get_records()
    
    def get_token_report(self) -> str:
        """
        获取token使用报告
        
        Returns:
            格式化的token使用报告
        """
        return self.agent_mgr.token_tracker.generate_report()
    
    def get_current_state(self) -> str:
        """获取当前状态"""
        return self.state
    
    def reset(self):
        """重置编排器状态"""
        self.state = OrchestratorState.IDLE
        self.current_topic = None
        self.agent_mgr.clear_chat_history()
        print("🔄 编排器已重置")
    
    # ==================== 私有方法 ====================
    
    def _get_project_basic_info(self) -> Dict:
        """
        获取项目基本信息（从代码索引中提取）
        
        Returns:
            包含structure、dependencies、framework_hint的字典
        """
        # 1. 构建项目结构信息
        structure_lines = ["包结构:"]
        packages = {}
        
        for file_path, info in self.context_mgr.code_cache.index.items():
            package = info.get('package', 'default')
            packages[package] = packages.get(package, 0) + 1
        
        for package_name, count in sorted(packages.items()):
            structure_lines.append(f"- {package_name} ({count}个类)")
        
        structure_text = "\n".join(structure_lines) if len(structure_lines) > 1 else "暂无包结构信息"
        
        # 2. 提取依赖信息（从pom.xml或build.gradle）
        dependencies_text = self._extract_dependencies()
        
        # 3. 检测框架提示（基于导入语句）
        framework_hint = self._detect_framework_from_imports()
        
        return {
            'structure': structure_text,
            'dependencies': dependencies_text,
            'framework_hint': framework_hint
        }
    
    def _extract_dependencies(self) -> str:
        """
        从pom.xml或build.gradle提取依赖信息
        
        Returns:
            格式化的依赖列表文本
        """
        pom_path = self.project_path / "pom.xml"
        gradle_path = self.project_path / "build.gradle"
        
        if pom_path.exists():
            return self._parse_pom_dependencies(pom_path)
        elif gradle_path.exists():
            return self._parse_gradle_dependencies(gradle_path)
        else:
            return "未找到依赖配置文件（pom.xml或build.gradle）"
    
    def _parse_pom_dependencies(self, pom_path: Path) -> str:
        """解析Maven POM文件的依赖"""
        try:
            import xml.etree.ElementTree as ET
            
            tree = ET.parse(str(pom_path))
            root = tree.getroot()
            
            # 处理命名空间
            ns = ''
            if root.tag.startswith('{'):
                ns = root.tag.split('}')[0] + '}'
            
            dependencies = []
            for dep in root.findall(f'.//{ns}dependency'):
                group_id = dep.find(f'{ns}groupId')
                artifact_id = dep.find(f'{ns}artifactId')
                version = dep.find(f'{ns}version')
                
                if group_id is not None and artifact_id is not None:
                    gid = group_id.text or 'unknown'
                    aid = artifact_id.text or 'unknown'
                    ver = version.text if version is not None else 'unknown'
                    dependencies.append(f"- `{gid}:{aid}` ({ver})")
            
            return "\n".join(dependencies) if dependencies else "POM文件中未找到依赖项"
            
        except Exception as e:
            return f"解析POM文件失败: {e}"
    
    def _parse_gradle_dependencies(self, gradle_path: Path) -> str:
        """解析Gradle构建文件的依赖（简化版）"""
        try:
            content = gradle_path.read_text(encoding='utf-8')
            
            # 简单的正则匹配（实际应该使用Gradle解析器）
            import re
            pattern = r"(?:implementation|compile)\s+['\"]([^'\"]+)['\"]"
            matches = re.findall(pattern, content)
            
            if matches:
                deps = [f"- `{match}`" for match in matches]
                return "\n".join(deps)
            else:
                return "Gradle文件中未找到依赖项"
                
        except Exception as e:
            return f"解析Gradle文件失败: {e}"
    
    def _detect_framework_from_imports(self) -> str:
        """
        从导入语句中检测框架
        
        Returns:
            检测到的框架名称
        """
        frameworks_detected = set()
        
        # 扫描所有已索引的文件
        for file_path, content in self.context_mgr.code_cache.code_cache.items():
            content_lower = content.lower()
            
            # Spring Boot
            if 'springframework.boot' in content_lower or '@springbootapplication' in content_lower:
                frameworks_detected.add('Spring Boot')
            
            # Spring Cloud
            if 'springframework.cloud' in content_lower:
                frameworks_detected.add('Spring Cloud')
            
            # MyBatis
            if 'mybatis' in content_lower or '@mapper' in content_lower:
                frameworks_detected.add('MyBatis')
            
            # JPA/Hibernate
            if 'javax.persistence' in content_lower or 'jakarta.persistence' in content_lower:
                frameworks_detected.add('JPA/Hibernate')
            
            # Redis
            if 'redis' in content_lower and ('template' in content_lower or 'cache' in content_lower):
                frameworks_detected.add('Redis')
            
            # Lombok
            if 'lombok' in content_lower:
                frameworks_detected.add('Lombok')
        
        if frameworks_detected:
            return ', '.join(sorted(frameworks_detected))
        else:
            return "标准Java项目（未检测到特定框架）"
    
    def _extract_code_samples(self, max_files: int = 8) -> str:
        """
        提取关键代码样本
        
        Args:
            max_files: 最大文件数
            
        Returns:
            格式化的代码样本
        """
        samples = []
        
        # 从代码缓存中获取关键文件
        for file_path, info in list(self.context_mgr.code_cache.index.items())[:max_files]:
            content = self.context_mgr.code_cache.get_file_content(file_path)
            if content:
                samples.append(f"\n### 文件: `{file_path}`\n```java\n{content}\n```\n")
        
        return "\n".join(samples) if samples else "暂无代码样本"
    
    def _save_overview(self, content: str):
        """保存overview.md文件"""
        self.overview_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.overview_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"💾 已保存: {self.overview_path}")
    
    def _save_error_overview(self, error_msg: str):
        """保存错误信息到overview.md"""
        error_content = f"""# ❌ 项目分析失败

> ⚠️ **错误信息**：{error_msg}

## 可能的原因

1. 项目路径不正确或不是有效的Java项目
2. 缺少必要的配置文件（pom.xml或build.gradle）
3. API密钥无效或网络连接问题

## 解决建议

1. 确认项目路径包含 `src/main/java` 目录
2. 检查项目根目录是否有 `pom.xml` 或 `build.gradle`
3. 验证API密钥是否正确配置
4. 检查网络连接是否正常

---

请修正问题后重新尝试分析。
"""
        self._save_overview(error_content)
    
    def _read_overview(self) -> str:
        """读取overview.md文件"""
        if not self.overview_path.exists():
            raise FileNotFoundError(f"overview.md不存在: {self.overview_path}")
        
        with open(self.overview_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _save_knowledge_note(self, topic_id: str, content: str) -> Path:
        """
        保存知识点讲解文件
        
        Args:
            topic_id: 知识点ID
            content: 讲解内容
            
        Returns:
            保存的文件路径
        """
        # 创建note目录
        self.note_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成文件名
        note_file = self.note_dir / f"{topic_id}.md"
        
        # 保存文件
        with open(note_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"💾 已保存: {note_file}")
        
        return note_file
    
    def _update_overview_progress(self, topic_title: str, knowledge_content: str):
        """
        更新overview.md中的学习进度
        
        Args:
            topic_title: 知识点标题
            knowledge_content: 知识点讲解内容
        """
        try:
            # 1. 读取现有overview
            overview_content = self._read_overview()
            
            # 2. 提取总结
            summary = self._extract_summary(knowledge_content)
            
            # 3. 获取已有进度内容
            existing_progress = self._extract_progress_section(overview_content)
            
            # 4. 调用Agent生成更新的进度
            updated_progress = self.agent_mgr.update_progress(
                current_topic=topic_title,
                current_summary=summary,
                existing_progress=existing_progress,
                topic_code_examples=""
            )
            
            # 5. 替换overview中的进度部分
            new_overview = self._replace_progress_section(
                overview_content,
                updated_progress
            )
            
            # 6. 保存更新后的overview
            self._save_overview(new_overview)
            
        except Exception as e:
            print(f"⚠️ 更新进度失败: {e}")
            # 不中断流程，继续执行
    
    def _get_learned_topics_text(self) -> str:
        """获取已学习知识点的文本描述"""
        progress = self.context_mgr.get_progress()
        learned_ids = progress.get('learned_topics', [])
        
        if not learned_ids:
            return "尚未学习任何知识点"
        
        # 从knowledge_tree中获取详细信息
        try:
            with open(self.knowledge_tree_path, 'r', encoding='utf-8') as f:
                knowledge_tree = json.load(f)
            
            topics_info = []
            for topic in knowledge_tree:
                if topic['id'] in learned_ids:
                    topics_info.append(f"- {topic.get('title', topic['id'])}")
            
            return "\n".join(topics_info) if topics_info else "尚未学习任何知识点"
            
        except Exception as e:
            print(f"⚠️ 读取知识点信息失败: {e}")
            return ", ".join(learned_ids)
    
    def _extract_summary(self, content: str, max_length: int = 200) -> str:
        """
        从讲解内容中提取总结
        
        Args:
            content: 讲解内容
            max_length: 最大长度
            
        Returns:
            总结文本
        """
        # 简单策略：取前200字符
        summary = content[:max_length].strip()
        
        # 如果包含句号，在最后一个句号处截断
        if '。' in summary:
            last_period = summary.rfind('。')
            if last_period > 50:  # 至少保留50字符
                summary = summary[:last_period + 1]
        
        return summary
    
    def _extract_progress_section(self, overview_content: str) -> str:
        """
        从overview中提取"已学习内容"部分
        
        Args:
            overview_content: overview.md完整内容
            
        Returns:
            进度部分内容
        """
        # 查找"## 三、已学习内容"章节
        start_marker = "## 三、已学习内容"
        end_markers = ["## 四、", "## 五、"]
        
        start_idx = overview_content.find(start_marker)
        if start_idx == -1:
            return ""
        
        # 查找下一个章节的开始
        end_idx = len(overview_content)
        for marker in end_markers:
            idx = overview_content.find(marker, start_idx + len(start_marker))
            if idx != -1 and idx < end_idx:
                end_idx = idx
        
        return overview_content[start_idx:end_idx].strip()
    
    def _replace_progress_section(self, overview_content: str, new_progress: str) -> str:
        """
        替换overview中的进度部分
        
        Args:
            overview_content: 原文内容
            new_progress: 新的进度内容
            
        Returns:
            更新后的内容
        """
        start_marker = "## 三、已学习内容"
        end_markers = ["## 四、", "## 五、"]
        
        start_idx = overview_content.find(start_marker)
        if start_idx == -1:
            # 如果没有找到，追加到末尾
            return overview_content + "\n\n" + new_progress
        
        # 查找结束位置
        end_idx = len(overview_content)
        for marker in end_markers:
            idx = overview_content.find(marker, start_idx + len(start_marker))
            if idx != -1 and idx < end_idx:
                end_idx = idx
        
        # 替换
        before = overview_content[:start_idx]
        after = overview_content[end_idx:]
        
        return before + new_progress + "\n\n" + after
