class TranslatorManager:
    def __init__(self):
        # 初始化变量
        self._has_translation = False
        self._has_file_libs = False
        self.translator = None
        
        # 检查翻译相关库
        self._check_translation_libs()
        
        # 检查文件处理相关库
        self._check_file_libs()

    def _check_translation_libs(self):
        """检查翻译相关库是否可用"""
        try:
            import translation_api
            import document_processor
            self._has_translation = True
            self.translator = translation_api.translator
        except ImportError as e:
            print(f"Translation libraries not available: {e}")
            self._has_translation = False
            self.translator = None

    def _check_file_libs(self):
        """检查文件处理相关库是否可用"""
        try:
            import docx
            import PyPDF2
            import pdfplumber
            import fpdf2
            import reportlab
            self._has_file_libs = True
        except ImportError as e:
            print(f"File handling libraries not available: {e}")
            self._has_file_libs = False

    @property
    def has_translation(self):
        return self._has_translation

    @property
    def has_file_libs(self):
        return self._has_file_libs

    def translate_text(self, text, source_lang, target_lang, preserve_format=True):
        """Translate text using the translation API"""
        if not self.has_translation:
            raise RuntimeError("Translation feature is not available")
            
        return self.translator.translate_text(
            text,
            source_lang=source_lang,
            target_lang=target_lang,
            preserve_format=preserve_format
        )

    def translate_document(self, input_path, output_path, source_lang, target_lang, 
                         percent_to_translate=100, direct_pdf=True):
        """Translate document using the translation API"""
        if not self.has_translation:
            raise RuntimeError("Translation feature is not available")
        
        # 这里提前导入，确保PyInstaller能识别依赖
        import document_processor
        return document_processor.translate_document(
            input_path,
            output_path,
            self.translator.translate_text,
            source_lang=source_lang,
            target_lang=target_lang,
            percent_to_translate=percent_to_translate,
            direct_pdf=direct_pdf
        ) 