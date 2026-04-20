"""
GUI主窗口 - Java项目分析智能体

使用Tkinter实现图形界面，集成AgentOrchestrator
功能：
1. 项目路径选择（图形化）
2. 模型配置（API Key、Base URL、Model Name）
3. 项目分析与知识点讲解
4. Markdown内容展示
5. 问答互动
6. 学习进度可视化
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
from pathlib import Path
from typing import Optional

from core.orchestrator import AgentOrchestrator, OrchestratorState


class MainWindow:
    """
    主窗口类
    
    界面布局：
    ┌──────────────────────────────────────┐
    │         内容显示区域 (3/4)            │
    │  ┌──────────────┬─────────────────┐  │
    │  │  Markdown展示 │   聊天历史      │  │
    │  │              │                 │  │
    │  └──────────────┴─────────────────┘  │
    ├──────────────────────────────────────┤
    │         按钮层 (1/16)                 │
    │  [选择项目] [分析] [下一知识点] [提问]│
    ├──────────────────────────────────────┤
    │         输入框 (3/16)                 │
    │  [_______________________________]    │
    └──────────────────────────────────────┘
    """
    
    def __init__(self, root: tk.Tk):
        """
        初始化主窗口
        
        Args:
            root: Tkinter根窗口
        """
        self.root = root
        self.root.title("Java项目分析智能体")
        self.root.geometry("1200x800")
        
        # 状态变量
        self.orchestrator: Optional[AgentOrchestrator] = None
        self.project_path: Optional[str] = None
        self.is_processing = False
        
        # API配置
        self.api_key_var = tk.StringVar()
        self.base_url_var = tk.StringVar(value="")
        self.model_name_var = tk.StringVar(value="gpt-4")
        
        # 创建界面
        self._create_widgets()
        
        # 设置最小窗口大小
        self.root.minsize(1000, 700)
    
    def _create_widgets(self):
        """创建所有UI组件"""
        
        # ==================== 顶部工具栏 ====================
        toolbar = ttk.Frame(self.root, padding=5)
        toolbar.pack(fill=tk.X)
        
        # 项目路径显示
        ttk.Label(toolbar, text="项目路径:").pack(side=tk.LEFT, padx=5)
        self.project_path_var = tk.StringVar(value="未选择项目")
        path_entry = ttk.Entry(toolbar, textvariable=self.project_path_var, width=50, state='readonly')
        path_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # 选择项目按钮
        ttk.Button(toolbar, text="📁 选择项目", command=self._select_project).pack(side=tk.LEFT, padx=5)
        
        # 模型配置按钮
        ttk.Button(toolbar, text="⚙️ 模型配置", command=self._show_model_config).pack(side=tk.LEFT, padx=5)
        
        # ==================== 内容显示区域 (3/4) ====================
        content_frame = ttk.Frame(self.root)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 创建Notebook用于切换视图
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Markdown展示
        markdown_frame = ttk.Frame(self.notebook)
        self.notebook.add(markdown_frame, text="📄 文档查看")
        
        # Markdown文本框（只读）
        self.markdown_text = scrolledtext.ScrolledText(
            markdown_frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            state=tk.DISABLED
        )
        self.markdown_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab 2: 聊天历史
        chat_frame = ttk.Frame(self.notebook)
        self.notebook.add(chat_frame, text="💬 问答记录")
        
        # 聊天文本框（只读）
        self.chat_text = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            font=("Microsoft YaHei", 10),
            state=tk.DISABLED
        )
        self.chat_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab 3: 学习进度
        progress_frame = ttk.Frame(self.notebook)
        self.notebook.add(progress_frame, text="📊 学习进度")
        
        # 进度信息
        self.progress_info = ttk.Label(progress_frame, text="尚未开始学习", font=("Microsoft YaHei", 12))
        self.progress_info.pack(pady=20)
        
        # 进度条
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            orient=tk.HORIZONTAL,
            length=400,
            mode='determinate'
        )
        self.progress_bar.pack(pady=10)
        
        # 进度详情
        self.progress_details = scrolledtext.ScrolledText(
            progress_frame,
            wrap=tk.WORD,
            font=("Microsoft YaHei", 10),
            height=15,
            state=tk.DISABLED
        )
        self.progress_details.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Tab 4: Token消耗
        token_frame = ttk.Frame(self.notebook)
        self.notebook.add(token_frame, text="💰 Token消耗")
        
        # Token统计信息
        self.token_stats_label = ttk.Label(
            token_frame,
            text="尚未产生Token消耗",
            font=("Microsoft YaHei", 12)
        )
        self.token_stats_label.pack(pady=10)
        
        # Token消耗表格
        token_table_frame = ttk.Frame(token_frame)
        token_table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 创建Treeview表格
        columns = ("时间", "操作", "模型", "输入Token", "输出Token", "总Token")
        self.token_tree = ttk.Treeview(
            token_table_frame,
            columns=columns,
            show="headings",
            height=15
        )
        
        # 定义列
        self.token_tree.heading("时间", text="时间")
        self.token_tree.heading("操作", text="操作")
        self.token_tree.heading("模型", text="模型")
        self.token_tree.heading("输入Token", text="输入Token")
        self.token_tree.heading("输出Token", text="输出Token")
        self.token_tree.heading("总Token", text="总Token")
        
        # 设置列宽
        self.token_tree.column("时间", width=150, anchor=tk.CENTER)
        self.token_tree.column("操作", width=120, anchor=tk.CENTER)
        self.token_tree.column("模型", width=120, anchor=tk.CENTER)
        self.token_tree.column("输入Token", width=100, anchor=tk.E)
        self.token_tree.column("输出Token", width=100, anchor=tk.E)
        self.token_tree.column("总Token", width=100, anchor=tk.E)
        
        # 添加滚动条
        token_scrollbar = ttk.Scrollbar(token_table_frame, orient=tk.VERTICAL, command=self.token_tree.yview)
        self.token_tree.configure(yscrollcommand=token_scrollbar.set)
        
        self.token_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        token_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Token报告按钮
        token_btn_frame = ttk.Frame(token_frame)
        token_btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(
            token_btn_frame,
            text="📄 生成Token报告",
            command=self._show_token_report
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            token_btn_frame,
            text="🗑️ 清空记录",
            command=self._clear_token_records
        ).pack(side=tk.LEFT, padx=5)
        
        # ==================== 状态栏 ====================
        status_frame = ttk.Frame(self.root, padding=5)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_var = tk.StringVar(value="✅ 就绪")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, foreground="green")
        status_label.pack(side=tk.LEFT)
        
        # ==================== 按钮层 (1/16) ====================
        button_frame = ttk.Frame(self.root, padding=10)
        button_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        # 左侧按钮组
        left_buttons = ttk.Frame(button_frame)
        left_buttons.pack(side=tk.LEFT)
        
        self.analyze_btn = ttk.Button(
            left_buttons,
            text="🔍 分析项目",
            command=self._analyze_project,
            state=tk.DISABLED
        )
        self.analyze_btn.pack(side=tk.LEFT, padx=5)
        
        self.next_topic_btn = ttk.Button(
            left_buttons,
            text="📚 下一个知识点",
            command=self._next_topic,
            state=tk.DISABLED
        )
        self.next_topic_btn.pack(side=tk.LEFT, padx=5)
        
        # 右侧按钮组
        right_buttons = ttk.Frame(button_frame)
        right_buttons.pack(side=tk.RIGHT)
        
        self.ask_btn = ttk.Button(
            right_buttons,
            text="💬 提问",
            command=self._ask_question,
            state=tk.DISABLED
        )
        self.ask_btn.pack(side=tk.LEFT, padx=5)
        
        self.reset_btn = ttk.Button(
            right_buttons,
            text="🔄 重置",
            command=self._reset
        )
        self.reset_btn.pack(side=tk.LEFT, padx=5)
        
        # ==================== 输入框 (3/16) ====================
        input_frame = ttk.Frame(self.root, padding=10)
        input_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        ttk.Label(input_frame, text="你的问题:").pack(side=tk.LEFT, padx=5)
        
        self.question_var = tk.StringVar()
        self.question_entry = ttk.Entry(
            input_frame,
            textvariable=self.question_var,
            font=("Microsoft YaHei", 11)
        )
        self.question_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.question_entry.bind('<Return>', lambda e: self._ask_question())
        
        # 禁用输入框直到可以提问
        self.question_entry.config(state=tk.DISABLED)
    
    def _select_project(self):
        """选择Java项目目录"""
        project_dir = filedialog.askdirectory(title="选择Java项目根目录")
        
        if project_dir:
            # 验证是否为有效的Java项目
            src_java = Path(project_dir) / "src" / "main" / "java"
            if not src_java.exists():
                messagebox.showwarning(
                    "警告",
                    f"选择的目录似乎不是有效的Java项目\n未找到: {src_java}"
                )
                return
            
            self.project_path = project_dir
            self.project_path_var.set(project_dir)
            self.analyze_btn.config(state=tk.NORMAL)
            self.status_var.set(f"✅ 已选择项目: {project_dir}")
            
            # 尝试初始化Orchestrator
            self._init_orchestrator()
    
    def _init_orchestrator(self):
        """初始化编排器"""
        if not self.project_path:
            return
        
        try:
            api_key = self.api_key_var.get() or os.getenv("OPENAI_API_KEY")
            
            if not api_key:
                messagebox.showwarning(
                    "警告",
                    "请先配置API密钥！\n点击'模型配置'按钮进行设置。"
                )
                return
            
            kwargs = {
                'project_path': self.project_path,
                'api_key': api_key,
                'model_name': self.model_name_var.get()
            }
            
            if self.base_url_var.get():
                kwargs['base_url'] = self.base_url_var.get()
            
            self.orchestrator = AgentOrchestrator(**kwargs)
            self.status_var.set("✅ 编排器初始化成功")
            
        except Exception as e:
            messagebox.showerror("错误", f"初始化失败:\n{str(e)}")
            self.orchestrator = None
    
    def _analyze_project(self):
        """异步执行项目分析"""
        if not self.orchestrator:
            self._init_orchestrator()
            if not self.orchestrator:
                return
        
        # 禁用按钮防止重复点击
        self._set_processing_state(True)
        self.status_var.set("⏳ 正在分析项目...")
        
        # 在后台线程执行
        thread = threading.Thread(target=self._do_analyze_project, daemon=True)
        thread.start()
    
    def _do_analyze_project(self):
        """实际执行项目分析（后台线程）"""
        try:
            result = self.orchestrator.analyze_project()
            
            # 读取overview.md内容
            overview_path = Path(self.project_path) / "overview.md"
            if overview_path.exists():
                content = overview_path.read_text(encoding='utf-8')
                
                # 在主线程更新UI
                self.root.after(0, lambda: self._update_markdown_display(content))
                self.root.after(0, lambda: self.next_topic_btn.config(state=tk.NORMAL))
                self.root.after(0, lambda: self.status_var.set("✅ 项目分析完成"))
                
                # 更新Token消耗显示
                self.root.after(0, self._update_token_display)
            
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: messagebox.showerror("分析失败", error_msg))
            self.root.after(0, lambda: self.status_var.set(f"❌ 分析失败: {error_msg}"))
        
        finally:
            self.root.after(0, lambda: self._set_processing_state(False))
    
    def _next_topic(self):
        """异步获取下一个知识点"""
        if not self.orchestrator:
            return
        
        self._set_processing_state(True)
        self.status_var.set("⏳ 正在生成知识点讲解...")
        
        thread = threading.Thread(target=self._do_next_topic, daemon=True)
        thread.start()
    
    def _do_next_topic(self):
        """实际执行知识点讲解（后台线程）"""
        try:
            topic_result = self.orchestrator.next_topic()
            
            if topic_result is None:
                self.root.after(0, lambda: messagebox.showinfo("提示", "🎉 所有知识点已完成学习！"))
                self.root.after(0, lambda: self.status_var.set("✅ 学习完成"))
                return
            
            # 显示知识点内容
            content = topic_result['content']
            topic_title = topic_result['topic']['title']
            
            self.root.after(0, lambda: self._update_markdown_display(content))
            self.root.after(0, lambda: self._add_chat_message(f"📚 开始学习: {topic_title}", ""))
            self.root.after(0, lambda: self.question_entry.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.ask_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.status_var.set(f"✅ 知识点: {topic_title}"))
            
            # 切换到Markdown视图
            self.root.after(0, lambda: self.notebook.select(0))
            
            # 更新进度显示
            self.root.after(0, self._update_progress_display)
            
            # 更新Token消耗显示
            self.root.after(0, self._update_token_display)
            
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: messagebox.showerror("讲解失败", error_msg))
            self.root.after(0, lambda: self.status_var.set(f"❌ 讲解失败: {error_msg}"))
        
        finally:
            self.root.after(0, lambda: self._set_processing_state(False))
    
    def _ask_question(self):
        """异步回答问题"""
        question = self.question_var.get().strip()
        
        if not question:
            messagebox.showwarning("提示", "请输入问题")
            return
        
        if not self.orchestrator:
            return
        
        # 显示用户问题
        self._add_chat_message(question, "", is_user=True)
        self.question_var.set("")  # 清空输入框
        
        self._set_processing_state(True)
        self.status_var.set("⏳ AI思考中...")
        
        thread = threading.Thread(target=lambda: self._do_ask_question(question), daemon=True)
        thread.start()
    
    def _do_ask_question(self, question: str):
        """实际执行问答（后台线程）"""
        try:
            answer = self.orchestrator.answer_question(question)
            
            # 在主线程更新UI
            self.root.after(0, lambda: self._add_chat_message(question, answer))
            self.root.after(0, lambda: self.status_var.set("✅ 回答完成"))
            
            # 切换到聊天视图
            self.root.after(0, lambda: self.notebook.select(1))
            
            # 更新Token消耗显示
            self.root.after(0, self._update_token_display)
            
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: messagebox.showerror("回答失败", error_msg))
            self.root.after(0, lambda: self.status_var.set(f"❌ 回答失败: {error_msg}"))
        
        finally:
            self.root.after(0, lambda: self._set_processing_state(False))
    
    def _update_markdown_display(self, content: str):
        """更新Markdown显示"""
        self.markdown_text.config(state=tk.NORMAL)
        self.markdown_text.delete(1.0, tk.END)
        self.markdown_text.insert(tk.END, content)
        self.markdown_text.config(state=tk.DISABLED)
    
    def _add_chat_message(self, question: str, answer: str, is_user: bool = False):
        """添加聊天消息"""
        self.chat_text.config(state=tk.NORMAL)
        
        if is_user:
            self.chat_text.insert(tk.END, f"\n{'='*60}\n")
            self.chat_text.insert(tk.END, f"👤 你: {question}\n", "user")
        else:
            self.chat_text.insert(tk.END, f"\n{'='*60}\n")
            self.chat_text.insert(tk.END, f"👤 你: {question}\n", "user")
            self.chat_text.insert(tk.END, f"\n🤖 AI助手:\n{answer}\n", "assistant")
        
        self.chat_text.config(state=tk.DISABLED)
        
        # 滚动到底部
        self.chat_text.see(tk.END)
    
    def _update_progress_display(self):
        """更新进度显示"""
        if not self.orchestrator:
            return
        
        try:
            progress = self.orchestrator.get_progress()
            
            # 更新进度信息
            total = progress['total_topics']
            completed = progress['completed_topics']
            percentage = progress['progress_percentage']
            
            self.progress_info.config(text=f"已完成 {completed}/{total} 个知识点 ({percentage:.1f}%)")
            
            # 更新进度条
            self.progress_bar['value'] = percentage
            
            # 更新详细信息
            self.progress_details.config(state=tk.NORMAL)
            self.progress_details.delete(1.0, tk.END)
            
            details_text = f"""总知识点数: {total}
已完成: {completed}
进度百分比: {percentage:.1f}%

已学习的知识点:
"""
            
            learned_topics = progress.get('learned_topics', [])
            if learned_topics:
                for i, topic_id in enumerate(learned_topics, 1):
                    details_text += f"  {i}. {topic_id}\n"
            else:
                details_text += "  暂无\n"
            
            next_topic = progress.get('next_topic')
            if next_topic:
                details_text += f"\n下一个建议学习: {next_topic.get('title', 'N/A')}\n"
                details_text += f"难度等级: {next_topic.get('difficulty', 'N/A')}\n"
            
            self.progress_details.insert(tk.END, details_text)
            self.progress_details.config(state=tk.DISABLED)
            
        except Exception as e:
            print(f"更新进度显示失败: {e}")
    
    def _show_model_config(self):
        """显示模型配置对话框"""
        config_window = tk.Toplevel(self.root)
        config_window.title("模型配置")
        config_window.geometry("500x300")
        config_window.transient(self.root)
        config_window.grab_set()
        
        # API Key
        ttk.Label(config_window, text="API Key:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)
        api_key_entry = ttk.Entry(config_window, textvariable=self.api_key_var, width=40, show="*")
        api_key_entry.grid(row=0, column=1, padx=10, pady=10)
        
        # Base URL
        ttk.Label(config_window, text="Base URL (可选):").grid(row=1, column=0, sticky=tk.W, padx=10, pady=10)
        base_url_entry = ttk.Entry(config_window, textvariable=self.base_url_var, width=40)
        base_url_entry.grid(row=1, column=1, padx=10, pady=10)
        ttk.Label(config_window, text="例: http://localhost:11434/v1", foreground="gray").grid(row=2, column=1, sticky=tk.W, padx=10)
        
        # Model Name
        ttk.Label(config_window, text="模型名称:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=10)
        model_combo = ttk.Combobox(
            config_window,
            textvariable=self.model_name_var,
            values=["gpt-4", "gpt-3.5-turbo", "gpt-4-turbo", "custom"],
            width=37
        )
        model_combo.grid(row=3, column=1, padx=10, pady=10)
        
        # 保存按钮
        def save_config():
            if not self.api_key_var.get():
                messagebox.showwarning("警告", "API Key不能为空")
                return
            
            config_window.destroy()
            messagebox.showinfo("成功", "配置已保存")
            
            # 如果已有orchestrator，更新配置
            if self.orchestrator:
                self.orchestrator.update_model_config(
                    api_key=self.api_key_var.get(),
                    base_url=self.base_url_var.get() or None,
                    model_name=self.model_name_var.get()
                )
        
        ttk.Button(config_window, text="保存", command=save_config).grid(row=4, column=1, sticky=tk.E, padx=10, pady=20)
    
    def _reset(self):
        """重置状态"""
        if self.orchestrator:
            self.orchestrator.reset()
        
        # 清空显示
        self.markdown_text.config(state=tk.NORMAL)
        self.markdown_text.delete(1.0, tk.END)
        self.markdown_text.config(state=tk.DISABLED)
        
        self.chat_text.config(state=tk.NORMAL)
        self.chat_text.delete(1.0, tk.END)
        self.chat_text.config(state=tk.DISABLED)
        
        # 重置按钮状态
        self.next_topic_btn.config(state=tk.DISABLED)
        self.ask_btn.config(state=tk.DISABLED)
        self.question_entry.config(state=tk.DISABLED)
        
        # 重置进度显示
        self.progress_info.config(text="尚未开始学习")
        self.progress_bar['value'] = 0
        self.progress_details.config(state=tk.NORMAL)
        self.progress_details.delete(1.0, tk.END)
        self.progress_details.config(state=tk.DISABLED)
        
        # 重置Token显示
        self.token_stats_label.config(text="尚未产生Token消耗")
        for item in self.token_tree.get_children():
            self.token_tree.delete(item)
        
        self.status_var.set("✅ 已重置")
    
    def _update_token_display(self):
        """更新Token消耗显示"""
        if not self.orchestrator:
            return
        
        try:
            token_usage = self.orchestrator.get_token_usage()
            records = self.orchestrator.get_token_records()
            
            # 更新统计信息
            if token_usage['call_count'] > 0:
                stats_text = (
                    f"总调用次数: {token_usage['call_count']} 次  |  "
                    f"总Token: {token_usage['total_tokens']:,}"
                )
                self.token_stats_label.config(text=stats_text)
            else:
                self.token_stats_label.config(text="尚未产生Token消耗")
            
            # 清空表格
            for item in self.token_tree.get_children():
                self.token_tree.delete(item)
            
            # 填充表格数据（最新的在前）
            for record in reversed(records):
                # 格式化时间
                from datetime import datetime
                timestamp = datetime.fromisoformat(record['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                
                self.token_tree.insert(
                    "",
                    tk.END,
                    values=(
                        timestamp,
                        record['operation'],
                        record['model'],
                        f"{record['prompt_tokens']:,}",
                        f"{record['completion_tokens']:,}",
                        f"{record['total_tokens']:,}"
                    )
                )
                
        except Exception as e:
            print(f"更新Token显示失败: {e}")
    
    def _show_token_report(self):
        """显示Token消耗报告"""
        if not self.orchestrator:
            messagebox.showwarning("提示", "请先选择项目并配置模型")
            return
        
        try:
            report = self.orchestrator.get_token_report()
            
            # 在新窗口显示报告
            report_window = tk.Toplevel(self.root)
            report_window.title("Token消耗报告")
            report_window.geometry("800x600")
            report_window.transient(self.root)
            
            # 报告文本框
            report_text = scrolledtext.ScrolledText(
                report_window,
                wrap=tk.WORD,
                font=("Consolas", 10)
            )
            report_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            report_text.insert(tk.END, report)
            report_text.config(state=tk.DISABLED)
            
            # 关闭按钮
            ttk.Button(
                report_window,
                text="关闭",
                command=report_window.destroy
            ).pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("错误", f"生成报告失败:\n{str(e)}")
    
    def _clear_token_records(self):
        """清空Token记录"""
        if messagebox.askyesno("确认", "确定要清空所有Token记录吗？"):
            if self.orchestrator:
                self.orchestrator.agent_mgr.token_tracker.clear_records()
                self._update_token_display()
                messagebox.showinfo("成功", "Token记录已清空")
    
    def _set_processing_state(self, processing: bool):
        """设置处理状态（禁用/启用按钮）"""
        self.is_processing = processing
        
        if processing:
            self.analyze_btn.config(state=tk.DISABLED)
            self.next_topic_btn.config(state=tk.DISABLED)
            self.ask_btn.config(state=tk.DISABLED)
            self.question_entry.config(state=tk.DISABLED)
        else:
            # 根据当前状态恢复按钮
            if self.project_path:
                self.analyze_btn.config(state=tk.NORMAL)
            
            if self.orchestrator and self.orchestrator.state == OrchestratorState.QA:
                self.next_topic_btn.config(state=tk.NORMAL)
                self.ask_btn.config(state=tk.NORMAL)
                self.question_entry.config(state=tk.NORMAL)


def main():
    """启动GUI应用"""
    root = tk.Tk()
    
    # 设置主题
    style = ttk.Style()
    style.theme_use('clam')
    
    # 配置文本标签样式
    chat_text_tags = {
        'user': {'foreground': 'blue'},
        'assistant': {'foreground': 'green'}
    }
    
    app = MainWindow(root)
    
    # 为聊天框添加标签配置
    app.chat_text.tag_configure("user", foreground="blue", font=("Microsoft YaHei", 10, "bold"))
    app.chat_text.tag_configure("assistant", foreground="green", font=("Microsoft YaHei", 10))
    
    # 居中显示窗口
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'+{x}+{y}')
    
    root.mainloop()


if __name__ == "__main__":
    main()
