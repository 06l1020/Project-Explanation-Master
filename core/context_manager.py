"""
上下文管理器
负责管理：
1. 代码索引缓存（避免重复读取项目文件）
2. 学习进度跟踪器
3. 智能代码提取工具
"""

import os
import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class CodeIndexCache:
    """
    代码索引缓存
    
    功能：
    1. 首次分析时建立项目代码索引
    2. 缓存关键文件路径和摘要
    3. 按需提取相关代码片段
    4. 减少Token消耗
    """
    
    def __init__(self, project_path: str):
        """
        初始化代码索引缓存
        
        Args:
            project_path: Java项目根目录路径
        """
        self.project_path = Path(project_path)
        self.index: Dict[str, Dict] = {}  # 文件路径 -> 元数据
        self.code_cache: Dict[str, str] = {}  # 文件路径 -> 代码内容（截断后）
        self._built = False
    
    def build_index(self, max_files: int = 50, max_file_size: int = 3000):
        """
        构建代码索引
        
        按优先级扫描项目文件：
        1. 启动类 (*Application.java)
        2. Controller层
        3. Service层
        4. Model/Entity层
        5. Config配置类
        
        Args:
            max_files: 最大索引文件数
            max_file_size: 单个文件最大字符数（截断限制）
        """
        if self._built:
            return  # 已构建，跳过
        
        src_java_dir = self.project_path / "src" / "main" / "java"
        if not src_java_dir.exists():
            raise FileNotFoundError(f"未找到Java源代码目录: {src_java_dir}")
        
        # 收集所有Java文件
        java_files = list(src_java_dir.rglob("*.java"))
        
        # 按优先级排序
        prioritized_files = self._prioritize_files(java_files)
        
        # 限制文件数量
        selected_files = prioritized_files[:max_files]
        
        # 建立索引
        for file_path in selected_files:
            try:
                relative_path = file_path.relative_to(self.project_path)
                rel_path_str = str(relative_path).replace("\\", "/")
                
                # 读取并截断代码
                content = self._read_and_truncate(file_path, max_file_size)
                
                # 提取包名和类名
                package_name = self._extract_package(content)
                class_name = file_path.stem
                
                # 确定层级类型
                layer_type = self._detect_layer(rel_path_str, content)
                
                # 生成简要摘要
                summary = self._generate_summary(content, class_name)
                
                # 存入索引
                self.index[rel_path_str] = {
                    "full_path": str(file_path),
                    "package": package_name,
                    "class_name": class_name,
                    "layer": layer_type,
                    "summary": summary,
                    "size": len(content)
                }
                
                # 缓存代码内容
                self.code_cache[rel_path_str] = content
                
            except Exception as e:
                print(f"警告: 处理文件 {file_path} 时出错: {e}")
                continue
        
        self._built = True
        print(f"✅ 代码索引构建完成: {len(self.index)} 个文件")
    
    def get_relevant_code(self, topic: str, max_files: int = 5) -> str:
        """
        根据知识点主题提取相关代码
        
        Args:
            topic: 知识点主题（如 "Spring Boot自动配置"）
            max_files: 最多返回的文件数
            
        Returns:
            格式化的代码上下文（Markdown格式）
        """
        if not self._built:
            self.build_index()
        
        # 简单关键词匹配（可扩展为更智能的语义匹配）
        relevant_files = self._find_relevant_files(topic)
        
        if not relevant_files:
            return "暂无相关代码"
        
        # 限制返回数量
        selected = relevant_files[:max_files]
        
        # 格式化输出
        result_lines = []
        for file_path in selected:
            code_content = self.code_cache.get(file_path, "")
            file_info = self.index[file_path]
            
            result_lines.append(f"\n### 文件: `{file_path}`")
            result_lines.append(f"**类名:** {file_info['class_name']}")
            result_lines.append(f"**层级:** {file_info['layer']}")
            result_lines.append(f"**摘要:** {file_info['summary']}")
            result_lines.append("\n```java")
            result_lines.append(code_content)
            result_lines.append("```\n")
        
        return "\n".join(result_lines)
    
    def get_file_content(self, file_path: str) -> Optional[str]:
        """
        获取指定文件的代码内容
        
        Args:
            file_path: 相对路径（如 "src/main/java/com/example/DemoApplication.java"）
            
        Returns:
            代码内容，不存在则返回None
        """
        if not self._built:
            self.build_index()
        
        return self.code_cache.get(file_path)
    
    def get_index_summary(self) -> Dict:
        """
        获取索引摘要统计
        
        Returns:
            包含统计信息的字典
        """
        if not self._built:
            self.build_index()
        
        layer_stats = {}
        for info in self.index.values():
            layer = info['layer']
            layer_stats[layer] = layer_stats.get(layer, 0) + 1
        
        return {
            "total_files": len(self.index),
            "layer_distribution": layer_stats,
            "total_size": sum(info['size'] for info in self.index.values())
        }
    
    # ==================== 私有方法 ====================
    
    def _prioritize_files(self, java_files: List[Path]) -> List[Path]:
        """
        按优先级排序文件
        
        优先级：
        1. 启动类 (包含 @SpringBootApplication)
        2. Controller (@RestController, @Controller)
        3. Service (@Service)
        4. Repository (@Repository)
        5. Model/Entity (@Entity)
        6. Config (@Configuration)
        7. 其他
        """
        priority_map = {
            'application': 1,
            'controller': 2,
            'service': 3,
            'repository': 4,
            'model': 5,
            'config': 6,
            'other': 7
        }
        
        def get_priority(file_path: Path) -> int:
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                layer = self._detect_layer(str(file_path), content)
                return priority_map.get(layer, 7)
            except:
                return 7
        
        return sorted(java_files, key=get_priority)
    
    def _read_and_truncate(self, file_path: Path, max_size: int) -> str:
        """读取文件并截断到指定大小"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            if len(content) > max_size:
                # 保留开头和结尾，中间用省略号
                head = content[:max_size // 2]
                tail = content[-max_size // 2:]
                content = head + "\n\n// ... [代码已截断，共{}字符] ...\n\n".format(len(content)) + tail
            return content
        except Exception as e:
            return f"// 读取失败: {e}"
    
    def _extract_package(self, content: str) -> str:
        """从Java文件中提取包名"""
        for line in content.split('\n'):
            if line.strip().startswith('package '):
                return line.strip()[8:-1]  # 去掉 "package " 和 ";"
        return "default"
    
    def _detect_layer(self, file_path: str, content: str) -> str:
        """检测文件所属层级"""
        content_lower = content.lower()
        
        # 通过注解判断
        if '@springbootapplication' in content_lower:
            return 'application'
        elif '@restcontroller' in content_lower or '@controller' in content_lower:
            return 'controller'
        elif '@service' in content_lower:
            return 'service'
        elif '@repository' in content_lower:
            return 'repository'
        elif '@entity' in content_lower or '@table' in content_lower:
            return 'model'
        elif '@configuration' in content_lower or '@config' in content_lower:
            return 'config'
        
        # 通过路径判断
        if '/controller/' in file_path.lower():
            return 'controller'
        elif '/service/' in file_path.lower():
            return 'service'
        elif '/repository/' in file_path.lower() or '/dao/' in file_path.lower():
            return 'repository'
        elif '/model/' in file_path.lower() or '/entity/' in file_path.lower():
            return 'model'
        elif '/config/' in file_path.lower():
            return 'config'
        
        return 'other'
    
    def _generate_summary(self, content: str, class_name: str) -> str:
        """生成文件摘要"""
        # 提取类上的注释
        lines = content.split('\n')
        comments = []
        in_comment = False
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('/**'):
                in_comment = True
                comments.append(stripped[3:])
            elif in_comment:
                if stripped.endswith('*/'):
                    comments.append(stripped[:-2])
                    break
                else:
                    comments.append(stripped.lstrip('*').strip())
        
        if comments:
            return ' '.join(comments).strip()[:100]  # 限制长度
        
        return f"{class_name} 类"
    
    def _find_relevant_files(self, topic: str) -> List[str]:
        """
        根据主题查找相关文件
        
        简单的关键词匹配策略
        """
        topic_lower = topic.lower()
        relevant = []
        
        # 定义主题到层级的映射
        topic_keywords = {
            'controller': ['controller', '控制器', 'api', '接口', 'web'],
            'service': ['service', '服务', '业务逻辑'],
            'repository': ['repository', 'dao', '数据访问', '数据库'],
            'model': ['model', 'entity', '实体', '数据模型'],
            'config': ['config', '配置', '自动配置', 'bean'],
            'spring boot': ['application', '启动', 'springboot'],
        }
        
        # 确定要搜索的层级
        target_layers = []
        for keyword_layer, keywords in topic_keywords.items():
            if any(kw in topic_lower for kw in keywords):
                target_layers.append(keyword_layer)
        
        if not target_layers:
            # 如果没有匹配，返回所有文件
            target_layers = ['application', 'controller', 'service', 'config']
        
        # 筛选文件
        for file_path, info in self.index.items():
            if info['layer'] in target_layers:
                relevant.append(file_path)
        
        return relevant


class LearningProgressTracker:
    """
    学习进度跟踪器
    
    功能：
    1. 记录已学习的知识点
    2. 计算学习进度百分比
    3. 推荐下一个知识点
    4. 持久化到文件
    """
    
    def __init__(self, knowledge_tree_path: str):
        """
        初始化进度跟踪器
        
        Args:
            knowledge_tree_path: knowledge_tree.json 文件路径
        """
        self.knowledge_tree_path = Path(knowledge_tree_path)
        self.knowledge_tree = self._load_knowledge_tree()
        self.learned_topics: List[str] = []  # 已学习的知识点ID列表
        self.topic_details: Dict[str, Dict] = {}  # 知识点详细信息
    
    def mark_topic_completed(self, topic_id: str, summary: str = "", mastery_level: int = 3):
        """
        标记知识点已完成
        
        Args:
            topic_id: 知识点ID
            summary: 学习总结
            mastery_level: 掌握程度 (1-5)
        """
        if topic_id not in self.learned_topics:
            self.learned_topics.append(topic_id)
        
        self.topic_details[topic_id] = {
            "completed_at": self._get_current_time(),
            "summary": summary,
            "mastery_level": min(5, max(1, mastery_level))
        }
    
    def get_next_topic(self) -> Optional[Dict]:
        """
        获取下一个应该学习的知识点
        
        基于依赖关系和难度排序
        
        Returns:
            知识点信息字典，无可用知识点则返回None
        """
        # 过滤出未学习的知识点
        available_topics = [
            topic for topic in self.knowledge_tree
            if topic['id'] not in self.learned_topics
        ]
        
        if not available_topics:
            return None
        
        # 检查前置条件
        ready_topics = []
        for topic in available_topics:
            prerequisites = topic.get('prerequisites', [])
            if all(prereq in self.learned_topics for prereq in prerequisites):
                ready_topics.append(topic)
        
        if not ready_topics:
            # 如果所有未学习知识点都有未满足的前置条件，返回第一个
            return available_topics[0]
        
        # 按难度排序（简单到复杂）
        ready_topics.sort(key=lambda x: x.get('difficulty', 0))
        
        return ready_topics[0]
    
    def get_progress_percentage(self) -> float:
        """获取学习进度百分比"""
        if not self.knowledge_tree:
            return 0.0
        
        total = len(self.knowledge_tree)
        completed = len(self.learned_topics)
        
        return (completed / total * 100) if total > 0 else 0.0
    
    def get_progress_summary(self) -> Dict:
        """
        获取进度摘要
        
        Returns:
            包含进度信息的字典
        """
        return {
            "total_topics": len(self.knowledge_tree),
            "completed_topics": len(self.learned_topics),
            "progress_percentage": self.get_progress_percentage(),
            "learned_topics": self.learned_topics,
            "next_topic": self.get_next_topic()
        }
    
    def save_to_file(self, output_path: str):
        """
        保存进度到文件
        
        Args:
            output_path: 输出文件路径
        """
        data = {
            "learned_topics": self.learned_topics,
            "topic_details": self.topic_details,
            "progress_percentage": self.get_progress_percentage(),
            "last_updated": self._get_current_time()
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_from_file(self, input_path: str):
        """
        从文件加载进度
        
        Args:
            input_path: 输入文件路径
        """
        if not Path(input_path).exists():
            return
        
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.learned_topics = data.get('learned_topics', [])
        self.topic_details = data.get('topic_details', {})
    
    # ==================== 私有方法 ====================
    
    def _load_knowledge_tree(self) -> List[Dict]:
        """加载知识点树配置"""
        if not self.knowledge_tree_path.exists():
            raise FileNotFoundError(f"知识点配置文件不存在: {self.knowledge_tree_path}")
        
        with open(self.knowledge_tree_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _get_current_time(self) -> str:
        """获取当前时间字符串"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class ContextManager:
    """
    上下文管理器（统一入口）
    
    整合代码索引缓存和学习进度跟踪
    """
    
    def __init__(self, project_path: str, knowledge_tree_path: str):
        """
        初始化上下文管理器
        
        Args:
            project_path: Java项目根目录
            knowledge_tree_path: knowledge_tree.json 路径
        """
        self.code_cache = CodeIndexCache(project_path)
        self.progress_tracker = LearningProgressTracker(knowledge_tree_path)
    
    def initialize(self):
        """初始化（构建代码索引）"""
        self.code_cache.build_index()
    
    def get_code_context(self, topic: str, max_files: int = 5) -> str:
        """
        获取知识点相关的代码上下文
        
        Args:
            topic: 知识点主题
            max_files: 最大文件数
            
        Returns:
            格式化的代码上下文
        """
        return self.code_cache.get_relevant_code(topic, max_files)
    
    def get_next_topic(self) -> Optional[Dict]:
        """获取下一个知识点"""
        return self.progress_tracker.get_next_topic()
    
    def complete_topic(self, topic_id: str, summary: str = "", mastery_level: int = 3):
        """
        完成一个知识点
        
        Args:
            topic_id: 知识点ID
            summary: 学习总结
            mastery_level: 掌握程度 (1-5)
        """
        self.progress_tracker.mark_topic_completed(topic_id, summary, mastery_level)
    
    def get_progress(self) -> Dict:
        """获取学习进度"""
        return self.progress_tracker.get_progress_summary()
