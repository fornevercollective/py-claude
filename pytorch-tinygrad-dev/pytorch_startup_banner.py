#!/usr/bin/env python3
"""
PyTorch Startup Banner System
Custom banners for PyTorch-tinygrad development environment
"""

import time
import random
from datetime import datetime

class PyTorchStartupBanner:
    """Dynamic startup banner system for PyTorch development environment"""
    
    def __init__(self):
        self.current_time = datetime.now()
        self.greeting = self.get_time_based_greeting()
        
    def get_time_based_greeting(self):
        """Get appropriate greeting based on time of day"""
        hour = self.current_time.hour
        
        if 5 <= hour < 12:
            return "Good Morning"
        elif 12 <= hour < 17:
            return "Good Afternoon"
        elif 17 <= hour < 21:
            return "Good Evening"
        else:
            return "Working Late"
    
    def pytorch_banner(self):
        """Main PyTorch development banner"""
        return f"""
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
║                   🧠 {self.greeting}, Developer! 🚀                          ║
║                                                                              ║
║     ⚡ Apple M4 Neural Engine + Metal Performance Shaders Ready             ║
║     🔬 PyTorch + tinygrad Development Environment Active                    ║
║     📊 Efficiency Monitoring System Online                                  ║
║                                                                              ║
║                   Time: {self.current_time.strftime('%H:%M:%S')} | Date: {self.current_time.strftime('%Y-%m-%d')}                    ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
    
    def show_banner(self):
        """Display the PyTorch banner with animation"""
        banner = self.pytorch_banner()
        
        # Simple animation effect
        lines = banner.split('\n')
        for line in lines:
            print(line)
            time.sleep(0.05)  # Small delay for animation effect
        
        # Add system status
        self.show_system_status()
    
    def show_system_status(self):
        """Show quick system status after banner"""
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            
            print(f"\n🖥️  System Status: CPU {cpu:.1f}% | Memory {memory.percent:.1f}% | Available {memory.available / (1024**3):.1f}GB")
        except ImportError:
            print("\n🖥️  System Status: Monitoring tools not available")
        
        try:
            import torch
            if torch.backends.mps.is_available():
                print("⚡ Neural Engine: Ready for acceleration")
            else:
                print("💻 CPU Mode: Neural Engine not available")
        except ImportError:
            print("🔧 PyTorch: Not installed")
        
        print("-" * 80)


def main():
    """Display PyTorch startup banner"""
    banner = PyTorchStartupBanner()
    banner.show_banner()


if __name__ == "__main__":
    main()