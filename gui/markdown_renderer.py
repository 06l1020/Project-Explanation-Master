"""
Markdown 渲染组件

将 Markdown 文本渲染为 Tkinter Text 组件的富文本格式
支持：标题、代码块、列表、链接、粗体、斜体等
"""

import tkinter as tk
from tkinter import font as tkfont
from typing import Dict, List, Tuple, Optional
import re
import markdown


class MarkdownRenderer:
    """
    Markdown 渲染器
    
    将 Markdown 文本解析并渲染到 Tkinter Text 组件
    """
    
    # 主题颜色配置
    THEMES = {
        "light": {
            "name": "亮色主题",
            "bg": "#ffffff",
            "fg": "#24292e",
            "heading1_fg": "#24292e",
            "heading2_fg": "#24292e",
            "heading3_fg": "#24292e",
            "code_bg": "#f6f8fa",
            "code_fg": "#24292e",
            "blockquote_bg": "#f6f8fa",
            "blockquote_fg": "#586069",
            "link_fg": "#0366d6",
            "bold_fg": "#24292e",
            "italic_fg": "#24292e",
            "cursor_fg": "#24292e",
            "select_bg": "#c8c8c8",
        },
        "dark": {
            "name": "暗色主题",
            "bg": "#1e1e1e",
            "fg": "#d4d4d4",
            "heading1_fg": "#ffffff",
            "heading2_fg": "#e0e0e0",
            "heading3_fg": "#d0d0d0",
            "code_bg": "#2d2d2d",
            "code_fg": "#d4d4d4",
            "blockquote_bg": "#2d2d2d",
            "blockquote_fg": "#8b949e",
            "link_fg": "#58a6ff",
            "bold_fg": "#ffffff",
            "italic_fg": "#d4d4d4",
            "cursor_fg": "#ffffff",
            "select_bg": "#4a4a4a",
        },
        "eye_care": {
            "name": "护眼主题",
            "bg": "#c7edcc",
            "fg": "#2d3e3e",
            "heading1_fg": "#1a2e2e",
            "heading2_fg": "#2d3e3e",
            "heading3_fg": "#3d4e4e",
            "code_bg": "#b8d8be",
            "code_fg": "#1a2e2e",
            "blockquote_bg": "#b8d8be",
            "blockquote_fg": "#4a5d5d",
            "link_fg": "#2e5c8a",
            "bold_fg": "#1a2e2e",
            "italic_fg": "#2d3e3e",
            "cursor_fg": "#1a2e2e",
            "select_bg": "#98c8a0",
        },
    }
    
    # 字体大小基准
    FONT_SIZES = {
        "small": {"base": 10, "h1": 20, "h2": 18, "h3": 16, "h4": 14, "code": 9},
        "medium": {"base": 12, "h1": 24, "h2": 20, "h3": 18, "h4": 15, "code": 10},
        "large": {"base": 14, "h1": 28, "h2": 24, "h3": 20, "h4": 17, "code": 11},
        "xlarge": {"base": 16, "h1": 32, "h2": 28, "h3": 24, "h4": 19, "code": 12},
    }
    
    def __init__(self, text_widget: tk.Text, theme: str = "light", font_size: str = "medium"):
        """
        初始化 Markdown 渲染器
        
        Args:
            text_widget: Tkinter Text 组件
            theme: 主题名称 (light/dark/eye_care)
            font_size: 字体大小 (small/medium/large/xlarge)
        """
        self.text_widget = text_widget
        self.theme = theme
        self.font_size = font_size
        self._tag_configs: Dict[str, Dict] = {}
        self._setup_tags()
    
    def _setup_tags(self):
        """配置文本标签样式"""
        colors = self.THEMES[self.theme]
        sizes = self.FONT_SIZES[self.font_size]
        
        # 配置基础字体
        base_font = tkfont.Font(family="Consolas", size=sizes["base"])
        heading1_font = tkfont.Font(family="Microsoft YaHei", size=sizes["h1"], weight="bold")
        heading2_font = tkfont.Font(family="Microsoft YaHei", size=sizes["h2"], weight="bold")
        heading3_font = tkfont.Font(family="Microsoft YaHei", size=sizes["h3"], weight="bold")
        heading4_font = tkfont.Font(family="Microsoft YaHei", size=sizes["h4"], weight="bold")
        code_font = tkfont.Font(family="Consolas", size=sizes["code"])
        bold_font = tkfont.Font(family="Microsoft YaHei", size=sizes["base"], weight="bold")
        italic_font = tkfont.Font(family="Microsoft YaHei", size=sizes["base"], slant="italic")
        
        # 存储字体引用
        self._fonts = {
            "base": base_font,
            "h1": heading1_font,
            "h2": heading2_font,
            "h3": heading3_font,
            "h4": heading4_font,
            "code": code_font,
            "bold": bold_font,
            "italic": italic_font,
        }
        
        # 配置 Text 组件背景色
        self.text_widget.configure(
            bg=colors["bg"],
            fg=colors["fg"],
            font=base_font,
            insertbackground=colors["cursor_fg"],
            selectbackground=colors["select_bg"],
        )
        
        # 定义标签配置 (只使用 Text 组件支持的选项)
        tag_configs = {
            "heading1": {"font": heading1_font, "foreground": colors["heading1_fg"]},
            "heading2": {"font": heading2_font, "foreground": colors["heading2_fg"]},
            "heading3": {"font": heading3_font, "foreground": colors["heading3_fg"]},
            "heading4": {"font": heading4_font, "foreground": colors["heading3_fg"]},
            "code": {"font": code_font, "background": colors["code_bg"], "foreground": colors["code_fg"]},
            "code_block": {"font": code_font, "background": colors["code_bg"], "foreground": colors["code_fg"]},
            "blockquote": {"font": base_font, "foreground": colors["blockquote_fg"], "background": colors["blockquote_bg"]},
            "link": {"font": base_font, "foreground": colors["link_fg"], "underline": True},
            "bold": {"font": bold_font, "foreground": colors["bold_fg"]},
            "italic": {"font": italic_font, "foreground": colors["italic_fg"]},
            "list_item": {"font": base_font},
            "paragraph": {"font": base_font},
        }
        
        # 应用标签配置
        for tag_name, config in tag_configs.items():
            self.text_widget.tag_configure(tag_name, **config)
        
        self._tag_configs = tag_configs
    
    def apply_theme(self, theme: str):
        """
        应用主题
        
        Args:
            theme: 主题名称 (light/dark/eye_care)
        """
        if theme not in self.THEMES:
            raise ValueError(f"未知主题：{theme}")
        self.theme = theme
        self._setup_tags()
    
    def apply_font_size(self, size: str):
        """
        应用字体大小
        
        Args:
            size: 字体大小 (small/medium/large/xlarge)
        """
        if size not in self.FONT_SIZES:
            raise ValueError(f"未知字体大小：{size}")
        self.font_size = size
        self._setup_tags()
    
    def render(self, markdown_text: str):
        """
        渲染 Markdown 文本
        
        Args:
            markdown_text: Markdown 格式的文本
        """
        # 清空文本框
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete(1.0, tk.END)
        
        # 使用 markdown 库解析
        html = markdown.markdown(
            markdown_text,
            extensions=['extra', 'codehilite', 'toc']
        )
        
        # 简化的 Markdown 解析（逐行处理）
        self._render_markdown_simple(markdown_text)
        
        self.text_widget.config(state=tk.DISABLED)
    
    def _render_markdown_simple(self, text: str):
        """
        简化的 Markdown 渲染器（逐行解析）
        
        Args:
            text: Markdown 文本
        """
        lines = text.split('\n')
        i = 0
        in_code_block = False
        code_block_content = []
        in_list = False
        
        while i < len(lines):
            line = lines[i]
            
            # 代码块处理
            if line.startswith('```'):
                if in_code_block:
                    # 结束代码块
                    self._insert_code_block('\n'.join(code_block_content))
                    code_block_content = []
                    in_code_block = False
                else:
                    # 开始代码块
                    in_code_block = True
                i += 1
                continue
            
            if in_code_block:
                code_block_content.append(line)
                i += 1
                continue
            
            # 标题处理
            if line.startswith('# '):
                self._insert_text(line[2:], "heading1")
                self.text_widget.insert(tk.END, '\n\n')
            elif line.startswith('## '):
                self._insert_text(line[3:], "heading2")
                self.text_widget.insert(tk.END, '\n\n')
            elif line.startswith('### '):
                self._insert_text(line[4:], "heading3")
                self.text_widget.insert(tk.END, '\n\n')
            elif line.startswith('#### '):
                self._insert_text(line[5:], "heading4")
                self.text_widget.insert(tk.END, '\n\n')
            # 引用块
            elif line.startswith('> '):
                self._insert_text(line[2:], "blockquote")
                self.text_widget.insert(tk.END, '\n')
            # 无序列表
            elif line.startswith('- ') or line.startswith('* '):
                self._insert_text(f"•  {line[2:]}", "list_item")
                self.text_widget.insert(tk.END, '\n')
            # 有序列表
            elif re.match(r'^\d+\. ', line):
                content = re.sub(r'^\d+\. ', '', line)
                self._insert_text(f"•  {content}", "list_item")
                self.text_widget.insert(tk.END, '\n')
            # 空行
            elif line.strip() == '':
                self.text_widget.insert(tk.END, '\n')
            # 普通段落
            else:
                # 处理行内格式
                self._insert_inline_format(line)
                self.text_widget.insert(tk.END, '\n')
            
            i += 1
    
    def _insert_text(self, text: str, tag: str):
        """插入带标签的文本"""
        self.text_widget.insert(tk.END, text, tag)
    
    def _insert_code_block(self, code: str):
        """插入代码块"""
        self.text_widget.insert(tk.END, '\n')
        self.text_widget.insert(tk.END, code, "code_block")
        self.text_widget.insert(tk.END, '\n\n')
    
    def _insert_inline_format(self, text: str):
        """
        处理行内格式（粗体、斜体、行内代码）
        
        Args:
            text: 待处理的文本
        """
        # 简单的行内格式处理
        # 处理行内代码 `code`
        parts = re.split(r'(`[^`]+`|\*\*[^*]+\*\*|\*[^*]+\*|\[[^\]]+\]\([^)]+\))', text)
        
        for part in parts:
            if part.startswith('`') and part.endswith('`'):
                # 行内代码
                self.text_widget.insert(tk.END, part[1:-1], "code")
            elif part.startswith('**') and part.endswith('**'):
                # 粗体
                self.text_widget.insert(tk.END, part[2:-2], "bold")
            elif part.startswith('*') and part.endswith('*'):
                # 斜体
                self.text_widget.insert(tk.END, part[1:-1], "italic")
            elif part.startswith('[') and '](' in part:
                # 链接 [text](url)
                match = re.match(r'\[([^\]]+)\]\(([^)]+)\)', part)
                if match:
                    link_text, url = match.groups()
                    self.text_widget.insert(tk.END, link_text, "link")
            else:
                # 普通文本
                self.text_widget.insert(tk.END, part)


def create_markdown_frame(parent, theme: str = "light", font_size: str = "medium") -> Tuple[tk.Frame, MarkdownRenderer]:
    """
    创建 Markdown 显示框架
    
    Args:
        parent: 父组件
        theme: 主题名称
        font_size: 字体大小
    
    Returns:
        (frame, renderer) 元组
    """
    import tkinter.scrolledtext as scrolledtext
    
    frame = tk.Frame(parent)
    
    # 创建 Text 组件
    text_widget = scrolledtext.ScrolledText(
        frame,
        wrap=tk.WORD,
        font=("Consolas", 12),
        state=tk.DISABLED,
        padx=10,
        pady=10,
    )
    text_widget.pack(fill=tk.BOTH, expand=True)
    
    # 创建渲染器
    renderer = MarkdownRenderer(text_widget, theme, font_size)
    
    return frame, renderer
