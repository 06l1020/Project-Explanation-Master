"""
模型配置管理器测试

测试ModelConfigManager和ModelConfig类的功能
"""

import unittest
import tempfile
import json
from pathlib import Path
from core.model_config_manager import ModelConfigManager, ModelConfig


class TestModelConfig(unittest.TestCase):
    """测试ModelConfig类"""
    
    def test_create_config(self):
        """测试创建配置"""
        config = ModelConfig(
            name="Test Config",
            api_key="sk-test",
            base_url="http://test.com",
            model_name="gpt-4"
        )
        
        self.assertEqual(config.name, "Test Config")
        self.assertEqual(config.api_key, "sk-test")
        self.assertEqual(config.base_url, "http://test.com")
        self.assertEqual(config.model_name, "gpt-4")
        self.assertIsNotNone(config.created_at)
        self.assertEqual(config.use_count, 0)
    
    def test_to_dict(self):
        """测试转换为字典"""
        config = ModelConfig(
            name="Test",
            api_key="sk-test",
            base_url="",
            model_name="gpt-3.5-turbo"
        )
        
        data = config.to_dict()
        
        self.assertEqual(data['name'], "Test")
        self.assertEqual(data['api_key'], "sk-test")
        self.assertEqual(data['base_url'], "")
        self.assertEqual(data['model_name'], "gpt-3.5-turbo")
    
    def test_from_dict(self):
        """测试从字典创建"""
        data = {
            'name': 'Test Config',
            'api_key': 'sk-test',
            'base_url': 'http://test.com',
            'model_name': 'gpt-4',
            'created_at': '2024-01-01T12:00:00',
            'last_used': '2024-01-02T12:00:00',
            'use_count': 5
        }
        
        config = ModelConfig.from_dict(data)
        
        self.assertEqual(config.name, "Test Config")
        self.assertEqual(config.api_key, "sk-test")
        self.assertEqual(config.use_count, 5)


class TestModelConfigManager(unittest.TestCase):
    """测试ModelConfigManager类"""
    
    def setUp(self):
        """创建临时目录用于测试"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / "test_configs.json"
        self.manager = ModelConfigManager(config_file=str(self.config_file))
    
    def test_add_config(self):
        """测试添加配置"""
        config = self.manager.add_config(
            name="Test Config",
            api_key="sk-test",
            model_name="gpt-4"
        )
        
        self.assertEqual(config.name, "Test Config")
        self.assertEqual(len(self.manager.configs), 1)
    
    def test_add_duplicate_config(self):
        """测试添加重复配置（应更新）"""
        self.manager.add_config(
            name="Test",
            api_key="sk-1",
            model_name="gpt-4"
        )
        
        self.manager.add_config(
            name="Test",
            api_key="sk-2",
            model_name="gpt-3.5-turbo"
        )
        
        self.assertEqual(len(self.manager.configs), 1)
        self.assertEqual(self.manager.configs[0].api_key, "sk-2")
    
    def test_remove_config(self):
        """测试删除配置"""
        self.manager.add_config("Config1", "sk-1", model_name="gpt-4")
        self.manager.add_config("Config2", "sk-2", model_name="gpt-3.5")
        
        success = self.manager.remove_config("Config1")
        
        self.assertTrue(success)
        self.assertEqual(len(self.manager.configs), 1)
        self.assertEqual(self.manager.configs[0].name, "Config2")
    
    def test_get_config(self):
        """测试获取配置"""
        self.manager.add_config("Test", "sk-test", model_name="gpt-4")
        
        config = self.manager.get_config("Test")
        
        self.assertIsNotNone(config)
        self.assertEqual(config.api_key, "sk-test")
    
    def test_get_nonexistent_config(self):
        """测试获取不存在的配置"""
        config = self.manager.get_config("Nonexistent")
        
        self.assertIsNone(config)
    
    def test_set_default_config(self):
        """测试设置默认配置"""
        self.manager.add_config("Config1", "sk-1", model_name="gpt-4")
        self.manager.add_config("Config2", "sk-2", model_name="gpt-3.5")
        
        success = self.manager.set_default_config("Config2")
        
        self.assertTrue(success)
        self.assertEqual(self.manager.default_config_index, 1)
    
    def test_get_default_config(self):
        """测试获取默认配置"""
        self.manager.add_config("Config1", "sk-1", model_name="gpt-4")
        self.manager.add_config("Config2", "sk-2", model_name="gpt-3.5")
        self.manager.set_default_config("Config2")
        
        default = self.manager.get_default_config()
        
        self.assertIsNotNone(default)
        self.assertEqual(default.name, "Config2")
    
    def test_record_usage(self):
        """测试记录使用"""
        self.manager.add_config("Test", "sk-test", model_name="gpt-4")
        
        self.manager.record_usage("Test")
        self.manager.record_usage("Test")
        
        config = self.manager.get_config("Test")
        
        self.assertEqual(config.use_count, 2)
        self.assertIsNotNone(config.last_used)
    
    def test_get_all_configs(self):
        """测试获取所有配置"""
        self.manager.add_config("Config1", "sk-1", model_name="gpt-4")
        self.manager.add_config("Config2", "sk-2", model_name="gpt-3.5")
        
        configs = self.manager.get_all_configs()
        
        self.assertEqual(len(configs), 2)
        self.assertIsInstance(configs[0], dict)
    
    def test_get_config_names(self):
        """测试获取配置名称"""
        self.manager.add_config("Config1", "sk-1", model_name="gpt-4")
        self.manager.add_config("Config2", "sk-2", model_name="gpt-3.5")
        
        names = self.manager.get_config_names()
        
        self.assertEqual(len(names), 2)
        self.assertIn("Config1", names)
        self.assertIn("Config2", names)
    
    def test_get_frequently_used(self):
        """测试获取常用配置"""
        self.manager.add_config("Config1", "sk-1", model_name="gpt-4")
        self.manager.add_config("Config2", "sk-2", model_name="gpt-3.5")
        self.manager.add_config("Config3", "sk-3", model_name="gpt-4-turbo")
        
        self.manager.record_usage("Config1")
        self.manager.record_usage("Config1")
        self.manager.record_usage("Config1")
        self.manager.record_usage("Config2")
        
        frequent = self.manager.get_frequently_used(limit=2)
        
        self.assertEqual(len(frequent), 2)
        self.assertEqual(frequent[0]['name'], "Config1")
        self.assertEqual(frequent[1]['name'], "Config2")
    
    def test_save_and_load(self):
        """测试保存和加载"""
        # 添加配置
        self.manager.add_config("Config1", "sk-1", model_name="gpt-4")
        self.manager.add_config("Config2", "sk-2", model_name="gpt-3.5")
        self.manager.set_default_config("Config2")
        
        # 创建新管理器加载数据
        new_manager = ModelConfigManager(config_file=str(self.config_file))
        
        self.assertEqual(len(new_manager.configs), 2)
        self.assertEqual(new_manager.default_config_index, 1)
        self.assertEqual(new_manager.configs[0].name, "Config1")
    
    def test_auto_create_defaults(self):
        """测试自动创建默认配置"""
        # 创建新管理器（配置文件不存在）
        new_config_file = Path(self.temp_dir) / "new_configs.json"
        manager = ModelConfigManager(config_file=str(new_config_file))
        
        # 应该自动创建3个默认配置
        self.assertGreaterEqual(len(manager.configs), 3)
        self.assertEqual(manager.default_config_index, 0)
    
    def test_empty_manager(self):
        """测试空管理器"""
        self.assertEqual(len(self.manager.configs), 0)
        self.assertEqual(self.manager.default_config_index, -1)
        
        default = self.manager.get_default_config()
        self.assertIsNone(default)


if __name__ == '__main__':
    unittest.main()
