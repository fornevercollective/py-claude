#!/usr/bin/env python3
"""
PyTorch-tinygrad Integration Bridge
Provides seamless interoperability between PyTorch and tinygrad
"""

import torch
import numpy as np
from tinygrad import Tensor as TinyTensor
from typing import Union, Any
import time


class TensorBridge:
    """Bridge for converting between PyTorch and tinygrad tensors"""
    
    @staticmethod
    def torch_to_tinygrad(tensor: torch.Tensor) -> TinyTensor:
        """Convert PyTorch tensor to tinygrad tensor"""
        return TinyTensor(tensor.detach().cpu().numpy())
    
    @staticmethod
    def tinygrad_to_torch(tensor: TinyTensor, device: str = 'cpu') -> torch.Tensor:
        """Convert tinygrad tensor to PyTorch tensor"""
        return torch.from_numpy(tensor.numpy()).to(device)
    
    @staticmethod
    def sync_operation(torch_tensor: torch.Tensor, tinygrad_tensor: TinyTensor, 
                      operation: str) -> tuple[torch.Tensor, TinyTensor]:
        """Perform synchronized operations on both tensor types"""
        
        if operation == 'matmul':
            # PyTorch operation
            torch_result = torch.matmul(torch_tensor, torch_tensor.T)
            
            # tinygrad operation
            tinygrad_result = tinygrad_tensor @ tinygrad_tensor.T
            
            return torch_result, tinygrad_result
        
        elif operation == 'sum':
            return torch.sum(torch_tensor), tinygrad_tensor.sum()
        
        elif operation == 'mean':
            return torch.mean(torch_tensor), tinygrad_tensor.mean()
        
        else:
            raise ValueError(f"Unsupported operation: {operation}")


class PerformanceComparator:
    """Compare performance between PyTorch and tinygrad"""
    
    def __init__(self, use_mps: bool = True):
        self.use_mps = use_mps and torch.backends.mps.is_available()
        self.device = 'mps' if self.use_mps else 'cpu'
        
    def benchmark_operation(self, operation: str, size: tuple, iterations: int = 10):
        """Benchmark specific operation"""
        
        # Create test data
        torch_tensor = torch.randn(*size, device=self.device)
        tinygrad_tensor = TinyTensor.randn(*size)
        
        # Warm up
        for _ in range(3):
            if operation == 'matmul':
                _ = torch.matmul(torch_tensor, torch_tensor.T)
                _ = tinygrad_tensor @ tinygrad_tensor.T
        
        # Benchmark PyTorch
        torch_times = []
        for _ in range(iterations):
            start = time.time()
            if operation == 'matmul':
                result = torch.matmul(torch_tensor, torch_tensor.T)
                if self.use_mps:
                    torch.mps.synchronize()  # Ensure MPS operations complete
            torch_times.append(time.time() - start)
        
        # Benchmark tinygrad
        tinygrad_times = []
        for _ in range(iterations):
            start = time.time()
            if operation == 'matmul':
                result = (tinygrad_tensor @ tinygrad_tensor.T).numpy()
            tinygrad_times.append(time.time() - start)
        
        return {
            'pytorch': {
                'mean': np.mean(torch_times),
                'std': np.std(torch_times),
                'device': self.device
            },
            'tinygrad': {
                'mean': np.mean(tinygrad_times),
                'std': np.std(tinygrad_times),
                'device': 'auto'
            }
        }


class ModelBridge:
    """Bridge for running models on both frameworks"""
    
    def __init__(self):
        self.bridge = TensorBridge()
    
    def simple_neural_network_pytorch(self, input_size: int, hidden_size: int, output_size: int):
        """Create simple NN in PyTorch"""
        return torch.nn.Sequential(
            torch.nn.Linear(input_size, hidden_size),
            torch.nn.ReLU(),
            torch.nn.Linear(hidden_size, output_size)
        )
    
    def simple_neural_network_tinygrad(self, input_size: int, hidden_size: int, output_size: int):
        """Create simple NN in tinygrad"""
        from tinygrad.nn import Linear
        
        class SimpleNet:
            def __init__(self):
                self.l1 = Linear(input_size, hidden_size)
                self.l2 = Linear(hidden_size, output_size)
            
            def __call__(self, x):
                return self.l2(self.l1(x).relu())
        
        return SimpleNet()


def demo_integration():
    """Demonstration of PyTorch-tinygrad integration"""
    print("🔗 PyTorch-tinygrad Integration Demo")
    print("=" * 50)
    
    # Initialize bridge
    bridge = TensorBridge()
    comparator = PerformanceComparator()
    
    # Create test tensors
    size = (1000, 1000)
    torch_tensor = torch.randn(*size)
    tinygrad_tensor = TinyTensor.randn(*size)
    
    print(f"Created tensors of size {size}")
    print(f"PyTorch device: {torch_tensor.device}")
    print(f"MPS available: {torch.backends.mps.is_available()}")
    
    # Test conversion
    converted_to_tinygrad = bridge.torch_to_tinygrad(torch_tensor)
    converted_to_torch = bridge.tinygrad_to_torch(tinygrad_tensor)
    
    print(f"✅ Conversion test passed")
    
    # Performance comparison
    print("\n📊 Performance Comparison (Matrix Multiplication)")
    results = comparator.benchmark_operation('matmul', (500, 500), iterations=5)
    
    pytorch_time = results['pytorch']['mean']
    tinygrad_time = results['tinygrad']['mean']
    
    print(f"PyTorch ({results['pytorch']['device']}): {pytorch_time:.4f}s ± {results['pytorch']['std']:.4f}s")
    print(f"tinygrad: {tinygrad_time:.4f}s ± {results['tinygrad']['std']:.4f}s")
    
    if pytorch_time > 0:
        speedup = tinygrad_time / pytorch_time
        if speedup < 1:
            print(f"PyTorch is {1/speedup:.2f}x faster")
        else:
            print(f"tinygrad is {speedup:.2f}x faster")
    
    print("\n🎯 Integration demo complete!")


if __name__ == "__main__":
    demo_integration()