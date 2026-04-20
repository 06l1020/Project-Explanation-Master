"""
模型配置管理器

负责管理多个LLM模型配置的本地存储和读取
支持配置的保存、加载、删除和切换
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


class ModelConfig:
    """单个模型配置"""
    
    def __init__(
        self,
        name: str,
        api_key: str,
        base_url: str = "",
        model_name: str = "gpt-4",
        created_at: Optional[str] = None,
        last_used: Optional[str] = None,
        use_count: int = 0
    ):
        """
        初始化模型配置
        
        Args:
            name: 配置名称（用户自定义）
            api_key: API密钥
            base_url: API基础URL
            model_name: 模型名称
            created_at: 创建时间
            last_used: 最后使用时间
            use_count: 使用次数
        """
        self.name = name
        self.api_key = api_key
        self.base_url = base_url
        self.model_name = model_name
        self.created_at = created_at or datetime.now().isoformat()
        self.last_used = last_used
        self.use_count = use_count
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'name': self.name,
            'api_key': self.api_key,
            'base_url': self.base_url,
            'model_name': self.model_name,
            'created_at': self.created_at,
            'last_used': self.last_used,
            'use_count': self.use_count
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'ModelConfig':
        """从字典创建配置"""
        return ModelConfig(
            name=data['name'],
            api_key=data['api_key'],
            base_url=data.get('base_url', ''),
            model_name=data.get('model_name', 'gpt-4'),
            created_at=data.get('created_at'),
            last_used=data.get('last_used'),
            use_count=data.get('use_count', 0)
        )


class ModelConfigManager:
    """
    模型配置管理器
    
    功能：
    1. 加载和保存配置到本地JSON文件
    2. 添加、删除、更新配置
    3. 记录配置使用统计
    4. 提供常用配置列表
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_file: 配置文件路径（可选，默认使用config/model_configs.json）
        """
        if config_file is None:
            # 默认使用项目根目录下的config/model_configs.json
            current_dir = Path(__file__).parent.parent
            config_file = current_dir / "config" / "model_configs.json"
        
        self.config_file = Path(config_file)
        self.configs: List[ModelConfig] = []
        self.default_config_index: int = -1
        
        # 加载现有配置
        self._load_configs()
    
    def add_config(
        self,
        name: str,
        api_key: str,
        base_url: str = "",
        model_name: str = "gpt-4",
        set_as_default: bool = False
    ) -> ModelConfig:
        """
        添加新配置
        
        Args:
            name: 配置名称
            api_key: API密钥
            base_url: API基础URL
            model_name: 模型名称
            set_as_default: 是否设为默认配置
            
        Returns:
            创建的ModelConfig对象
        """
        # 检查是否已存在同名配置
        for i, config in enumerate(self.configs):
            if config.name == name:
                # 更新现有配置
                config.api_key = api_key
                config.base_url = base_url
                config.model_name = model_name
                if set_as_default:
                    self.default_config_index = i
                self._save_configs()
                return config
        
        # 创建新配置
        new_config = ModelConfig(
            name=name,
            api_key=api_key,
            base_url=base_url,
            model_name=model_name
        )
        
        self.configs.append(new_config)
        
        if set_as_default or len(self.configs) == 1:
            self.default_config_index = len(self.configs) - 1
        
        self._save_configs()
        return new_config
    
    def remove_config(self, name: str) -> bool:
        """
        删除配置
        
        Args:
            name: 配置名称
            
        Returns:
            是否成功删除
        """
        for i, config in enumerate(self.configs):
            if config.name == name:
                self.configs.pop(i)
                
                # 调整默认配置索引
                if self.default_config_index == i:
                    self.default_config_index = 0 if len(self.configs) > 0 else -1
                elif self.default_config_index > i:
                    self.default_config_index -= 1
                
                self._save_configs()
                return True
        
        return False
    
    def get_config(self, name: str) -> Optional[ModelConfig]:
        """
        获取指定配置
        
        Args:
            name: 配置名称
            
        Returns:
            ModelConfig对象或None
        """
        for config in self.configs:
            if config.name == name:
                return config
        return None
    
    def get_default_config(self) -> Optional[ModelConfig]:
        """
        获取默认配置
        
        Returns:
            默认ModelConfig对象或None
        """
        if 0 <= self.default_config_index < len(self.configs):
            return self.configs[self.default_config_index]
        return None
    
    def set_default_config(self, name: str) -> bool:
        """
        设置默认配置
        
        Args:
            name: 配置名称
            
        Returns:
            是否成功设置
        """
        for i, config in enumerate(self.configs):
            if config.name == name:
                self.default_config_index = i
                self._save_configs()
                return True
        return False
    
    def record_usage(self, name: str):
        """
        记录配置使用
        
        Args:
            name: 配置名称
        """
        for config in self.configs:
            if config.name == name:
                config.use_count += 1
                config.last_used = datetime.now().isoformat()
                self._save_configs()
                break
    
    def get_all_configs(self) -> List[Dict]:
        """
        获取所有配置（字典列表）
        
        Returns:
            配置字典列表
        """
        return [config.to_dict() for config in self.configs]
    
    def get_config_names(self) -> List[str]:
        """
        获取所有配置名称
        
        Returns:
            配置名称列表
        """
        return [config.name for config in self.configs]
    
    def get_frequently_used(self, limit: int = 5) -> List[Dict]:
        """
        获取最常用的配置
        
        Args:
            limit: 返回数量限制
            
        Returns:
            最常用的配置列表
        """
        sorted_configs = sorted(self.configs, key=lambda x: x.use_count, reverse=True)
        return [config.to_dict() for config in sorted_configs[:limit]]
    
    def _load_configs(self):
        """从文件加载配置"""
        if not self.config_file.exists():
            # 创建默认配置
            self._create_default_configs()
            return
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 加载配置列表
            configs_data = data.get('configs', [])
            self.configs = [ModelConfig.from_dict(c) for c in configs_data]
            
            # 加载默认配置索引
            self.default_config_index = data.get('default_config_index', -1)
            
        except Exception as e:
            print(f"⚠️ 加载模型配置失败: {e}")
            self.configs = []
            self.default_config_index = -1
            # 创建默认配置
            self._create_default_configs()
    
    def _save_configs(self):
        """保存配置到文件"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                'configs': [config.to_dict() for config in self.configs],
                'default_config_index': self.default_config_index,
                'version': '1.0',
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"⚠️ 保存模型配置失败: {e}")
    
    def _create_default_configs(self):
        """创建默认配置"""
        # 添加一些常用的默认配置
        default_configs = [
            ModelConfig(
                name="OpenAI GPT-4",
                api_key="",  # 用户需要自己填写
                base_url="",
                model_name="gpt-4"
            ),
            ModelConfig(
                name="OpenAI GPT-3.5",
                api_key="",
                base_url="",
                model_name="gpt-3.5-turbo"
            ),
            ModelConfig(
                name="Ollama Local",
                api_key="ollama",
                base_url="http://localhost:11434/v1",
                model_name="llama2"
            )
        ]
        
        self.configs = default_configs
        self.default_config_index = 0
        self._save_configs()


# 全局配置管理器实例（单例模式）
_config_manager_instance: Optional[ModelConfigManager] = None


def get_config_manager() -> ModelConfigManager:
    """
    获取全局配置管理器实例
    
    Returns:
        ModelConfigManager实例
    """
    global _config_manager_instance
    if _config_manager_instance is None:
        _config_manager_instance = ModelConfigManager()
    return _config_manager_instance
