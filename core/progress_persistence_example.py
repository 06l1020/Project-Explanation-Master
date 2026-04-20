"""
进度持久化功能使用示例

展示如何利用已有的分析结果和进度记录，避免重复分析
"""

import os
from pathlib import Path
from core.orchestrator import AgentOrchestrator


def example_smart_resume():
    """
    智能恢复示例
    
    场景：用户第二次启动程序，分析同一个项目
    """
    print("=" * 60)
    print("📚 智能恢复学习进度示例")
    print("=" * 60)
    
    # 配置项目路径
    project_path = "path/to/your/java/project"  # 替换为实际路径
    
    # 第一次运行：完整分析
    print("\n【第一次运行】")
    print("-" * 60)
    
    orchestrator = AgentOrchestrator(
        project_path=project_path,
        api_key=os.getenv("OPENAI_API_KEY"),
        model_name="gpt-4"
    )
    
    # 自动检测并恢复进度
    if orchestrator.restore_analysis_if_needed():
        print("✅ 项目分析就绪\n")
    
    # 查看当前进度
    progress = orchestrator.get_progress()
    print(f"📊 当前进度: {progress['completed_topics']}/{progress['total_topics']} "
          f"({progress['progress_percentage']:.1f}%)")
    
    # 讲解下一个知识点
    topic = orchestrator.next_topic()
    if topic:
        print(f"\n📖 正在讲解: {topic['topic']['title']}")
        print(f"💾 笔记已保存: {topic['note_file']}")
        
        # 问答环节
        answer = orchestrator.answer_question("这个知识点在实际项目中如何应用？")
        print(f"\n🤖 AI回答:\n{answer[:200]}...\n")
    
    print("\n" + "=" * 60)
    print("【程序退出，进度已自动保存】")
    print("=" * 60)
    
    # ========================================
    # 第二次运行：智能恢复
    # ========================================
    print("\n\n【第二次运行 - 重新启动程序】")
    print("-" * 60)
    
    # 创建新的编排器实例（模拟重启）
    orchestrator2 = AgentOrchestrator(
        project_path=project_path,
        api_key=os.getenv("OPENAI_API_KEY"),
        model_name="gpt-4"
    )
    
    # 🎯 关键：自动检测到已有分析结果，跳过重复分析
    if orchestrator2.restore_analysis_if_needed():
        print("✅ 项目分析就绪（已跳过重复分析）\n")
    
    # 查看恢复的进度
    progress2 = orchestrator2.get_progress()
    print(f"📊 恢复后的进度: {progress2['completed_topics']}/{progress2['total_topics']} "
          f"({progress2['progress_percentage']:.1f}%)")
    print(f"✅ 已完成的知识点: {', '.join(progress2['learned_topics'])}")
    
    # 继续学习下一个知识点（从上次中断的地方继续）
    print("\n📖 继续学习下一个知识点...")
    topic2 = orchestrator2.next_topic()
    if topic2:
        print(f"📖 正在讲解: {topic2['topic']['title']}")
    
    print("\n✨ 成功实现进度持久化和智能恢复！")


def example_force_reanalyze():
    """
    强制重新分析示例
    
    场景：项目代码发生重大变化，需要重新分析
    """
    print("\n\n" + "=" * 60)
    print("🔄 强制重新分析示例")
    print("=" * 60)
    
    project_path = "path/to/your/java/project"
    
    orchestrator = AgentOrchestrator(
        project_path=project_path,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # 🎯 关键：使用 force=True 参数强制重新分析
    print("⚠️  项目代码已重大更新，强制重新分析...")
    result = orchestrator.analyze_project(force=True)
    
    print(f"✅ 重新分析完成: {result}")


def example_manual_progress_management():
    """
    手动进度管理示例
    
    展示如何手动加载和保存进度
    """
    print("\n\n" + "=" * 60)
    print("🛠️  手动进度管理示例")
    print("=" * 60)
    
    project_path = "path/to/your/java/project"
    
    orchestrator = AgentOrchestrator(
        project_path=project_path,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # 1. 手动检查是否需要分析
    if orchestrator.should_analyze_project():
        print("📝 需要分析项目")
        orchestrator.analyze_project()
    else:
        print("✅ 已有分析结果，可以跳过")
    
    # 2. 获取当前进度
    progress = orchestrator.get_progress()
    print(f"\n📊 学习进度:")
    print(f"   - 总知识点: {progress['total_topics']}")
    print(f"   - 已完成: {progress['completed_topics']}")
    print(f"   - 完成率: {progress['progress_percentage']:.1f}%")
    print(f"   - 已学习: {', '.join(progress['learned_topics'])}")
    
    # 3. 手动保存进度（通常不需要，因为会自动保存）
    orchestrator._save_progress()
    print("\n💾 进度已手动保存")


if __name__ == "__main__":
    # 运行示例
    example_smart_resume()
    example_force_reanalyze()
    example_manual_progress_management()
