import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox, filedialog
import threading
import queue
import json
import os
from .settings_dialog import SettingsDialog
from .translation_dialog import TranslationDialog

class DeepSeekChatGUI:
    def __init__(self, root, config_manager, translator_manager):
        # Initialize window
        self.root = root
        self.root.title("DeepSeek Chat")
        self.root.geometry("800x600")
        
        # Store managers
        self.config_manager = config_manager
        self.translator_manager = translator_manager
        
        # Attachment related variables
        self.attachment = None
        self.attachment_type = None
        self.attachment_name = None
        self.attachment_path = None
        
        # Translation variables
        self.translation_in_progress = False
        self.translation_mode = False
        self.source_lang = "zh"
        self.target_lang = "en"
        self.preserve_format = True
        self.percent_to_translate = 100
        
        # Default translation settings
        self.api_option = "deepseek-chat"
        self.translate_percent = 10
        
        # Default output format settings
        self.output_pdf = False
        self.direct_pdf = True
        
        # Create UI components
        self.create_widgets()
        
        # Message queue and background thread
        self.message_queue = queue.Queue()
        self.running = True
        self.is_sending = False
        self.check_queue()

    def create_widgets(self):
        """Build the UI layout"""
        # Create main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        self._create_top_frame(main_frame)
        self._create_chat_frame(main_frame)
        self._create_input_frame(main_frame)
        self._create_status_bar()
        
        # Configure styles
        self.apply_styles()

    def _create_top_frame(self, parent):
        # Create top frame
        top_frame = ttk.Frame(parent)
        top_frame.pack(fill='x', pady=(0, 10))
        
        # Add model selection dropdown
        ttk.Label(top_frame, text="Model:").pack(side=tk.LEFT, padx=(0, 5))
        self.model_var = tk.StringVar(value="deepseek-chat")
        model_combo = ttk.Combobox(
            top_frame, 
            textvariable=self.model_var,
            values=["deepseek-chat", "deepseek-reasoner"],
            state="readonly",
            width=20
        )
        model_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        # Add mode selection (chat/translation)
        if self.translator_manager.has_translation:
            self._create_translation_controls(top_frame)
        
        # Add settings button
        settings_btn = ttk.Button(
            top_frame,
            text="API Settings",
            command=self.show_settings
        )
        settings_btn.pack(side=tk.RIGHT)

    def _create_translation_controls(self, parent):
        """Create translation mode control components"""
        # Create mode switching frame
        mode_frame = ttk.Frame(parent)
        mode_frame.pack(side=tk.LEFT, padx=10)
        
        # Create mode switching radio buttons
        self.mode_var = tk.StringVar(value="chat")
        ttk.Radiobutton(
            mode_frame,
            text="Chat",
            variable=self.mode_var,
            value="chat",
            command=self.toggle_translation_mode
        ).pack(side=tk.LEFT)
        
        ttk.Radiobutton(
            mode_frame,
            text="Translation",
            variable=self.mode_var,
            value="translation",
            command=self.toggle_translation_mode
        ).pack(side=tk.LEFT)
        
        # Create translation settings button
        self.translation_settings_btn = ttk.Button(
            parent,
            text="Translation Settings",
            command=self.show_translation_settings
        )
        self.translation_settings_btn.pack(side=tk.LEFT)
        self.translation_settings_btn.config(state=tk.DISABLED)  # Disabled by default

    def toggle_translation_mode(self):
        """Toggle translation mode"""
        is_translation = self.mode_var.get() == "translation"
        self.translation_mode = is_translation
        
        # Enable or disable translation settings button
        self.translation_settings_btn.config(
            state=tk.NORMAL if is_translation else tk.DISABLED
        )
        
        # Update UI hint
        mode_text = "Translation Mode" if is_translation else "Chat Mode"
        self.status_var.set(f"Switched to {mode_text}")
        
        # If entering translation mode, show hint
        if is_translation:
            self.display_message("system", "Translation mode activated. Upload a document to translate or type text directly.")

    def _create_chat_frame(self, parent):
        # Create chat area
        chat_frame = ttk.Frame(parent)
        chat_frame.pack(expand=True, fill='both', pady=(0, 10))
        
        # Chat history display area
        self.chat_area = scrolledtext.ScrolledText(
            chat_frame, wrap=tk.WORD, state='disabled',
            font=('Segoe UI', 10)
        )
        self.chat_area.pack(expand=True, fill='both')

    def _create_input_frame(self, parent):
        # Bottom input area
        input_frame = ttk.Frame(parent)
        input_frame.pack(fill='x')
        
        # Attachment indicator frame
        self.attachment_frame = ttk.Frame(input_frame)
        self.attachment_frame.pack(fill='x', pady=(0, 5))
        
        # Attachment label (hidden by default)
        self.attachment_var = tk.StringVar(value="")
        self.attachment_label = ttk.Label(
            self.attachment_frame, 
            textvariable=self.attachment_var,
            foreground="#0078D4",
            font=('Segoe UI', 9, 'italic')
        )
        
        # Text input area
        self.input_area = scrolledtext.ScrolledText(
            input_frame, wrap=tk.WORD, height=4,
            font=('Segoe UI', 10)
        )
        self.input_area.pack(side=tk.LEFT, expand=True, fill='both', padx=(0, 10))
        self.input_area.bind("<Control-Return>", lambda e: self.send_message())
        
        self._create_button_frame(input_frame)

    def _create_button_frame(self, parent):
        # Button frame
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(side=tk.RIGHT, fill='y')
        
        # Progress bar
        self.progress = ttk.Progressbar(
            btn_frame, orient='horizontal', length=100, mode='indeterminate'
        )
        self.progress.pack(side=tk.TOP, fill='x', pady=(0, 5))
        self.progress.pack_forget()  # Hidden by default
        
        # Add buttons
        self._create_action_buttons(btn_frame)

    def _create_action_buttons(self, parent):
        # Upload button
        self.upload_btn = ttk.Button(
            parent,
            text="Upload File",
            command=self.upload_attachment
        )
        self.upload_btn.pack(side=tk.TOP, fill='x', pady=(0, 5))
        
        # Output location button
        self.output_location_var = tk.StringVar(value=f"Output Dir: {os.path.basename(self.config_manager.output_dir)}")
        self.output_location_btn = ttk.Button(
            parent,
            text="Output Location",
            command=self.select_output_location
        )
        self.output_location_btn.pack(side=tk.TOP, fill='x', pady=(0, 5))
        
        # Send button
        self.send_btn = ttk.Button(
            parent, 
            text="Send",
            command=self.send_message
        )
        self.send_btn.pack(side=tk.BOTTOM, fill='both', expand=True)

    def _create_status_bar(self):
        # Add bottom status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(
            self.root, textvariable=self.status_var, 
            relief=tk.SUNKEN, anchor=tk.W
        )
        status_bar.pack(side=tk.BOTTOM, fill='x')

    def apply_styles(self):
        """Apply styles to widgets"""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TButton', font=('Segoe UI', 10))
        
        # Configure chat area tags
        tags = {
            "user_header": {"foreground": "#0078D4", "spacing1": 10, "spacing3": 5},
            "assistant_header": {"foreground": "#107C10", "spacing1": 10, "spacing3": 5},
            "system_header": {"foreground": "#5B5FC7", "spacing1": 10, "spacing3": 5},
            "error": {"foreground": "red"},
            "attachment": {"foreground": "#5B5FC7"},
            "translation_header": {"foreground": "#0078D4", "spacing1": 10, "spacing3": 5}
        }
        
        for tag, config in tags.items():
            self.chat_area.tag_configure(
                tag,
                font=('Segoe UI', 10, 'bold'),
                **config
            )
            
            # Add content tags
            if "header" in tag:
                content_tag = tag.replace("header", "content")
                self.chat_area.tag_configure(
                    content_tag,
                    lmargin1=20,
                    lmargin2=20
                )

    def upload_attachment(self):
        """Upload attachment"""
        file_types = [
            ("All supported files", "*.txt *.pdf *.docx *.doc"),
            ("Text files", "*.txt"),
            ("PDF files", "*.pdf"),
            ("Word documents", "*.docx *.doc"),
            ("All files", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title="Select file",
            filetypes=file_types
        )
        
        if not file_path:
            return
            
        try:
            file_name = os.path.basename(file_path)
            extension = os.path.splitext(file_name)[1].lower()
            
            # Set attachment information
            self.attachment_path = file_path
            self.attachment_name = file_name
            
            if extension in ['.txt']:
                self.attachment_type = 'text'
            elif extension in ['.pdf']:
                self.attachment_type = 'pdf'
            elif extension in ['.docx', '.doc']:
                self.attachment_type = 'docx'
            else:
                self.attachment_type = 'unknown'
                
            # Update UI
            self.attachment_var.set(f"Attached: {file_name}")
            self.attachment_label.pack(side=tk.LEFT)
            
            # If in translation mode, prompt user how to handle the document
            if self.translation_mode:
                self.display_message("system", f"Document attached: {file_name}\nClick send button to start translation.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Unable to load file: {str(e)}")
            self.clear_attachment()

    def clear_attachment(self):
        """Clear current attachment"""
        self.attachment = None
        self.attachment_type = None
        self.attachment_name = None
        self.attachment_path = None
        self.attachment_var.set("")
        self.attachment_label.pack_forget()

    def select_output_location(self):
        """Select output directory"""
        output_dir = filedialog.askdirectory(
            title="Select output directory",
            initialdir=self.config_manager.output_dir
        )
        
        if output_dir:
            self.config_manager.update_settings(output_dir=output_dir)
            self.output_location_var.set(f"Output directory: {os.path.basename(output_dir)}")
            self.status_var.set(f"Output directory changed to: {output_dir}")

    def send_message(self):
        """Send message or start translation task"""
        # If processing message, return
        if self.is_sending:
            return
            
        # Get user input content
        message = self.input_area.get("1.0", "end-1c").strip()
        
        # Translation mode
        if self.translation_mode:
            if self.attachment_path:
                self.start_translation()
            elif message:
                self.translate_text(message)
            else:
                messagebox.showinfo("Information", "Please enter text to translate or upload a document")
            return
            
        # Chat mode
        if not message:
            return
            
        # Display user message
        self.display_message("user", message)
        
        # Clear input field
        self.input_area.delete("1.0", tk.END)
        
        # Display processing
        self.is_sending = True
        self.send_btn.config(state=tk.DISABLED)
        self.progress.pack(side=tk.TOP, fill='x', pady=(0, 5))
        self.progress.start()
        self.status_var.set("Translating...")
        
        # Background thread handles request
        threading.Thread(target=self._process_message, args=(message,), daemon=True).start()

    def _process_message(self, message):
        """Process message in background thread"""
        try:
            # TODO: Implement actual interaction with API
            # Here is just a simple simulation of a reply
            reply = f"You sent: {message}"
            
            # Put reply into queue for updating UI in main thread
            self.message_queue.put(("assistant", reply))
        except Exception as e:
            # Put error message into queue
            error_message = f"Error processing message: {str(e)}"
            self.message_queue.put(("error", error_message))
        finally:
            # Put command to reset UI state into queue
            self.message_queue.put(("reset_ui", None))

    def start_translation(self):
        """Start document translation task"""
        if not self.translator_manager.has_translation:
            self.display_message("error", "Translation function not available, please check API settings")
            return
            
        if not self.attachment_path:
            self.display_message("error", "No document selected")
            return
            
        # Set output file path
        output_dir = self.config_manager.output_dir
        file_name = os.path.basename(self.attachment_path)
        name, ext = os.path.splitext(file_name)
        
        # Determine extension based on output format
        out_ext = ".pdf" if self.output_pdf else ext
        output_path = os.path.join(output_dir, f"{name}_translated{out_ext}")
        
        # Display start translation message
        self.display_message("system", f"Starting document translation: {file_name}\nSource language: {self.source_lang} → Target language: {self.target_lang}")
        
        # Set UI
        self.is_sending = True
        self.translation_in_progress = True
        self.send_btn.config(state=tk.DISABLED)
        self.progress.pack(side=tk.TOP, fill='x', pady=(0, 5))
        self.progress.start()
        self.status_var.set("Translating...")
        
        # Start translation thread
        threading.Thread(
            target=self._translate_document,
            args=(self.attachment_path, output_path),
            daemon=True
        ).start()

    def _translate_document(self, input_path, output_path):
        """Execute document translation in background thread"""
        try:
            # Call translation API
            result = self.translator_manager.translate_document(
                input_path,
                output_path,
                self.source_lang,
                self.target_lang,
                self.percent_to_translate,
                self.direct_pdf
            )
            
            # Success message
            self.message_queue.put(("system", f"Translation completed!\nFile saved to: {output_path}"))
        except Exception as e:
            # Error message
            error_message = f"Translation error: {str(e)}"
            self.message_queue.put(("error", error_message))
        finally:
            # Reset UI
            self.message_queue.put(("reset_ui", None))
            self.message_queue.put(("clear_attachment", None))

    def translate_text(self, text):
        """Translate text in text input field"""
        if not self.translator_manager.has_translation:
            self.display_message("error", "Translation function not available, please check API settings")
            return
            
        # Display user input text
        self.display_message("user", text)
        
        # Clear input field
        self.input_area.delete("1.0", tk.END)
        
        # Set UI
        self.is_sending = True
        self.send_btn.config(state=tk.DISABLED)
        self.progress.pack(side=tk.TOP, fill='x', pady=(0, 5))
        self.progress.start()
        self.status_var.set("Translating...")
        
        # Start translation thread
        threading.Thread(
            target=self._translate_text,
            args=(text,),
            daemon=True
        ).start()

    def _translate_text(self, text):
        """Execute text translation in background thread"""
        try:
            # Call translation API
            translated_text = self.translator_manager.translate_text(
                text,
                self.source_lang,
                self.target_lang,
                self.preserve_format
            )
            
            # Put translated text into queue
            self.message_queue.put(("translation", f"Translation result:\n\n{translated_text}"))
        except Exception as e:
            # Error message
            error_message = f"Translation error: {str(e)}"
            self.message_queue.put(("error", error_message))
        finally:
            # Reset UI
            self.message_queue.put(("reset_ui", None))

    def display_message(self, role, content):
        """Display message in chat area"""
        self.chat_area.config(state='normal')
        
        # Add appropriate header
        if role == "user":
            header = "User"
            header_tag = "user_header"
            content_tag = "user_content"
        elif role == "assistant":
            header = "Assistant"
            header_tag = "assistant_header"
            content_tag = "assistant_content"
        elif role == "system":
            header = "System"
            header_tag = "system_header"
            content_tag = "system_content"
        elif role == "error":
            header = "Error"
            header_tag = "error"
            content_tag = "error"
        elif role == "translation":
            header = "Translation"
            header_tag = "translation_header"
            content_tag = "translation_content"
        else:
            header = role
            header_tag = "system_header"
            content_tag = "system_content"
            
        # Insert header and content
        self.chat_area.insert(tk.END, f"{header}:\n", header_tag)
        self.chat_area.insert(tk.END, f"{content}\n\n", content_tag)
        
        # Auto scroll to bottom
        self.chat_area.see(tk.END)
        self.chat_area.config(state='disabled')

    def check_queue(self):
        """Check message queue, update UI"""
        try:
            while True:
                # Get a message, no blocking
                try:
                    message_type, message = self.message_queue.get_nowait()
                    
                    # Handle message based on type
                    if message_type == "reset_ui":
                        # Reset UI state
                        self.is_sending = False
                        self.translation_in_progress = False
                        self.send_btn.config(state=tk.NORMAL)
                        self.progress.stop()
                        self.progress.pack_forget()
                        self.status_var.set("Ready")
                    elif message_type == "clear_attachment":
                        # Clear attachment
                        self.clear_attachment()
                    else:
                        # Display message
                        self.display_message(message_type, message)
                        
                    # Mark task completed
                    self.message_queue.task_done()
                except queue.Empty:
                    break
                    
        except Exception as e:
            print(f"Error in check_queue: {e}")
            
        # If application is still running, continue checking queue
        if self.running:
            self.root.after(100, self.check_queue)

    def show_settings(self):
        """Show settings dialog"""
        SettingsDialog(self.root, self.config_manager, self.translator_manager)

    def show_translation_settings(self):
        """Show translation settings dialog"""
        TranslationDialog(self.root, self)

    def on_closing(self):
        """Clean up when closing window"""
        self.running = False
        self.root.destroy() 