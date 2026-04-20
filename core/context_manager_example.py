"""
ContextManager 使用示例

演示如何使用上下文管理器进行代码缓存和进度跟踪
"""

from core.context_manager import ContextManager, CodeIndexCache, LearningProgressTracker


def example_context_manager():
    """ContextManager 完整使用示例"""
    
    # 1. 初始化上下文管理器
    context_mgr = ContextManager(
        project_path="path/to/your/java/project",
        knowledge_tree_path="config/knowledge_tree.json"
    )
    
    # 2. 初始化（构建代码索引）
    print("正在构建代码索引...")
    context_mgr.initialize()
    
    # 3. 查看索引统计
    stats = context_mgr.code_cache.get_index_summary()
    print(f"\n索引统计:")
    print(f"  总文件数: {stats['total_files']}")
    print(f"  层级分布: {stats['layer_distribution']}")
    print(f"  总大小: {stats['total_size']} 字符")
    
    # 4. 获取下一个知识点
    next_topic = context_mgr.get_next_topic()
    if next_topic:
        print(f"\n下一个知识点: {next_topic['title']}")
        
        # 5. 获取相关代码上下文
        code_context = context_mgr.get_code_context(
            topic=next_topic['title'],
            max_files=3
        )
        print(f"\n相关代码:\n{code_context[:500]}...")  # 只显示前500字符
    
    # 6. 完成一个知识点
    if next_topic:
        context_mgr.complete_topic(
            topic_id=next_topic['id'],
            summary="学习了Spring Boot的核心概念",
            mastery_level=4
        )
    
    # 7. 查看学习进度
    progress = context_mgr.get_progress()
    print(f"\n学习进度:")
    print(f"  已完成: {progress['completed_topics']}/{progress['total_topics']}")
    print(f"  进度百分比: {progress['progress_percentage']:.1f}%")
    
    # 8. 保存进度到文件
    context_mgr.progress_tracker.save_to_file("learning_progress.json")
    print("\n✅ 进度已保存到 learning_progress.json")


def example_code_cache_only():
    """单独使用代码索引缓存"""
    
    cache = CodeIndexCache("path/to/java/project")
    
    # 构建索引
    cache.build_index(max_files=30, max_file_size=2000)
    
    # 获取特定主题的相关代码
    code = cache.get_relevant_code("Controller层开发", max_files=3)
    print(code)
    
    # 获取指定文件内容
    content = cache.get_file_content("src/main/java/com/example/DemoApplication.java")
    if content:
        print(f"文件大小: {len(content)} 字符")


def example_progress_tracker_only():
    """单独使用学习进度跟踪器"""
    
    tracker = LearningProgressTracker("config/knowledge_tree.json")
    
    # 加载之前的进度（如果存在）
    tracker.load_from_file("learning_progress.json")
    
    # 标记知识点完成
    tracker.mark_topic_completed(
        topic_id="core_java",
        summary="掌握了Java基础语法和面向对象编程",
        mastery_level=5
    )
    
    tracker.mark_topic_completed(
        topic_id="spring_boot",
        summary="理解了Spring Boot自动配置原理",
        mastery_level=4
    )
    
    # 获取下一个知识点
    next_topic = tracker.get_next_topic()
    if next_topic:
        print(f"建议学习: {next_topic['title']}")
        print(f"难度: {next_topic.get('difficulty', 'N/A')}")
        print(f"前置条件: {next_topic.get('prerequisites', [])}")
    
    # 查看进度
    progress = tracker.get_progress_summary()
    print(f"\n进度: {progress['progress_percentage']:.1f}%")
    
    # 保存进度
    tracker.save_to_file("learning_progress.json")


if __name__ == "__main__":
    print("ContextManager 使用示例\n")
    print("=" * 60)
    
    # 注意：运行此示例需要有效的Java项目路径
    # example_context_manager()
    
    print("\n提示：取消注释example_context_manager()并配置项目路径后即可运行")
