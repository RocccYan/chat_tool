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


class WelcomeMessageManager:
    def __init__(self, config_file: str = "config/welcome_messages.ini"):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self._load_config()

    def _load_config(self):
        """Load welcome messages from configuration file"""
        if os.path.exists(self.config_file):
            self.config.read(self.config_file, encoding='utf-8')
        else:
            # Create default configuration if file doesn't exist
            self._create_default_config()

    def _create_default_config(self):
        """Create default configuration file"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        
        self.config['normal'] = {
            'title': '欢迎使用大模型问答平台',
            'message': '我是您的AI助手，具备广泛的知识基础，可以帮助您解答各种问题、提供信息查询、协助分析问题等。无论是学术研究、工作事务还是日常疑问，我都会尽力为您提供准确、有用的回答。请随时提出您的问题！'
        }
        
        self.config['search'] = {
            'title': '欢迎使用大模型问答平台',
            'message': '我可以协助你找到权威的信息来源，并提供相应链接帮助你更便捷地获取相关信息。我会通过搜索功能获取最新的实时数据，确保为您提供准确、及时的信息。如果你准备好了就开始对话，我将和你一起完成任务！'
        }
        
        self.config['nosystem'] = {
            'title': '欢迎使用大模型问答平台',
            'message': '这是一个自由对话模式，没有特定的系统提示约束。我将以最自然的方式与您交流，您可以畅所欲言，探讨任何感兴趣的话题。让我们开始一场轻松愉快的对话吧！'
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            self.config.write(f)

    def get_welcome_title(self, mode: str = "normal") -> str:
        """Get welcome title by mode"""
        if mode in self.config:
            return self.config[mode].get('title', '欢迎使用大模型问答平台')
        return self.config['normal'].get('title', '欢迎使用大模型问答平台')

    def get_welcome_message(self, mode: str = "normal") -> str:
        """Get welcome message by mode"""
        if mode in self.config:
            return self.config[mode].get('message', '')
        return self.config['normal'].get('message', '')

    def set_welcome_message(self, mode: str, title: str, message: str):
        """Set welcome message for a mode"""
        self.config[mode] = {
            'title': title,
            'message': message
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            self.config.write(f)


class ImplicitPromptManager:
    def __init__(self, config_file: str = "config/implicit_prompts.ini"):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self._load_config()

    def _load_config(self):
        """Load implicit prompts from configuration file"""
        if os.path.exists(self.config_file):
            self.config.read(self.config_file, encoding='utf-8')
        else:
            # Create default configuration if file doesn't exist
            self._create_default_config()

    def _create_default_config(self):
        """Create default configuration file"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        
        self.config['default'] = {
            'name': '默认隐式提示',
            'implicit_prompt': '请以专业、准确和有用的方式回答问题。'
        }
        
        self.config['normal'] = {
            'name': '标准对话隐式提示',
            'implicit_prompt': '请提供清晰、准确的回答，如果不确定请说明。'
        }
        
        self.config['search'] = {
            'name': '搜索模式隐式提示',
            'implicit_prompt': '请基于搜索到的最新信息提供准确回答，并在可能的情况下提供相关链接。'
        }
        
        self.config['nosystem'] = {
            'name': '自由对话隐式提示',
            'implicit_prompt': '请自然地回答用户问题，保持对话的连贯性。'
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            self.config.write(f)

    def get_implicit_prompt(self, mode: str = "default") -> str:
        """Get implicit prompt by mode"""
        if mode in self.config:
            return self.config[mode].get('implicit_prompt', '')
        return self.config['default'].get('implicit_prompt', '')

    def get_prompt_name(self, mode: str = "default") -> str:
        """Get implicit prompt name by mode"""
        if mode in self.config:
            return self.config[mode].get('name', mode)
        return self.config['default'].get('name', 'Default')

    def set_implicit_prompt(self, mode: str, name: str, implicit_prompt: str):
        """Set implicit prompt for a mode"""
        self.config[mode] = {
            'name': name,
            'implicit_prompt': implicit_prompt
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            self.config.write(f)
