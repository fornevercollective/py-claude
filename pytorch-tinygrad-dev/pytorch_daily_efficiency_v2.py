#!/usr/bin/env python3
"""
PyTorch Daily Efficiency Reporter v2.0
Advanced ML workload optimization and reporting for PyTorch/tinygrad development
Optimized for Apple M4 Neural Engine
"""

import os
import json
import time
import psutil
import sqlite3
import torch
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import numpy as np

# Claude Startup Banner
CLAUDE_BANNER = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║    ████████╗ ██████╗ ██████╗  ██████╗██╗  ██╗    ██████╗██╗      █████╗     ║
║    ╚══██╔══╝██╔═══██╗██╔══██╗██╔════╝██║  ██║   ██╔════╝██║     ██╔══██╗    ║
║       ██║   ██║   ██║██████╔╝██║     ███████║   ██║     ██║     ███████║    ║
║       ██║   ██║   ██║██╔══██╗██║     ██╔══██║   ██║     ██║     ██╔══██║    ║
║       ██║   ╚██████╔╝██║  ██║╚██████╗██║  ██║   ╚██████╗███████╗██║  ██║    ║
║       ╚═╝    ╚═════╝ ╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝    ╚═════╝╚══════╝╚═╝  ╚═╝    ║
║                                                                              ║
║                    ██████╗ ███████╗██╗   ██╗██████╗ ███████╗                ║
║                   ██╔═══██╗██╔════╝██║   ██║██╔══██╗██╔════╝                ║
║                   ██║   ██║█████╗  ██║   ██║██║  ██║█████╗                  ║
║                   ██║   ██║██╔══╝  ╚██╗ ██╔╝██║  ██║██╔══╝                  ║
║                   ╚██████╔╝███████╗ ╚████╔╝ ██████╔╝███████╗                ║
║                    ╚═════╝ ╚══════╝  ╚═══╝  ╚═════╝ ╚══════╝                ║
║                                                                              ║
║              🚀 PyTorch Daily Efficiency Reporter v2.0 🧠                   ║
║                                                                              ║
║     ⚡ Optimized for Apple M4 Neural Engine + Metal Performance Shaders     ║
║     🔬 Advanced ML workload tracking and optimization                       ║
║     📊 Real-time performance monitoring and reporting                       ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

class PyTorchDailyEfficiencyReporter:
    """Advanced PyTorch/tinygrad efficiency monitoring and reporting system"""
    
    def __init__(self):
        self.version = "2.0"
        self.project_root = Path(__file__).parent
        self.db_path = self.project_root / "pytorch_efficiency.db"
        self.report_dir = self.project_root / "efficiency_reports"
        self.report_dir.mkdir(exist_ok=True)
        
        # Show banner
        print(CLAUDE_BANNER)
        time.sleep(1)  # Brief pause to appreciate the banner
        
        self.init_database()
        self.check_pytorch_environment()
        
    def init_database(self):
        """Initialize PyTorch-specific efficiency tracking database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # PyTorch performance metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pytorch_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                operation_type TEXT,
                tensor_size TEXT,
                device_used TEXT,
                execution_time_ms REAL,
                memory_allocated_mb REAL,
                memory_cached_mb REAL,
                mps_acceleration BOOLEAN,
                throughput_ops_per_sec REAL
            )
        ''')
        
        # tinygrad performance metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tinygrad_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                operation_type TEXT,
                tensor_size TEXT,
                execution_time_ms REAL,
                memory_usage_mb REAL,
                backend_used TEXT
            )
        ''')
        
        # ML training sessions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS training_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_start DATETIME,
                session_end DATETIME,
                model_name TEXT,
                framework TEXT,
                epochs_completed INTEGER,
                final_loss REAL,
                avg_epoch_time_sec REAL,
                device_used TEXT,
                dataset_size INTEGER,
                batch_size INTEGER,
                learning_rate REAL,
                optimizer TEXT,
                peak_memory_mb REAL
            )
        ''')
        
        # System performance during ML workloads
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_ml_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                cpu_percent REAL,
                memory_percent REAL,
                memory_available_gb REAL,
                gpu_utilization REAL,
                temperature_celsius REAL,
                power_consumption_watts REAL,
                thermal_state TEXT,
                active_ml_processes INTEGER
            )
        ''')
        
        # Daily efficiency summaries
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_summaries_v2 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE UNIQUE,
                pytorch_operations INTEGER,
                tinygrad_operations INTEGER,
                training_sessions INTEGER,
                avg_mps_speedup REAL,
                peak_memory_usage_gb REAL,
                total_ml_compute_hours REAL,
                efficiency_score REAL,
                optimization_suggestions TEXT,
                neural_engine_utilization REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def check_pytorch_environment(self):
        """Comprehensive PyTorch environment check"""
        print("🔍 PyTorch Environment Check")
        print("-" * 40)
        
        env_status = {
            'pytorch_version': torch.__version__,
            'mps_available': torch.backends.mps.is_available(),
            'mps_built': torch.backends.mps.is_built(),
            'cuda_available': torch.cuda.is_available(),
            'cpu_threads': torch.get_num_threads()
        }
        
        # Check tinygrad
        try:
            from tinygrad import Tensor as TinyTensor
            env_status['tinygrad_available'] = True
            print("✅ tinygrad: Available")
        except ImportError:
            env_status['tinygrad_available'] = False
            print("❌ tinygrad: Not installed")
        
        # Display PyTorch status
        print(f"✅ PyTorch: {env_status['pytorch_version']}")
        print(f"{'✅' if env_status['mps_available'] else '❌'} MPS Available: {env_status['mps_available']}")
        print(f"{'✅' if env_status['mps_built'] else '❌'} MPS Built: {env_status['mps_built']}")
        print(f"✅ CPU Threads: {env_status['cpu_threads']}")
        
        if env_status['mps_available']:
            # Quick MPS test
            try:
                device = torch.device("mps")
                x = torch.randn(100, 100, device=device)
                y = torch.matmul(x, x.T)
                print("✅ MPS Test: Passed")
            except Exception as e:
                print(f"❌ MPS Test: Failed - {e}")
        
        print("-" * 40)
        return env_status
    
    def benchmark_pytorch_operation(self, operation_type: str, tensor_size: tuple, 
                                   iterations: int = 10, use_mps: bool = True):
        """Benchmark specific PyTorch operation"""
        device = 'mps' if use_mps and torch.backends.mps.is_available() else 'cpu'
        
        times = []
        memory_allocated = []
        memory_cached = []
        
        for _ in range(iterations):
            if device == 'mps':
                torch.mps.empty_cache()
            
            start_time = time.time()
            
            if operation_type == 'matmul':
                x = torch.randn(*tensor_size, device=device)
                y = torch.randn(*tensor_size, device=device)
                result = torch.matmul(x, y.T)
            elif operation_type == 'conv2d':
                x = torch.randn(*tensor_size, device=device)
                conv = torch.nn.Conv2d(tensor_size[1], 64, 3, padding=1).to(device)
                result = conv(x)
            elif operation_type == 'linear':
                x = torch.randn(*tensor_size, device=device)
                linear = torch.nn.Linear(tensor_size[-1], 512).to(device)
                result = linear(x)
            
            if device == 'mps':
                torch.mps.synchronize()
            
            end_time = time.time()
            times.append((end_time - start_time) * 1000)  # Convert to milliseconds
            
            # Memory tracking
            if device == 'mps':
                allocated = torch.mps.current_allocated_memory() / (1024 * 1024)  # MB
                cached = torch.mps.driver_allocated_memory() / (1024 * 1024)  # MB
            else:
                allocated = 0  # CPU memory tracking is complex
                cached = 0
            
            memory_allocated.append(allocated)
            memory_cached.append(cached)
        
        # Calculate statistics
        avg_time = np.mean(times)
        throughput = 1000 / avg_time if avg_time > 0 else 0  # ops per second
        
        # Log to database
        self.log_pytorch_metric(
            operation_type=operation_type,
            tensor_size=str(tensor_size),
            device_used=device,
            execution_time_ms=avg_time,
            memory_allocated_mb=np.mean(memory_allocated),
            memory_cached_mb=np.mean(memory_cached),
            mps_acceleration=(device == 'mps'),
            throughput_ops_per_sec=throughput
        )
        
        return {
            'operation': operation_type,
            'tensor_size': tensor_size,
            'device': device,
            'avg_time_ms': avg_time,
            'std_time_ms': np.std(times),
            'throughput_ops_per_sec': throughput,
            'avg_memory_mb': np.mean(memory_allocated),
            'mps_acceleration': (device == 'mps')
        }
    
    def log_pytorch_metric(self, operation_type: str, tensor_size: str, device_used: str,
                          execution_time_ms: float, memory_allocated_mb: float,
                          memory_cached_mb: float, mps_acceleration: bool,
                          throughput_ops_per_sec: float):
        """Log PyTorch performance metric to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO pytorch_metrics 
            (operation_type, tensor_size, device_used, execution_time_ms,
             memory_allocated_mb, memory_cached_mb, mps_acceleration, throughput_ops_per_sec)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (operation_type, tensor_size, device_used, execution_time_ms,
              memory_allocated_mb, memory_cached_mb, mps_acceleration, throughput_ops_per_sec))
        
        conn.commit()
        conn.close()
    
    def collect_system_ml_metrics(self):
        """Collect system metrics during ML workloads"""
        # Basic system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        # Count active ML processes
        ml_processes = 0
        for proc in psutil.process_iter(['name']):
            try:
                if any(ml_name in proc.info['name'].lower() 
                      for ml_name in ['python', 'jupyter', 'tensorboard', 'pytorch']):
                    ml_processes += 1
            except:
                pass
        
        # Thermal state
        try:
            thermal_result = subprocess.run(['pmset', '-g', 'thermstate'], 
                                          capture_output=True, text=True)
            thermal_state = "normal" if "CPU_Speed_Limit" not in thermal_result.stdout else "throttling"
        except:
            thermal_state = "unknown"
        
        metrics = {
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_available_gb': memory.available / (1024**3),
            'gpu_utilization': 0,  # Placeholder for future GPU monitoring
            'temperature_celsius': 0,  # Placeholder
            'power_consumption_watts': 0,  # Placeholder
            'thermal_state': thermal_state,
            'active_ml_processes': ml_processes
        }
        
        # Log to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO system_ml_metrics 
            (cpu_percent, memory_percent, memory_available_gb, gpu_utilization,
             temperature_celsius, power_consumption_watts, thermal_state, active_ml_processes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (metrics['cpu_percent'], metrics['memory_percent'], metrics['memory_available_gb'],
              metrics['gpu_utilization'], metrics['temperature_celsius'], 
              metrics['power_consumption_watts'], metrics['thermal_state'], 
              metrics['active_ml_processes']))
        
        conn.commit()
        conn.close()
        
        return metrics
    
    def run_comprehensive_benchmark(self):
        """Run comprehensive PyTorch benchmark suite"""
        print("🏁 Running Comprehensive PyTorch Benchmark")
        print("=" * 50)
        
        benchmark_results = []
        
        # Matrix operations
        print("🔢 Matrix Operations...")
        for size in [(100, 100), (500, 500), (1000, 1000)]:
            result = self.benchmark_pytorch_operation('matmul', size)
            benchmark_results.append(result)
            print(f"  {size}: {result['avg_time_ms']:.2f}ms ({result['device']})")
        
        # Neural network layers
        print("🧠 Neural Network Layers...")
        conv_result = self.benchmark_pytorch_operation('conv2d', (1, 3, 224, 224))
        linear_result = self.benchmark_pytorch_operation('linear', (32, 784))
        benchmark_results.extend([conv_result, linear_result])
        
        print(f"  Conv2D: {conv_result['avg_time_ms']:.2f}ms ({conv_result['device']})")
        print(f"  Linear: {linear_result['avg_time_ms']:.2f}ms ({linear_result['device']})")
        
        # System metrics during benchmark
        system_metrics = self.collect_system_ml_metrics()
        
        print("\n📊 System Status During Benchmark:")
        print(f"  CPU Usage: {system_metrics['cpu_percent']:.1f}%")
        print(f"  Memory Usage: {system_metrics['memory_percent']:.1f}%")
        print(f"  ML Processes: {system_metrics['active_ml_processes']}")
        print(f"  Thermal State: {system_metrics['thermal_state']}")
        
        return benchmark_results
    
    def generate_daily_report(self, date: str = None) -> dict:
        """Generate comprehensive daily PyTorch efficiency report"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # PyTorch operations for the day
        cursor.execute('''
            SELECT COUNT(*) as total_ops, AVG(execution_time_ms) as avg_time,
                   SUM(CASE WHEN mps_acceleration = 1 THEN 1 ELSE 0 END) as mps_ops,
                   AVG(CASE WHEN mps_acceleration = 1 THEN throughput_ops_per_sec ELSE NULL END) as mps_throughput,
                   AVG(CASE WHEN mps_acceleration = 0 THEN throughput_ops_per_sec ELSE NULL END) as cpu_throughput,
                   MAX(memory_allocated_mb) as peak_memory
            FROM pytorch_metrics 
            WHERE DATE(timestamp) = ?
        ''', (date,))
        
        pytorch_stats = cursor.fetchone()
        
        # System performance during ML workloads
        cursor.execute('''
            SELECT AVG(cpu_percent) as avg_cpu, AVG(memory_percent) as avg_memory,
                   MIN(memory_available_gb) as min_memory_available,
                   AVG(active_ml_processes) as avg_ml_processes,
                   GROUP_CONCAT(DISTINCT thermal_state) as thermal_states
            FROM system_ml_metrics 
            WHERE DATE(timestamp) = ?
        ''', (date,))
        
        system_stats = cursor.fetchone()
        
        conn.close()
        
        # Calculate efficiency metrics
        mps_speedup = 0
        if pytorch_stats[4] and pytorch_stats[3]:  # cpu_throughput and mps_throughput
            mps_speedup = pytorch_stats[3] / pytorch_stats[4]
        
        neural_engine_utilization = (pytorch_stats[2] / pytorch_stats[0] * 100) if pytorch_stats[0] > 0 else 0
        
        # Generate optimization suggestions
        suggestions = self.generate_optimization_suggestions(pytorch_stats, system_stats)
        
        report = {
            'date': date,
            'version': self.version,
            'pytorch_performance': {
                'total_operations': pytorch_stats[0] or 0,
                'avg_execution_time_ms': pytorch_stats[1] or 0,
                'mps_operations': pytorch_stats[2] or 0,
                'mps_speedup': mps_speedup,
                'peak_memory_mb': pytorch_stats[5] or 0,
                'neural_engine_utilization_percent': neural_engine_utilization
            },
            'system_performance': {
                'avg_cpu_percent': system_stats[0] or 0,
                'avg_memory_percent': system_stats[1] or 0,
                'min_memory_available_gb': system_stats[2] or 0,
                'avg_ml_processes': system_stats[3] or 0,
                'thermal_issues': 'throttling' in (system_stats[4] or '')
            },
            'optimization_suggestions': suggestions,
            'overall_efficiency_score': self.calculate_efficiency_score(pytorch_stats, system_stats),
            'generated_at': datetime.now().isoformat()
        }
        
        return report
    
    def generate_optimization_suggestions(self, pytorch_stats, system_stats) -> list:
        """Generate PyTorch-specific optimization suggestions"""
        suggestions = []
        
        # PyTorch performance suggestions
        if pytorch_stats[0] > 0:  # If operations were recorded
            mps_ratio = (pytorch_stats[2] / pytorch_stats[0]) if pytorch_stats[0] > 0 else 0
            
            if mps_ratio < 0.5:
                suggestions.append("Consider using .to('mps') for tensor operations to leverage Neural Engine")
            
            if pytorch_stats[1] and pytorch_stats[1] > 100:  # Slow operations
                suggestions.append("Operations are slow - consider batch processing or tensor optimization")
            
            if pytorch_stats[5] and pytorch_stats[5] > 8000:  # High memory usage
                suggestions.append("High GPU memory usage - consider reducing batch size or using gradient checkpointing")
        
        # System performance suggestions
        if system_stats[0] and system_stats[0] > 85:
            suggestions.append("High CPU usage during ML workloads - consider reducing concurrent processes")
        
        if system_stats[1] and system_stats[1] > 90:
            suggestions.append("Memory pressure detected - close unused applications or restart development environment")
        
        if system_stats[2] and system_stats[2] < 2:
            suggestions.append("Low available memory - consider optimizing data loading or using smaller models")
        
        # Add daily maintenance suggestion
        suggestions.append("Run daily optimization: python3 pytorch_daily_efficiency_v2.py --optimize")
        
        return suggestions
    
    def calculate_efficiency_score(self, pytorch_stats, system_stats) -> float:
        """Calculate overall efficiency score for PyTorch workloads"""
        base_score = 50.0
        
        # Neural Engine utilization bonus
        if pytorch_stats[0] > 0:
            mps_ratio = (pytorch_stats[2] / pytorch_stats[0]) if pytorch_stats[0] > 0 else 0
            neural_bonus = mps_ratio * 30
        else:
            neural_bonus = 0
        
        # Performance bonus
        perf_bonus = 0
        if pytorch_stats[1]:  # avg execution time
            if pytorch_stats[1] < 50:  # Fast operations
                perf_bonus = 15
            elif pytorch_stats[1] < 100:
                perf_bonus = 10
        
        # System efficiency
        system_penalty = 0
        if system_stats[0] and system_stats[0] > 80:  # High CPU
            system_penalty += 10
        if system_stats[1] and system_stats[1] > 85:  # High memory
            system_penalty += 10
        
        efficiency_score = base_score + neural_bonus + perf_bonus - system_penalty
        return max(0, min(100, efficiency_score))
    
    def print_status_report(self):
        """Print current status and recent performance"""
        print("\n📊 PyTorch Efficiency Status")
        print("=" * 40)
        
        report = self.generate_daily_report()
        
        print(f"Date: {report['date']}")
        print(f"Overall Efficiency: {report['overall_efficiency_score']:.1f}/100")
        print(f"Neural Engine Utilization: {report['pytorch_performance']['neural_engine_utilization_percent']:.1f}%")
        print(f"PyTorch Operations: {report['pytorch_performance']['total_operations']}")
        
        if report['pytorch_performance']['mps_speedup'] > 1:
            print(f"MPS Speedup: {report['pytorch_performance']['mps_speedup']:.1f}x")
        
        if report['optimization_suggestions']:
            print("\n💡 Top Suggestions:")
            for suggestion in report['optimization_suggestions'][:3]:
                print(f"  • {suggestion}")


def main():
    """Main CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='PyTorch Daily Efficiency Reporter v2.0')
    parser.add_argument('--benchmark', action='store_true', help='Run comprehensive benchmark')
    parser.add_argument('--report', type=str, help='Generate report for date (YYYY-MM-DD)')
    parser.add_argument('--collect', action='store_true', help='Collect current system metrics')
    parser.add_argument('--optimize', action='store_true', help='Run optimization suggestions')
    parser.add_argument('--status', action='store_true', help='Show current status')
    
    args = parser.parse_args()
    
    reporter = PyTorchDailyEfficiencyReporter()
    
    if args.benchmark:
        results = reporter.run_comprehensive_benchmark()
        print("\n✅ Benchmark completed and logged to database")
    
    elif args.collect:
        metrics = reporter.collect_system_ml_metrics()
        print("📊 System metrics collected and logged")
    
    elif args.optimize:
        report = reporter.generate_daily_report()
        print("\n🔧 Optimization Suggestions:")
        for suggestion in report['optimization_suggestions']:
            print(f"  • {suggestion}")
    
    elif args.report:
        report = reporter.generate_daily_report(args.report)
        print(f"\n📋 PyTorch Efficiency Report - {args.report}")
        print(f"Overall Efficiency: {report['overall_efficiency_score']:.1f}/100")
        print(f"PyTorch Operations: {report['pytorch_performance']['total_operations']}")
        print(f"Neural Engine Usage: {report['pytorch_performance']['neural_engine_utilization_percent']:.1f}%")
    
    elif args.status:
        reporter.print_status_report()
    
    else:
        # Default: show status
        reporter.print_status_report()


if __name__ == "__main__":
    main()