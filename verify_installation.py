#!/usr/bin/env python3
"""
Verification script for the ethical keylogger installation
Checks that all components are properly installed and configured

Made By Vision - github.com/vision-dev1
"""

import os
import sys
import subprocess

def check_python_version():
    """Check Python version"""
    print("[*] Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 6:
        print(f"[+] Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"[!] Python {version.major}.{version.minor}.{version.micro} - Version too old")
        return False

def check_system_tools():
    """Check if required system tools are installed"""
    tools = ['xdotool', 'scrot']
    all_good = True
    
    print("[*] Checking system tools...")
    for tool in tools:
        try:
            result = subprocess.run(['which', tool], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"[+] {tool} - Found at {result.stdout.strip()}")
            else:
                print(f"[!] {tool} - Not found")
                all_good = False
        except Exception as e:
            print(f"[!] {tool} - Error checking: {e}")
            all_good = False
            
    return all_good

def check_python_dependencies():
    """Check if Python dependencies are installed"""
    dependencies = ['pynput', 'cryptography', 'psutil', 'flask']
    all_good = True
    
    print("[*] Checking Python dependencies...")
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"[+] {dep} - Installed")
        except ImportError:
            print(f"[!] {dep} - Not installed")
            all_good = False
        except Exception as e:
            print(f"[!] {dep} - Error importing: {e}")
            all_good = False
            
    return all_good

def check_files():
    """Check if required files exist"""
    required_files = [
        'keylogger.py',
        'decrypt.py',
        'dashboard.py',
        'requirements.txt',
        'INSTALL.md',
        'README.md',
        'keylogger.service',
        'start_keylogger.sh',
        'start_dashboard.sh',
        'view_logs.sh'
    ]
    
    print("[*] Checking required files...")
    all_good = True
    for file in required_files:
        if os.path.exists(file):
            print(f"[+] {file} - Found")
        else:
            print(f"[!] {file} - Missing")
            all_good = False
            
    return all_good

def check_permissions():
    """Check if scripts have execute permissions"""
    scripts = ['start_keylogger.sh', 'start_dashboard.sh', 'view_logs.sh']
    
    print("[*] Checking script permissions...")
    all_good = True
    for script in scripts:
        if os.path.exists(script):
            if os.access(script, os.X_OK):
                print(f"[+] {script} - Executable")
            else:
                print(f"[!] {script} - Not executable")
                all_good = False
        else:
            print(f"[!] {script} - Missing")
            all_good = False
            
    return all_good

def main():
    """Run all verification checks"""
    print("Ethical Keylogger Installation Verification")
    print("=" * 45)
    print("Made By Vision - https://visionkc.com.np\n")
    
    checks = [
        check_python_version,
        check_system_tools,
        check_python_dependencies,
        check_files,
        check_permissions
    ]
    
    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
            print()  # Empty line for readability
        except Exception as e:
            print(f"[!] Error during {check.__name__}: {e}\n")
            results.append(False)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("=" * 45)
    print(f"Verification Summary: {passed}/{total} checks passed")
    
    if all(results):
        print("[+] All checks passed! Installation is complete.")
        print("\nNext steps:")
        print("1. Run './start_keylogger.sh' to start the keylogger")
        print("2. Run './start_dashboard.sh' to start the web dashboard")
        print("3. Run './view_logs.sh' to view decrypted logs")
        return True
    else:
        print("[!] Some checks failed. Please review the output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)