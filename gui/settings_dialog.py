import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os

class SettingsDialog:
    def __init__(self, parent, config_manager, translator_manager):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("API Settings")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.config_manager = config_manager
        self.translator_manager = translator_manager
        
        self.create_widgets()
        
    def create_widgets(self):
        # API URL
        ttk.Label(self.dialog, text="API URL:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        self.url_entry = ttk.Entry(self.dialog, width=40)
        self.url_entry.grid(row=0, column=1, padx=10, pady=10)
        self.url_entry.insert(0, self.config_manager.api_url)
        
        # API Key
        ttk.Label(self.dialog, text="API Key:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        self.key_entry = ttk.Entry(self.dialog, width=40, show="*")
        self.key_entry.grid(row=1, column=1, padx=10, pady=10)
        self.key_entry.insert(0, self.config_manager.api_key)
        
        # Output directory
        ttk.Label(self.dialog, text="Output Directory:").grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        self.output_entry = ttk.Entry(self.dialog, width=40)
        self.output_entry.grid(row=2, column=1, padx=10, pady=10)
        self.output_entry.insert(0, self.config_manager.output_dir)
        
        # Browse button
        browse_btn = ttk.Button(
            self.dialog,
            text="Browse...",
            command=self.browse_output_dir,
            width=10
        )
        browse_btn.grid(row=2, column=2, padx=5, pady=10)
        
        # Show key checkbox
        self.show_key = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            self.dialog, text="Show API Key", 
            variable=self.show_key, command=self.toggle_show_key
        ).grid(row=3, column=1, padx=10, pady=5, sticky=tk.W)
        
        # Status labels
        self.create_status_labels()
        
        # Buttons
        self.create_buttons()
        
    def create_status_labels(self):
        # File processing status
        status_text = "Installed" if self.translator_manager.has_file_libs else "Not installed (attachment features unavailable)"
        status_color = "green" if self.translator_manager.has_file_libs else "red"
        ttk.Label(
            self.dialog, 
            text=f"File Processing Libraries: {status_text}", 
            foreground=status_color
        ).grid(row=4, column=0, columnspan=2, padx=10, pady=5, sticky=tk.W)
        
        # Translation status
        status_text = "Installed" if self.translator_manager.has_translation else "Not installed (translation features unavailable)"
        status_color = "green" if self.translator_manager.has_translation else "red"
        ttk.Label(
            self.dialog, 
            text=f"Translation Libraries: {status_text}", 
            foreground=status_color
        ).grid(row=5, column=0, columnspan=2, padx=10, pady=5, sticky=tk.W)
        
        # Required packages info
        ttk.Label(
            self.dialog, 
            text="Required Packages:", 
            font=('Segoe UI', 9, 'bold')
        ).grid(row=6, column=0, columnspan=2, padx=10, pady=(15,0), sticky=tk.W)
        
        ttk.Label(
            self.dialog, 
            text="For file processing: python-docx, PyPDF2"
        ).grid(row=7, column=0, columnspan=2, padx=10, pady=(0,0), sticky=tk.W)
        
        ttk.Label(
            self.dialog, 
            text="For translation: document_processor.py, translation_api.py"
        ).grid(row=8, column=0, columnspan=2, padx=10, pady=(0,5), sticky=tk.W)
        
    def create_buttons(self):
        btn_frame = ttk.Frame(self.dialog)
        btn_frame.grid(row=9, column=0, columnspan=2, pady=20)
        
        ttk.Button(
            btn_frame, text="Save", 
            command=self.save_settings
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(
            btn_frame, text="Cancel", 
            command=self.dialog.destroy
        ).pack(side=tk.LEFT, padx=10)
        
    def browse_output_dir(self):
        new_dir = filedialog.askdirectory(
            title="Select Output Location",
            initialdir=self.output_entry.get()
        )
        if new_dir:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, new_dir)
            
    def toggle_show_key(self):
        self.key_entry.config(show="" if self.show_key.get() else "*")
        
    def save_settings(self):
        try:
            # Update configuration
            self.config_manager.update_settings(
                api_url=self.url_entry.get().strip(),
                api_key=self.key_entry.get().strip(),
                output_dir=self.output_entry.get().strip()
            )
            
            messagebox.showinfo("Success", "API settings saved")
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error saving settings: {str(e)}") 