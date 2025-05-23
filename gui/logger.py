import os
import sys
import logging
import datetime
from pathlib import Path

# 配置日志系统
def setup_logger():
    """设置应用程序日志系统"""
    # 确定日志存储位置
    if hasattr(sys, '_MEIPASS'):
        # 打包环境 - 使用用户目录
        log_dir = os.path.join(os.path.expanduser("~"), "DeepSeekChat", "logs")
    else:
        # 开发环境 - 使用当前目录
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
    
    # 确保日志目录存在
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    # 创建日志文件名，包含日期时间戳
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"deepseek_chat_{timestamp}.log")
    
    # 配置日志格式
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()  # 同时输出到控制台
        ]
    )
    
    # 创建并返回主日志器
    logger = logging.getLogger("DeepSeekChat")
    logger.info(f"Application started, logging to {log_file}")
    
    # 记录系统信息
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Platform: {sys.platform}")
    
    return logger

# 获取应用程序日志器
def get_logger():
    """获取或创建应用程序日志器"""
    logger = logging.getLogger("DeepSeekChat")
    if not logger.handlers:  # 如果日志器没有配置，重新设置
        return setup_logger()
    return logger 