import json
import os
import sys

def get_resource_path(relative_path):
    """获取资源文件的绝对路径，适用于开发环境和PyInstaller打包后的环境"""
    try:
        # PyInstaller创建临时文件夹，将路径存储在_MEIPASS中
        base_path = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
        return os.path.join(base_path, relative_path)
    except Exception as e:
        print(f"Error getting resource path: {e}")
        return os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), relative_path)

class ConfigManager:
    def __init__(self):
        self.config_path = get_resource_path('api_config.json')
        self.config = self.load_config()
        
    def load_config(self):
        """Load configuration from file"""
        try:
            with open(self.config_path) as f:
                return json.load(f)
        except Exception as e:
            print(f"Failed to load config: {e}")
            # Try to read API key from API directory
            api_key = ""
            api_key_path = get_resource_path(os.path.join("API", "API_Key.txt"))
            if os.path.exists(api_key_path):
                try:
                    with open(api_key_path, 'r') as f:
                        api_key = f.read().strip()
                except Exception as e:
                    print(f"Failed to read API key: {e}")
            
            config = {
                "api_url": "https://api.deepseek.com/v1/chat/completions",
                "api_key": api_key,
                "model": "deepseek-chat",
                "output_dir": self.get_default_output_dir()
            }
            
            # Save config to file
            try:
                self.save_config(config)
            except Exception as e:
                print(f"Failed to save config: {e}")
            return config
            
    def save_config(self, config=None):
        """Save configuration to file"""
        if config is None:
            config = self.config
        
        try:    
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Failed to save config: {e}")
            # 若无法写入打包后的路径，则尝试写入用户目录
            user_config = os.path.expanduser("~/deepseek_config.json")
            with open(user_config, 'w') as f:
                json.dump(config, f, indent=4)
            print(f"Config saved to {user_config} instead")
            
    def update_settings(self, **kwargs):
        """Update configuration settings"""
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value
                
        self.save_config()
        
    def get_default_output_dir(self):
        """Get default output directory"""
        # Try user's Documents folder
        documents_dir = os.path.expanduser("~\\Documents")
        if os.path.isdir(documents_dir):
            return documents_dir
            
        # Fallback to current directory
        return os.getcwd()
        
    @property
    def api_url(self):
        return self.config.get("api_url", "")
        
    @property
    def api_key(self):
        return self.config.get("api_key", "")
        
    @property
    def model(self):
        return self.config.get("model", "deepseek-chat")
        
    @property
    def output_dir(self):
        return self.config.get("output_dir", self.get_default_output_dir()) 