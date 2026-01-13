"""
Setup Verification Script
Run this to check if your environment is properly configured
"""

import sys
import os


def check_python_version():
    """Check if Python version is 3.8+"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print("✅ Python version: {}.{}.{} (Compatible)".format(
            version.major, version.minor, version.micro
        ))
        return True
    else:
        print("❌ Python version: {}.{}.{} (Requires 3.8+)".format(
            version.major, version.minor, version.micro
        ))
        return False


def check_dependencies():
    """Check if required packages are installed"""
    required_packages = {
        'agno': 'agno',
        'openai': 'openai',
        'dotenv': 'python-dotenv',
        'pydantic': 'pydantic'
    }
    
    all_installed = True
    
    for module, package in required_packages.items():
        try:
            __import__(module)
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is NOT installed")
            all_installed = False
    
    return all_installed


def check_env_file():
    """Check if .env file exists and has API key"""
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        print("   → Copy env.example to .env and add your API keys")
        return False
    
    print("✅ .env file exists")
    
    # Check if API keys are set
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('OPENAI_API_KEY')
    apify_token = os.getenv('APIFY_API_TOKEN')
    
    openai_ok = False
    apify_ok = False
    
    # Check OpenAI API key
    if not api_key:
        print("❌ OPENAI_API_KEY not set in .env")
    elif api_key == 'your_openai_api_key_here':
        print("❌ OPENAI_API_KEY still has placeholder value")
        print("   → Replace with your actual OpenAI API key")
    elif api_key.startswith('sk-'):
        print("✅ OPENAI_API_KEY is configured (starts with sk-)")
        openai_ok = True
    else:
        print("⚠️  OPENAI_API_KEY is set but doesn't start with sk-")
        print("   → Verify your API key is correct")
    
    # Check Apify API token (optional for basic workflow)
    if not apify_token:
        print("⚠️  APIFY_API_TOKEN not set (optional - needed for scraping)")
    elif apify_token == 'your_apify_api_token_here':
        print("⚠️  APIFY_API_TOKEN still has placeholder value")
    else:
        print("✅ APIFY_API_TOKEN is configured")
        apify_ok = True
    
    return openai_ok  # Apify is optional, so only require OpenAI


def check_project_structure():
    """Check if all required files exist"""
    required_files = [
        'config.py',
        'main.py',
        'requirements.txt',
        'agents/__init__.py',
        'agents/orchestrator_agent.py',
        'agents/linkedin_agent.py',
        'agents/x_agent.py'
    ]
    
    all_exist = True
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} is missing")
            all_exist = False
    
    return all_exist


def test_openai_connection():
    """Test if OpenAI API is accessible"""
    try:
        from dotenv import load_dotenv
        import openai
        
        load_dotenv()
        api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key or api_key == 'your_openai_api_key_here':
            print("⏭️  Skipping OpenAI connection test (API key not configured)")
            return None
        
        # Try to initialize OpenAI client
        client = openai.OpenAI(api_key=api_key)
        
        # Test with a minimal completion request
        print("🔄 Testing OpenAI API connection...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        
        print("✅ OpenAI API connection successful")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API connection failed: {str(e)}")
        return False


def main():
    """Run all verification checks"""
    print("\n" + "="*70)
    print("🔍 THOUGHT LEADERSHIP WORKFLOW - SETUP VERIFICATION")
    print("="*70 + "\n")
    
    checks = {
        "Python Version": check_python_version(),
        "Dependencies": check_dependencies(),
        "Environment File": check_env_file(),
        "Project Structure": check_project_structure()
    }
    
    print("\n" + "-"*70)
    print("📊 VERIFICATION SUMMARY")
    print("-"*70)
    
    all_passed = all(checks.values())
    
    for check_name, passed in checks.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{check_name}: {status}")
    
    # Test OpenAI connection if basic checks pass
    if checks["Dependencies"] and checks["Environment File"]:
        print("\n" + "-"*70)
        api_test = test_openai_connection()
        if api_test is not None:
            checks["OpenAI Connection"] = api_test
            all_passed = all_passed and api_test
    
    print("\n" + "="*70)
    
    if all_passed:
        print("✅ ALL CHECKS PASSED - Ready to run the workflow!")
        print("="*70)
        print("\nRun the workflow with: python main.py")
    else:
        print("❌ SOME CHECKS FAILED - Please fix the issues above")
        print("="*70)
        print("\nSetup instructions:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Create .env file: cp env.example .env")
        print("3. Add your OpenAI API key to .env")
        print("4. Run verification again: python verify_setup.py")
    
    print()
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

