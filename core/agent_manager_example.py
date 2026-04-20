"""
AgentManager 使用示例

演示如何使用Agent统一管理器进行项目分析和知识讲解
"""

from core.agent_manager import AgentManager


def example_basic_usage():
    """基本使用示例"""
    
    # 1. 初始化Agent管理器
    agent_mgr = AgentManager(
        api_key="your-api-key-here",  # 或设置环境变量 OPENAI_API_KEY
        base_url=None,  # None则使用OpenAI官方端点
        model_name="gpt-4",
        temperature=0.7
    )
    
    # 2. 项目分析
    overview = agent_mgr.analyze_project(
        project_structure="""
包结构:
- com.example.demo.controller (3个类)
- com.example.demo.service (5个类)
- com.example.demo.model (8个类)
        """,
        dependencies="""
- org.springframework.boot:spring-boot-starter-web (3.2.0)
- org.springframework.boot:spring-boot-starter-data-jpa (3.2.0)
- mysql:mysql-connector-java (8.0.33)
        """,
        framework_detected="Spring Boot 3.2.0 + JPA + MySQL",
        code_samples="""
文件: src/main/java/com/example/demo/DemoApplication.java
```java
@SpringBootApplication
public class DemoApplication {
    public static void main(String[] args) {
        SpringApplication.run(DemoApplication.class, args);
    }
}
```
        """
    )
    
    print("=== 项目分析完成 ===")
    print(overview)
    
    # 保存到文件
    with open("overview.md", "w", encoding="utf-8") as f:
        f.write(overview)
    
    # 3. 知识讲解
    knowledge_content = agent_mgr.teach_knowledge(
        project_overview=overview,
        topic_title="Spring Boot自动配置原理",
        topic_description="理解@SpringBootApplication背后的自动配置机制",
        learned_topics="已完成: Java基础、Maven构建",
        project_code_context="""
项目中的启动类使用了@SpringBootApplication注解：
```java
@SpringBootApplication
public class DemoApplication { ... }
```
        """
    )
    
    print("\n=== 知识讲解完成 ===")
    print(knowledge_content)
    
    # 保存到note目录
    import os
    os.makedirs("note", exist_ok=True)
    with open("note/spring_boot_auto_config.md", "w", encoding="utf-8") as f:
        f.write(knowledge_content)
    
    # 4. 问答互动
    answer = agent_mgr.answer_question(
        project_overview=overview,
        current_topic="Spring Boot自动配置原理",
        question="@ConditionalOnClass是如何工作的？"
    )
    
    print("\n=== 问题回答 ===")
    print(answer)
    
    # 5. 更新学习进度
    progress_update = agent_mgr.update_progress(
        current_topic="Spring Boot自动配置原理",
        current_summary="学习了@SpringBootApplication的三个核心注解...",
        existing_progress="",  # 首次学习为空
        topic_code_examples="""
```java
@SpringBootApplication = 
    @SpringBootConfiguration + 
    @EnableAutoConfiguration + 
    @ComponentScan
```
        """
    )
    
    print("\n=== 进度更新 ===")
    print(progress_update)
    
    # 6. 切换知识点时清除聊天历史
    agent_mgr.clear_chat_history()
    
    # 7. 动态切换模型配置
    agent_mgr.update_model_config(
        model_name="gpt-3.5-turbo",
        temperature=0.5
    )
    
    print("\n=== 模型已切换到 gpt-3.5-turbo ===")


def example_with_custom_api():
    """使用自定义API端点示例（如Ollama、DeepSeek等）"""
    
    # 使用本地Ollama服务
    agent_mgr = AgentManager(
        api_key="ollama",  # Ollama通常不需要真实key
        base_url="http://localhost:11434/v1",
        model_name="llama2",
        temperature=0.7
    )
    
    # 后续使用方式相同
    overview = agent_mgr.analyze_project(
        project_structure="...",
        dependencies="...",
        framework_detected="Spring Boot"
    )
    
    print(overview)


if __name__ == "__main__":
    print("AgentManager 使用示例\n")
    print("=" * 60)
    
    # 注意：运行此示例需要有效的API密钥
    # example_basic_usage()
    
    print("\n提示：取消注释example_basic_usage()并配置API密钥后即可运行")
