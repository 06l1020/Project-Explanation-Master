"""
项目启动脚本

快速启动Java项目分析智能体GUI应用
"""

import sys
import os


def main():
    """主入口函数"""
    try:
        # 添加项目根目录到Python路径
        project_root = os.path.dirname(os.path.abspath(__file__))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        # 导入并启动GUI
        from gui.main_window import main as gui_main
        gui_main()
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("\n请确保已安装必要的依赖:")
        print("  pip install langchain langchain-openai openai tiktoken")
        sys.exit(1)
    
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
