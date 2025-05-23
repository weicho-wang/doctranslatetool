import tkinter as tk
import os
import traceback
from gui import DeepSeekChatGUI, ConfigManager, TranslatorManager
from gui.logger import setup_logger

def main():
    # Setup logging system
    logger = setup_logger()
    logger.info("Starting DeepSeek Chat application")
    
    try:
        # Create root window
        root = tk.Tk()
        root.title("DeepSeek Chat")
        
        # Set application icon
        icon_path = "icon.ico"
        if os.path.exists(icon_path):
            try:
                root.iconbitmap(icon_path)
                logger.info(f"Loaded icon from: {icon_path}")
            except Exception as e:
                logger.error(f"Could not load icon: {e}")
        else:
            logger.warning(f"Icon not found at: {icon_path}")
        
        # Create configuration and translation managers
        logger.info("Initializing config manager")
        config_manager = ConfigManager()
        
        logger.info("Initializing translator manager")
        translator_manager = TranslatorManager()
        
        # Create main application
        logger.info("Creating main application")
        app = DeepSeekChatGUI(root, config_manager, translator_manager)
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        
        # Show initial message
        features_available = []
        if translator_manager.has_file_libs:
            features_available.append("File Attachments")
        if translator_manager.has_translation:
            features_available.append("Document Translation")
            
        if features_available:
            logger.info(f"Available features: {', '.join(features_available)}")
            app.display_message("system", f"Available features: {', '.join(features_available)}")
        else:
            logger.warning("No additional features available")
            app.display_message("system", "Basic chat mode active. Install additional libraries for more features.")
        
        # Start application
        logger.info("Starting main event loop")
        root.mainloop()
        
    except Exception as e:
        logger.critical(f"Application crashed: {e}")
        logger.critical(traceback.format_exc())
        raise

if __name__ == "__main__":
    main() 