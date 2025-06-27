#!/usr/bin/env python3
"""
PyTorch-tinygrad Development Environment Setup
Optimized for Apple M4 with Neural Engine acceleration
"""

import os
import sys
import subprocess
import platform
import psutil
from pathlib import Path

def check_system():
    """Check system specifications and compatibility"""
    print("=== System Information ===")
    print(f"Platform: {platform.platform()}")
    print(f"Python Version: {sys.version}")
    print(f"CPU Count: {psutil.cpu_count()}")
    print(f"Memory: {psutil.virtual_memory().total / (1024**3):.1f} GB")
    
    # Check for Apple Silicon
    if platform.machine() == 'arm64' and platform.system() == 'Darwin':
        print("✅ Apple Silicon detected - optimized for Metal Performance Shaders")
        return True
    else:
        print("⚠️  Not Apple Silicon - using standard configuration")
        return False

def setup_pytorch_mps():
    """Configure PyTorch for Metal Performance Shaders on Apple Silicon"""
    test_code = '''
import torch
print(f"PyTorch Version: {torch.__version__}")
print(f"MPS Available: {torch.backends.mps.is_available()}")
print(f"MPS Built: {torch.backends.mps.is_built()}")

if torch.backends.mps.is_available():
    device = torch.device("mps")
    x = torch.randn(1000, 1000, device=device)
    y = torch.matmul(x, x.T)
    print("✅ MPS acceleration working!")
else:
    print("❌ MPS not available")
'''
    
    try:
        result = subprocess.run([sys.executable, '-c', test_code], 
                              capture_output=True, text=True, timeout=30)
        print("=== PyTorch MPS Test ===")
        print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"Error testing PyTorch MPS: {e}")
        return False

def setup_tinygrad():
    """Configure tinygrad for optimal performance"""
    test_code = '''
import tinygrad
from tinygrad import Tensor
print(f"tinygrad version: {tinygrad.__version__}")

# Test basic operations
x = Tensor.randn(100, 100)
y = x @ x.T
result = y.numpy()
print("✅ tinygrad working!")
print(f"Result shape: {result.shape}")
'''
    
    try:
        result = subprocess.run([sys.executable, '-c', test_code], 
                              capture_output=True, text=True, timeout=30)
        print("=== tinygrad Test ===")
        print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"Error testing tinygrad: {e}")
        return False

def create_benchmark_script():
    """Create performance benchmark script"""
    benchmark_code = '''#!/usr/bin/env python3
"""
Performance Benchmark Suite for PyTorch vs tinygrad
"""

import time
import torch
import numpy as np
from tinygrad import Tensor
import matplotlib.pyplot as plt
import json
from datetime import datetime

def benchmark_pytorch_cpu(size=1000, iterations=10):
    """Benchmark PyTorch on CPU"""
    times = []
    device = torch.device('cpu')
    
    for _ in range(iterations):
        start = time.time()
        x = torch.randn(size, size, device=device)
        y = torch.matmul(x, x.T)
        torch.sum(y)  # Force computation
        times.append(time.time() - start)
    
    return np.mean(times), np.std(times)

def benchmark_pytorch_mps(size=1000, iterations=10):
    """Benchmark PyTorch on Apple Silicon MPS"""
    if not torch.backends.mps.is_available():
        return None, None
        
    times = []
    device = torch.device('mps')
    
    for _ in range(iterations):
        start = time.time()
        x = torch.randn(size, size, device=device)
        y = torch.matmul(x, x.T)
        torch.sum(y)  # Force computation
        times.append(time.time() - start)
    
    return np.mean(times), np.std(times)

def benchmark_tinygrad(size=1000, iterations=10):
    """Benchmark tinygrad"""
    times = []
    
    for _ in range(iterations):
        start = time.time()
        x = Tensor.randn(size, size)
        y = x @ x.T
        y.sum().numpy()  # Force computation
        times.append(time.time() - start)
    
    return np.mean(times), np.std(times)

def run_full_benchmark():
    """Run comprehensive benchmark suite"""
    sizes = [100, 500, 1000, 2000]
    results = {'timestamp': datetime.now().isoformat(), 'benchmarks': {}}
    
    for size in sizes:
        print(f"\\nBenchmarking size {size}x{size}...")
        
        # PyTorch CPU
        cpu_mean, cpu_std = benchmark_pytorch_cpu(size)
        print(f"PyTorch CPU: {cpu_mean:.4f}s ± {cpu_std:.4f}s")
        
        # PyTorch MPS
        mps_mean, mps_std = benchmark_pytorch_mps(size)
        if mps_mean is not None:
            print(f"PyTorch MPS: {mps_mean:.4f}s ± {mps_std:.4f}s")
            speedup = cpu_mean / mps_mean if mps_mean > 0 else 0
            print(f"MPS Speedup: {speedup:.2f}x")
        
        # tinygrad
        tg_mean, tg_std = benchmark_tinygrad(size)
        print(f"tinygrad: {tg_mean:.4f}s ± {tg_std:.4f}s")
        
        results['benchmarks'][size] = {
            'pytorch_cpu': {'mean': cpu_mean, 'std': cpu_std},
            'pytorch_mps': {'mean': mps_mean, 'std': mps_std} if mps_mean else None,
            'tinygrad': {'mean': tg_mean, 'std': tg_std}
        }
    
    # Save results
    with open('benchmark_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\\n=== Benchmark Complete ===")
    print("Results saved to benchmark_results.json")
    
    return results

if __name__ == "__main__":
    results = run_full_benchmark()
'''
    
    with open('/Users/taderiscon/PyCharmProjects/pytorch-tinygrad-dev/benchmark.py', 'w') as f:
        f.write(benchmark_code)
    
    print("✅ Benchmark script created")

def main():
    """Main setup function"""
    print("🚀 Setting up PyTorch-tinygrad Development Environment")
    
    # Check system
    is_apple_silicon = check_system()
    
    print("\n📦 Installing packages...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True)
        print("✅ Packages installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Package installation failed: {e}")
        return False
    
    # Test installations
    pytorch_ok = setup_pytorch_mps()
    tinygrad_ok = setup_tinygrad()
    
    if pytorch_ok and tinygrad_ok:
        print("✅ All components working correctly")
        create_benchmark_script()
        
        print("\n🎯 Setup Complete!")
        print("Next steps:")
        print("1. Run: python benchmark.py")
        print("2. Open PyCharm and create a new project")
        print("3. Set interpreter to this Python environment")
        
        return True
    else:
        print("❌ Some components failed - check error messages above")
        return False

if __name__ == "__main__":
    main()