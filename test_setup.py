#!/usr/bin/env python3
"""
Quick test script to verify basic project setup
"""

import sys
import os
import importlib.util

def test_python_version():
    """Test if Python version is compatible"""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 8:
        print("✅ Python version is compatible (3.8+)")
        return True
    else:
        print("❌ Python version not compatible. Requires Python 3.8+")
        return False

def test_required_modules():
    """Test if required modules can be imported"""
    required_modules = [
        'tkinter',
        'requests', 
        'PyPDF2',
        'docx',
        'pdfplumber',
        'PIL',
        'fpdf2',
        'reportlab'
    ]
    
    print("\nTesting required modules:")
    failed_modules = []
    
    for module in required_modules:
        try:
            if module == 'docx':
                # python-docx imports as docx
                importlib.import_module(module)
            elif module == 'PIL':
                # Pillow imports as PIL
                importlib.import_module(module)
            else:
                importlib.import_module(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module} - {e}")
            failed_modules.append(module)
    
    if not failed_modules:
        print("✅ All required modules are available")
        return True
    else:
        print(f"\n❌ Missing modules: {', '.join(failed_modules)}")
        print("Run the setup script to install missing dependencies")
        return False

def test_project_files():
    """Test if main project files exist"""
    required_files = [
        'main.py',
        'requirements.txt',
        'setup.ps1',
        'install.bat',
        'README_SETUP.md'
    ]
    
    print("\nTesting project files:")
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file}")
            missing_files.append(file)
    
    if not missing_files:
        print("✅ All required project files exist")
        return True
    else:
        print(f"\n❌ Missing files: {', '.join(missing_files)}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("MITranslateTool Setup Test")
    print("=" * 50)
    
    tests = [
        test_python_version,
        test_project_files,
        test_required_modules
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 50)
    print("Test Summary:")
    print("=" * 50)
    
    if all(results):
        print("🎉 All tests passed! The project is ready to run.")
        print("\nTo start the application:")
        print("1. In VSCode: Press F5")
        print("2. Command line: python main.py")
    else:
        print("⚠️  Some tests failed. Please:")
        print("1. Run the setup script: install.bat")
        print("2. Or manually install missing dependencies")
    
    return all(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 