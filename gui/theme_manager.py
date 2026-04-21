"""
主题管理器

管理 GUI 主题（亮色/暗色/护眼）和字体大小设置
支持设置持久化
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any


# 主题配置
THEMES = {
    "light": {
        "name": "亮色主题",
        "bg": "#ffffff",
        "fg": "#24292e",
        "frame_bg": "#f6f8fa",
        "button_bg": "#f0f0f0",
        "header_bg": "#f6f8fa",
        "separator": "#e1e4e8",
        "accent": "#0366d6",
        "success": "#28a745",
        "warning": "#ff9800",
        "error": "#d73a49",
    },
    "dark": {
        "name": "暗色主题",
        "bg": "#1e1e1e",
        "fg": "#d4d4d4",
        "frame_bg": "#252526",
        "button_bg": "#3c3c3c",
        "header_bg": "#2d2d2d",
        "separator": "#404040",
        "accent": "#58a6ff",
        "success": "#4ec9b0",
        "warning": "#cca700",
        "error": "#f14c4c",
    },
    "eye_care": {
        "name": "护眼主题",
        "bg": "#c7edcc",
        "fg": "#2d3e3e",
        "frame_bg": "#b8d8be",
        "button_bg": "#a8c8ae",
        "header_bg": "#a8c8ae",
        "separator": "#8ab894",
        "accent": "#2e5c8a",
        "success": "#3a7d44",
        "warning": "#b8860b",
        "error": "#8b3a3a",
    },
}

# 字体大小配置
FONT_SIZES = {
    "small": {"name": "小", "base": 10},
    "medium": {"name": "中", "base": 12},
    "large": {"name": "大", "base": 14},
    "xlarge": {"name": "超大", "base": 16},
}

# 配置文件路径
CONFIG_DIR = Path(__file__).parent.parent / "config"
SETTINGS_FILE = CONFIG_DIR / "gui_settings.json"


class ThemeManager:
    """
    主题管理器
    
    管理 GUI 主题和字体大小设置
    """
    
    def __init__(self):
        """初始化主题管理器"""
        self._theme = "light"
        self._font_size = "medium"
        self._load_settings()
    
    def _load_settings(self):
        """从文件加载设置"""
        if SETTINGS_FILE.exists():
            try:
                with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self._theme = settings.get('theme', 'light')
                    self._font_size = settings.get('font_size', 'medium')
            except (json.JSONDecodeError, IOError) as e:
                print(f"加载设置失败：{e}")
                self._save_settings()
        else:
            # 创建默认设置
            self._save_settings()
    
    def _save_settings(self):
        """保存设置到文件"""
        try:
            # 确保目录存在
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            
            settings = {
                'theme': self._theme,
                'font_size': self._font_size,
            }
            
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"保存设置失败：{e}")
    
    @property
    def theme(self) -> str:
        """获取当前主题"""
        return self._theme
    
    @theme.setter
    def theme(self, value: str):
        """设置主题"""
        if value not in THEMES:
            raise ValueError(f"未知主题：{value}")
        self._theme = value
        self._save_settings()
    
    @property
    def font_size(self) -> str:
        """获取当前字体大小"""
        return self._font_size
    
    @font_size.setter
    def font_size(self, value: str):
        """设置字体大小"""
        if value not in FONT_SIZES:
            raise ValueError(f"未知字体大小：{value}")
        self._font_size = value
        self._save_settings()
    
    def get_theme_colors(self, theme_name: Optional[str] = None) -> Dict[str, str]:
        """
        获取主题颜色配置
        
        Args:
            theme_name: 主题名称，None 则使用当前主题
        
        Returns:
            颜色配置字典
        """
        name = theme_name if theme_name else self._theme
        return THEMES.get(name, THEMES["light"])
    
    def get_font_size_config(self, size_name: Optional[str] = None) -> Dict[str, Any]:
        """
        获取字体大小配置
        
        Args:
            size_name: 字体大小名称，None 则使用当前设置
        
        Returns:
            字体大小配置字典
        """
        name = size_name if size_name else self._font_size
        return FONT_SIZES.get(name, FONT_SIZES["medium"])
    
    def get_all_themes(self) -> Dict[str, str]:
        """
        获取所有主题
        
        Returns:
            {theme_id: theme_name} 字典
        """
        return {k: v["name"] for k, v in THEMES.items()}
    
    def get_all_font_sizes(self) -> Dict[str, str]:
        """
        获取所有字体大小
        
        Returns:
            {size_id: size_name} 字典
        """
        return {k: v["name"] for k, v in FONT_SIZES.items()}
    
    def apply_to_tk_style(self, style):
        """
        应用主题到 ttk.Style
        
        Args:
            style: ttk.Style 实例
        """
        colors = self.get_theme_colors()
        
        # 配置通用样式
        style.configure(".", 
            background=colors["bg"],
            foreground=colors["fg"],
            font=("Microsoft YaHei", self.get_font_size_config()["base"])
        )
        
        # 配置 TFrame
        style.configure("TFrame", 
            background=colors["frame_bg"]
        )
        
        # 配置 TLabel
        style.configure("TLabel",
            background=colors["frame_bg"],
            foreground=colors["fg"],
            font=("Microsoft YaHei", self.get_font_size_config()["base"])
        )
        
        # 配置 TButton
        style.configure("TButton",
            background=colors["button_bg"],
            foreground=colors["fg"],
            font=("Microsoft YaHei", self.get_font_size_config()["base"])
        )
        
        # 配置 TEntry
        style.configure("TEntry",
            fieldbackground=colors["bg"],
            foreground=colors["fg"],
            font=("Microsoft YaHei", self.get_font_size_config()["base"])
        )
        
        # 配置 TCombobox
        style.configure("TCombobox",
            fieldbackground=colors["bg"],
            foreground=colors["fg"],
            arrowcolor=colors["fg"],
            font=("Microsoft YaHei", self.get_font_size_config()["base"])
        )
        
        # 配置 TNotebook
        style.configure("TNotebook",
            background=colors["frame_bg"],
            bordercolor=colors["separator"],
        )
        
        style.configure("TNotebook.Tab",
            background=colors["button_bg"],
            foreground=colors["fg"],
            font=("Microsoft YaHei", self.get_font_size_config()["base"]),
            padding=[10, 5]
        )
        
        style.map("TNotebook.Tab",
            background=[("selected", colors["bg"])],
            foreground=[("selected", colors["accent"])],
        )
        
        # 配置 Treeview
        style.configure("Treeview",
            background=colors["bg"],
            foreground=colors["fg"],
            fieldbackground=colors["bg"],
            font=("Microsoft YaHei", self.get_font_size_config()["base"]),
            rowheight=25
        )
        
        style.configure("Treeview.Heading",
            background=colors["button_bg"],
            foreground=colors["fg"],
            font=("Microsoft YaHei", self.get_font_size_config()["base"], "bold")
        )
        
        style.map("Treeview",
            background=[("selected", colors["accent"])],
            foreground=[("selected", colors["bg"])],
        )
        
        # 配置 Progressbar
        style.configure("Horizontal.TProgressbar",
            background=colors["accent"],
            troughcolor=colors["button_bg"],
            bordercolor=colors["separator"],
        )
        
        # 配置 Scrollbar
        style.configure("Vertical.TScrollbar",
            background=colors["button_bg"],
            troughcolor=colors["bg"],
            bordercolor=colors["separator"],
        )
        
        style.configure("Horizontal.TScrollbar",
            background=colors["button_bg"],
            troughcolor=colors["bg"],
            bordercolor=colors["separator"],
        )


# 全局主题管理器实例
_theme_manager: Optional[ThemeManager] = None


def get_theme_manager() -> ThemeManager:
    """获取全局主题管理器实例"""
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager
