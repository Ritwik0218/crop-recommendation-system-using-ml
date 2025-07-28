#!/usr/bin/env python3
"""
Installation and setup validation script for Crop Recommendation System.
This script checks if all dependencies are properly installed and models are accessible.
"""

import sys
import os
import importlib
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} is not supported. Requires Python 3.8+")
        return False

def check_dependencies():
    """Check if required packages are installed."""
    required_packages = {
        'flask': 'Flask',
        'numpy': 'NumPy',
        'sklearn': 'scikit-learn',
        'pickle': 'pickle (built-in)'
    }
    
    all_good = True
    for package, name in required_packages.items():
        try:
            importlib.import_module(package)
            print(f"✅ {name} is installed")
        except ImportError:
            print(f"❌ {name} is not installed")
            all_good = False
    
    return all_good

def check_model_files():
    """Check if ML model files exist."""
    model_files = [
        'model.pkl',
        'minmaxscaler.pkl',
        'standardscaler.pkl'
    ]
    
    all_good = True
    for file in model_files:
        if Path(file).exists():
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} is missing")
            all_good = False
    
    return all_good

def check_template_files():
    """Check if template files exist."""
    template_files = [
        'templates/index.html',
        'static/favicon.ico',
        'static/crop_images/default.jpg'
    ]
    
    all_good = True
    for file in template_files:
        if Path(file).exists():
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} is missing")
            all_good = False
    
    return all_good

def test_model_loading():
    """Test if models can be loaded successfully."""
    try:
        import pickle
        
        # Test loading each model
        with open('model.pkl', 'rb') as f:
            model = pickle.load(f)
        print("✅ Main model loads successfully")
        
        with open('minmaxscaler.pkl', 'rb') as f:
            scaler = pickle.load(f)
        print("✅ MinMax scaler loads successfully")
        
        with open('standardscaler.pkl', 'rb') as f:
            scaler = pickle.load(f)
        print("✅ Standard scaler loads successfully")
        
        return True
    except Exception as e:
        print(f"❌ Error loading models: {e}")
        return False

def main():
    """Run all validation checks."""
    print("🌾 Crop Recommendation System - Installation Validator")
    print("=" * 60)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Model Files", check_model_files),
        ("Template Files", check_template_files),
        ("Model Loading", test_model_loading)
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        print(f"\n📋 Checking {check_name}...")
        if not check_func():
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All checks passed! The system is ready to run.")
        print("💡 Run 'python app.py' to start the application")
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
