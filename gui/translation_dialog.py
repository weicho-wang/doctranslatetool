import tkinter as tk
from tkinter import ttk

class TranslationDialog:
    def __init__(self, parent, app):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Translation Settings")
        self.dialog.geometry("400x280")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.app = app
        self.create_widgets()
        
    def create_widgets(self):
        # Content percentage slider
        ttk.Label(
            self.dialog, 
            text="Percentage of content to translate:",
            font=('Segoe UI', 10)
        ).grid(row=0, column=0, columnspan=2, padx=10, pady=(20, 5), sticky=tk.W)
        
        # Create slider frame
        slider_frame = ttk.Frame(self.dialog)
        slider_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 20), sticky=tk.W+tk.E)
        
        # Percentage slider
        self.percent_slider = ttk.Scale(
            slider_frame,
            from_=10,
            to=100,
            orient='horizontal',
            length=300,
            value=self.app.percent_to_translate
        )
        self.percent_slider.pack(side=tk.LEFT, fill='x', expand=True)
        
        # Percentage label
        self.percent_label = ttk.Label(
            slider_frame,
            width=5,
            text=f"{int(self.percent_slider.get())}%"
        )
        self.percent_label.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Update label when slider changes
        self.percent_slider.bind("<Motion>", self.update_percent_label)
        
        # Output format section
        ttk.Label(
            self.dialog, 
            text="Output format:",
            font=('Segoe UI', 10)
        ).grid(row=2, column=0, columnspan=2, padx=10, pady=(10, 5), sticky=tk.W)
        
        # PDF output option
        self.pdf_output_var = tk.BooleanVar(value=self.app.output_pdf)
        pdf_check = ttk.Checkbutton(
            self.dialog, 
            text="Output as PDF format",
            variable=self.pdf_output_var
        )
        pdf_check.grid(row=3, column=0, columnspan=2, padx=10, pady=(0, 5), sticky=tk.W)
        
        # Direct PDF option
        self.direct_pdf_var = tk.BooleanVar(value=self.app.direct_pdf)
        direct_pdf_check = ttk.Checkbutton(
            self.dialog, 
            text="Generate PDF directly (better formatting fidelity)",
            variable=self.direct_pdf_var
        )
        direct_pdf_check.grid(row=4, column=0, columnspan=2, padx=10, pady=(0, 5), sticky=tk.W)
        
        # Information label
        ttk.Label(
            self.dialog, 
            text="Direct PDF generation uses ReportLab library\nto create PDF files with better format preservation.",
            foreground="blue"
        ).grid(row=5, column=0, columnspan=2, padx=10, pady=(0, 10), sticky=tk.W)
        
        # Buttons
        self.create_buttons()
        
    def create_buttons(self):
        btn_frame = ttk.Frame(self.dialog)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        ttk.Button(
            btn_frame, 
            text="Save", 
            command=self.save_settings
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(
            btn_frame, 
            text="Cancel", 
            command=self.dialog.destroy
        ).pack(side=tk.LEFT, padx=10)
        
    def update_percent_label(self, event=None):
        self.percent_label.config(text=f"{int(self.percent_slider.get())}%")
        
    def save_settings(self):
        self.app.percent_to_translate = int(self.percent_slider.get())
        self.app.output_pdf = self.pdf_output_var.get()
        self.app.direct_pdf = self.direct_pdf_var.get()
        self.dialog.destroy() 