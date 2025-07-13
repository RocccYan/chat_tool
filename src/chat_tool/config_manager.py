import configparser
import os
from typing import Dict, Optional

class SystemPromptManager:
    def __init__(self, config_file: str = "config/system_prompts.ini"):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self._load_config()

    def _load_config(self):
        """Load system prompts from configuration file"""
        if os.path.exists(self.config_file):
            self.config.read(self.config_file, encoding='utf-8')
        else:
            # Create default configuration if file doesn't exist
            self._create_default_config()

    def _create_default_config(self):
        """Create default configuration file"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        
        self.config['default'] = {
            'name': '通用聊天助手',
            'system_prompt': '你是一个有用的AI助手。请友善、准确地回答用户的问题。'
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            self.config.write(f)

    def get_system_prompt(self, prompt_type: str = "default") -> str:
        """Get system prompt by type"""
        if prompt_type in self.config:
            return self.config[prompt_type].get('system_prompt', '')
        return self.config['default'].get('system_prompt', '')

    def get_prompt_name(self, prompt_type: str = "default") -> str:
        """Get prompt name by type"""
        if prompt_type in self.config:
            return self.config[prompt_type].get('name', prompt_type)
        return self.config['default'].get('name', 'Default')

    def list_available_prompts(self) -> Dict[str, str]:
        """List all available prompt types with their names"""
        prompts = {}
        for section in self.config.sections():
            prompts[section] = self.config[section].get('name', section)
        return prompts

    def add_system_prompt(self, prompt_type: str, name: str, system_prompt: str):
        """Add a new system prompt"""
        self.config[prompt_type] = {
            'name': name,
            'system_prompt': system_prompt
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            self.config.write(f)
