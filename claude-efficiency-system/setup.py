#!/usr/bin/env python3
"""
Setup script for Claude Efficiency System
Initializes the complete training system with adaptive learning
"""

import os
import sys
import subprocess
from pathlib import Path

def setup_claude_efficiency_system():
    """Initialize the complete Claude efficiency system"""
    print("🚀 Setting up Claude Efficiency System")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ required")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # Setup directories
    base_dir = Path(__file__).parent
    core_dir = base_dir / "core"
    data_dir = base_dir / "data"
    tools_dir = base_dir / "tools"
    
    print(f"📁 Base directory: {base_dir}")
    
    # Initialize word efficiency database
    print("\n📊 Initializing word efficiency database...")
    try:
        if (tools_dir / "load_dont_words.py").exists():
            os.chdir(tools_dir)
            result = subprocess.run([sys.executable, "load_dont_words.py"], 
                                 capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Word database loaded successfully")
                # Count loaded words
                lines = result.stdout.split('\n')
                for line in lines:
                    if "Total words loaded:" in line:
                        print(f"   {line}")
            else:
                print("⚠️  Word database loading had issues")
                print(result.stderr)
        else:
            print("⚠️  Word loader not found, creating basic database")
    except Exception as e:
        print(f"❌ Error loading word database: {e}")
    
    # Initialize core training system
    print("\n🧠 Initializing training system...")
    try:
        os.chdir(core_dir)
        result = subprocess.run([sys.executable, "efficiency_training_system.py", "--init-word-db"], 
                             capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Training system initialized")
        else:
            print("⚠️  Training system initialization had issues")
    except Exception as e:
        print(f"❌ Error initializing training system: {e}")
    
    # Test optimization system
    print("\n🔧 Testing optimization system...")
    try:
        test_input = "Can you help me with some stuff later when you get a chance?"
        result = subprocess.run([sys.executable, "claude_efficiency_optimizer.py", test_input], 
                             capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Optimizer working correctly")
            print(f"   Test: '{test_input}'")
            print(f"   Optimized: '{result.stdout.replace('Optimized: ', '').strip()}'")
        else:
            print("⚠️  Optimizer test failed")
    except Exception as e:
        print(f"❌ Error testing optimizer: {e}")
    
    # Create convenience scripts
    print("\n📝 Creating convenience scripts...")
    
    # Create optimize script
    optimize_script = base_dir / "optimize"
    with open(optimize_script, 'w') as f:
        f.write(f"""#!/bin/bash
# Claude Efficiency Optimizer
cd "{core_dir}"
python3 claude_efficiency_optimizer.py "$@"
""")
    optimize_script.chmod(0o755)
    print(f"✅ Created: {optimize_script}")
    
    # Create training script
    train_script = base_dir / "train"
    with open(train_script, 'w') as f:
        f.write(f"""#!/bin/bash
# Training Dashboard
cd "{core_dir}"
python3 efficiency_training_system.py "$@"
""")
    train_script.chmod(0o755)
    print(f"✅ Created: {train_script}")
    
    # Create adaptive learning script
    adaptive_script = base_dir / "adaptive"
    with open(adaptive_script, 'w') as f:
        f.write(f"""#!/bin/bash
# Adaptive Learning Engine
cd "{base_dir}"
python3 adaptive_training_engine.py "$@"
""")
    adaptive_script.chmod(0o755)
    print(f"✅ Created: {adaptive_script}")
    
    # Create usage examples
    print("\n📚 Usage Examples:")
    print(f"   Optimize question: ./optimize \"your question here\"")
    print(f"   View training dashboard: ./train")
    print(f"   Start adaptive learning: ./adaptive --monitor")
    print(f"   Generate report: ./adaptive --report")
    
    # Create shell aliases
    shell_config = Path.home() / ".zshrc"
    if shell_config.exists():
        print(f"\n🔗 Adding shell aliases to {shell_config}")
        aliases = f"""
# Claude Efficiency System
alias claude-optimize='"{optimize_script}"'
alias claude-train='"{train_script}"'
alias claude-adaptive='"{adaptive_script}"'
"""
        try:
            with open(shell_config, 'a') as f:
                f.write(aliases)
            print("✅ Shell aliases added")
            print("   Reload shell or run: source ~/.zshrc")
        except Exception as e:
            print(f"⚠️  Could not add aliases: {e}")
    
    print("\n🎯 Setup Complete!")
    print("=" * 50)
    print("Claude Efficiency System is ready to use.")
    print("Run './optimize \"your question\"' to start optimizing!")
    
    return True

if __name__ == "__main__":
    setup_claude_efficiency_system()