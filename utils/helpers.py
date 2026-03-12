"""
工具辅助模块
提供配置加载、环境切换等通用功能
"""
import os
import yaml
from typing import Dict, Any


class ConfigLoader:
    """
    配置文件加载器
    用于加载和管理 YAML 配置文件
    """

    def __init__(self, config_path: str = None):
        """
        初始化配置加载器

        Args:
            config_path: 配置文件路径，默认为项目根目录下的 config/config.yaml
        """
        if config_path is None:
            # 获取项目根目录
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(project_root, "config", "config.yaml")
        
        self.config_path = config_path
        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """
        加载 YAML 配置文件

        Returns:
            配置字典
        """
        with open(self.config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def get_env_config(self, env: str = None) -> Dict[str, Any]:
        """
        获取指定环境的配置

        Args:
            env: 环境名称，如 dev、test、prod，默认为配置文件中的 default 环境

        Returns:
            环境配置字典
        """
        if env is None:
            env = self._config["env"]["default"]
        
        return self._config["env"][env]

    def get_browser_config(self) -> Dict[str, Any]:
        """
        获取浏览器配置

        Returns:
            浏览器配置字典
        """
        return self._config["browser"]

    def get_test_config(self) -> Dict[str, Any]:
        """
        获取测试配置

        Returns:
            测试配置字典
        """
        return self._config["test"]

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值，支持点号分隔的嵌套键

        Args:
            key: 配置键，如 "env.dev.base_url"
            default: 默认值

        Returns:
            配置值
        """
        keys = key.split(".")
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value


# 全局配置实例
config_loader = ConfigLoader()
