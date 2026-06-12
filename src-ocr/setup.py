#!/usr/bin/env python3
"""
Installation and Setup Helper
Run this script to help set up the Document Extractor Chatbot
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def print_step(number, text):
    """Print formatted step"""
    print(f"  Step {number}: {text}")

def check_python_version():
    """Check if Python version is supported"""
    print_header("Checking Python Version")
    
    version = sys.version_info
    print(f"Python Version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and 8 <= version.minor <= 12:
        print("✓ Python version is compatible (3.8 through 3.12)")
        return True
    else:
        print("✗ Python 3.8 through 3.12 is required")
        print("  If your system has a newer preview Python, use a stable interpreter:")
        print("  py -3.12 -m venv venv")
        return False

def check_tesseract():
    """Check if Tesseract is installed"""
    print_header("Checking Tesseract Installation")
    
    system = platform.system()
    
    if system == "Windows":
        paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
        ]
        
        found = False
        for path in paths:
            if os.path.exists(path):
                print(f"✓ Tesseract found at: {path}")
                found = True
                break
        
        if not found:
            print("✗ Tesseract not found")
            print("\n  Download from: https://github.com/UB-Mannheim/tesseract/wiki")
            print("  Install and note the installation path")
            return False
    
    elif system == "Darwin":  # macOS
        try:
            result = subprocess.run(["which", "tesseract"], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✓ Tesseract found at: {result.stdout.strip()}")
                return True
            else:
                print("✗ Tesseract not found")
                print("\n  Install with: brew install tesseract")
                return False
        except Exception as e:
            print(f"✗ Error checking tesseract: {e}")
            return False
    
    elif system == "Linux":
        try:
            result = subprocess.run(["which", "tesseract"], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✓ Tesseract found at: {result.stdout.strip()}")
                return True
            else:
                print("✗ Tesseract not found")
                print("\n  Install with: sudo apt-get install tesseract-ocr")
                return False
        except Exception as e:
            print(f"✗ Error checking tesseract: {e}")
            return False
    
    return False

def setup_virtual_environment():
    """Create virtual environment"""
    print_header("Setting Up Virtual Environment")
    
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("✓ Virtual environment already exists")
        return True
    
    try:
        print("  Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✓ Virtual environment created successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to create virtual environment: {e}")
        return False

def get_pip_command():
    """Get the appropriate pip command for the current OS and venv"""
    system = platform.system()
    
    if system == "Windows":
        return "venv\\Scripts\\pip"
    else:
        return "venv/bin/pip"

def install_dependencies():
    """Install Python dependencies"""
    print_header("Installing Python Dependencies")
    
    pip_cmd = get_pip_command()
    
    if not os.path.exists("requirements.txt"):
        print("✗ requirements.txt not found")
        return False
    
    try:
        print("  Installing packages (this may take a few minutes)...")
        
        # Upgrade pip first
        subprocess.run([pip_cmd, "install", "--upgrade", "pip"], check=True, capture_output=True)
        
        # Install requirements
        subprocess.run([pip_cmd, "install", "-r", "requirements.txt"], check=True)
        
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install dependencies: {e}")
        return False

def verify_installation():
    """Verify all packages are installed"""
    print_header("Verifying Installation")
    
    required_packages = {
        'streamlit': 'Streamlit',
        'pytesseract': 'Pytesseract',
        'PIL': 'Pillow',
        'cv2': 'OpenCV',
        'pdf2image': 'pdf2image',
        'numpy': 'NumPy'
    }
    
    all_good = True
    
    for package, name in required_packages.items():
        try:
            __import__(package)
            print(f"✓ {name}")
        except ImportError:
            print(f"✗ {name} not found")
            all_good = False
    
    return all_good

def print_next_steps():
    """Print next steps"""
    print_header("Setup Complete!")
    
    system = platform.system()
    
    if system == "Windows":
        activate_cmd = "venv\\Scripts\\activate"
    else:
        activate_cmd = "source venv/bin/activate"
    
    print("  Next steps:")
    print(f"\n  1. Activate virtual environment:")
    print(f"     {activate_cmd}")
    print(f"\n  2. Run the application:")
    print(f"     streamlit run app.py")
    print(f"\n  3. Open your browser:")
    print(f"     http://localhost:8501")
    print(f"\n  4. Upload a document and start extracting!")
    
    print("\n  For more information, see:")
    print("  - README.md - Full documentation")
    print("  - QUICK_START.md - Quick setup guide")

def main():
    """Main setup function"""
    print_header("Document Extractor Chatbot - Setup Assistant")
    
    steps_passed = 0
    steps_total = 5
    
    # Step 1: Check Python
    print_step(1, f"Checking Python version (Required: 3.8+)")
    if check_python_version():
        steps_passed += 1
    
    # Step 2: Check Tesseract
    print_step(2, f"Checking Tesseract OCR")
    if check_tesseract():
        steps_passed += 1
    else:
        print("\n  ⚠ Warning: Tesseract not found")
        print("  The application will not work without Tesseract.")
        print("  Please install it and try again.\n")
    
    # Step 3: Virtual Environment
    print_step(3, f"Setting up Python virtual environment")
    if setup_virtual_environment():
        steps_passed += 1
    
    # Step 4: Install Dependencies
    print_step(4, f"Installing Python dependencies")
    if install_dependencies():
        steps_passed += 1
    
    # Step 5: Verify Installation
    print_step(5, f"Verifying installation")
    if verify_installation():
        steps_passed += 1
    
    # Summary
    print_header("Setup Summary")
    print(f"  Completed: {steps_passed}/{steps_total} steps")
    
    if steps_passed == steps_total:
        print("\n  ✓ Setup completed successfully!")
        print_next_steps()
        return 0
    else:
        print("\n  ✗ Some steps failed. Please review the errors above.")
        print("  You may need to manually install or configure something.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
