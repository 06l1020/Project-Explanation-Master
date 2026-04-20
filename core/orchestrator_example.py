"""
AgentOrchestrator 使用示例

演示完整的业务流程：项目分析 → 知识点讲解 → 问答互动
"""

from core.orchestrator import AgentOrchestrator


def example_full_workflow():
    """完整工作流程示例"""
    
    # 1. 初始化编排器
    orchestrator = AgentOrchestrator(
        project_path="path/to/your/java/project",
        api_key="your-api-key",  # 或设置环境变量 OPENAI_API_KEY
        model_name="gpt-4",
        temperature=0.7
    )
    
    print("=" * 60)
    print("阶段1: 项目分析")
    print("=" * 60)
    
    # 2. 分析项目
    try:
        result = orchestrator.analyze_project()
        print(f"✅ 分析完成: {result}")
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        return
    
    print("\n" + "=" * 60)
    print("阶段2: 知识点学习循环")
    print("=" * 60)
    
    # 3. 学习多个知识点
    for i in range(3):  # 学习3个知识点
        print(f"\n--- 第{i+1}个知识点 ---")
        
        # 获取并讲解下一个知识点
        topic_result = orchestrator.next_topic()
        
        if topic_result is None:
            print("🎉 所有知识点已完成！")
            break
        
        print(f"📚 知识点: {topic_result['topic']['title']}")
        print(f"📄 笔记文件: {topic_result['note_file']}")
        
        # 4. 问答环节
        print("\n💬 问答环节（输入'next'跳过，'quit'退出）")
        while True:
            question = input("\n你的问题: ").strip()
            
            if question.lower() == 'next':
                break
            elif question.lower() == 'quit':
                return
            
            try:
                answer = orchestrator.answer_question(question)
                print(f"\n🤖 AI回答:\n{answer}\n")
            except Exception as e:
                print(f"❌ 回答失败: {e}")
    
    # 5. 查看最终进度
    print("\n" + "=" * 60)
    print("学习进度总结")
    print("=" * 60)
    
    progress = orchestrator.get_progress()
    print(f"总知识点: {progress['total_topics']}")
    print(f"已完成: {progress['completed_topics']}")
    print(f"进度: {progress['progress_percentage']:.1f}%")


def example_simple_usage():
    """简化使用示例"""
    
    # 初始化
    orchestrator = AgentOrchestrator(
        project_path="path/to/java/project",
        api_key="your-api-key"
    )
    
    # 分析项目
    orchestrator.analyze_project()
    
    # 学习一个知识点
    topic = orchestrator.next_topic()
    if topic:
        print(f"学习了: {topic['topic']['title']}")
        
        # 提问
        answer = orchestrator.answer_question("这个知识点在项目哪里用到了？")
        print(answer)
    
    # 查看进度
    progress = orchestrator.get_progress()
    print(f"进度: {progress['progress_percentage']}%")


def example_error_handling():
    """错误处理示例"""
    
    try:
        orchestrator = AgentOrchestrator(
            project_path="invalid/path",
            api_key="your-api-key"
        )
        
        orchestrator.analyze_project()
        
    except RuntimeError as e:
        print(f"❌ 运行时错误: {e}")
        print("建议: 检查项目路径是否正确")
    
    except FileNotFoundError as e:
        print(f"❌ 文件未找到: {e}")
        print("建议: 确认knowledge_tree.json存在")
    
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        import traceback
        traceback.print_exc()


def example_model_switching():
    """动态切换模型示例"""
    
    orchestrator = AgentOrchestrator(
        project_path="path/to/java/project",
        api_key="your-api-key",
        model_name="gpt-4"
    )
    
    # 使用GPT-4进行分析（质量更高）
    orchestrator.analyze_project()
    
    # 切换到GPT-3.5进行知识点讲解（速度更快，成本更低）
    orchestrator.update_model_config(
        model_name="gpt-3.5-turbo",
        temperature=0.7
    )
    
    # 继续学习
    orchestrator.next_topic()
    
    print("✅ 模型已动态切换")


if __name__ == "__main__":
    print("AgentOrchestrator 使用示例\n")
    print("=" * 60)
    
    # 注意：运行此示例需要有效的API密钥和Java项目路径
    # example_full_workflow()
    
    print("\n提示：取消注释example_full_workflow()并配置参数后即可运行")
    print("\n快速开始步骤：")
    print("1. 准备一个Java项目（包含src/main/java目录）")
    print("2. 确保config/knowledge_tree.json存在")
    print("3. 设置API密钥: export OPENAI_API_KEY='sk-xxx'")
    print("4. 修改project_path为你的Java项目路径")
    print("5. 运行示例")
