#!/usr/bin/env python3
"""
Claude Integration System
Connects PyTorch development environment with Claude's capabilities
"""

import os
import json
import time
import sqlite3
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class ClaudeIntegration:
    """Integration system connecting local PyTorch environment with Claude"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.integration_db = self.project_root / "claude_integration.db"
        self.session_log = self.project_root / "claude_sessions.log"
        
        self.init_integration_database()
        self.check_claude_availability()
        
    def init_integration_database(self):
        """Initialize Claude integration tracking database"""
        conn = sqlite3.connect(self.integration_db)
        cursor = conn.cursor()
        
        # Claude interaction sessions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS claude_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_start DATETIME DEFAULT CURRENT_TIMESTAMP,
                session_end DATETIME,
                queries_count INTEGER DEFAULT 0,
                code_generations INTEGER DEFAULT 0,
                optimizations_suggested INTEGER DEFAULT 0,
                pytorch_related BOOLEAN DEFAULT 0,
                session_type TEXT,
                efficiency_gain REAL
            )
        ''')
        
        # Code suggestions and implementations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS claude_code_suggestions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                query_text TEXT,
                suggestion_type TEXT,
                code_generated TEXT,
                language TEXT,
                framework TEXT,
                implemented BOOLEAN DEFAULT 0,
                performance_impact REAL
            )
        ''')
        
        # Optimization feedback loop
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS optimization_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                optimization_type TEXT,
                before_metrics TEXT,
                after_metrics TEXT,
                claude_suggestion TEXT,
                success_rate REAL,
                time_saved_minutes REAL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def check_claude_availability(self):
        """Check if Claude CLI is available"""
        try:
            # Check if claude command is available
            result = subprocess.run(['which', 'claude'], capture_output=True, text=True)
            self.claude_available = result.returncode == 0
            
            if self.claude_available:
                print("✅ Claude CLI detected and available")
            else:
                print("ℹ️  Claude CLI not found - using manual integration mode")
                
        except Exception as e:
            self.claude_available = False
            print(f"⚠️  Claude availability check failed: {e}")
    
    def start_claude_session(self, session_type: str = "development"):
        """Start a new Claude interaction session"""
        session_data = {
            'start_time': datetime.now().isoformat(),
            'session_type': session_type,
            'queries_count': 0,
            'code_generations': 0,
            'optimizations_suggested': 0,
            'pytorch_related': False
        }
        
        session_file = self.project_root / "current_claude_session.json"
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        # Log session start
        with open(self.session_log, 'a') as f:
            f.write(f"[{datetime.now()}] Claude session started: {session_type}\n")
        
        print(f"🤖 Claude session started: {session_type}")
        return session_data
    
    def log_claude_interaction(self, query: str, response: str = None, 
                              code_generated: bool = False, pytorch_related: bool = False):
        """Log interaction with Claude"""
        session_file = self.project_root / "current_claude_session.json"
        
        # Update current session
        if session_file.exists():
            with open(session_file, 'r') as f:
                session_data = json.load(f)
            
            session_data['queries_count'] += 1
            if code_generated:
                session_data['code_generations'] += 1
            if pytorch_related:
                session_data['pytorch_related'] = True
            
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
        
        # Log to database
        conn = sqlite3.connect(self.integration_db)
        cursor = conn.cursor()
        
        # Determine suggestion type
        suggestion_type = "code_generation" if code_generated else "consultation"
        if "optimize" in query.lower():
            suggestion_type = "optimization"
        elif "debug" in query.lower() or "error" in query.lower():
            suggestion_type = "debugging"
        elif "pytorch" in query.lower() or "tensor" in query.lower():
            suggestion_type = "pytorch_specific"
        
        cursor.execute('''
            INSERT INTO claude_code_suggestions
            (query_text, suggestion_type, code_generated, pytorch_related)
            VALUES (?, ?, ?, ?)
        ''', (query[:500], suggestion_type, code_generated, pytorch_related))
        
        conn.commit()
        conn.close()
        
        # Log to session file
        with open(self.session_log, 'a') as f:
            f.write(f"[{datetime.now()}] Query: {query[:100]}...\n")
            if response:
                f.write(f"[{datetime.now()}] Response logged\n")
    
    def suggest_claude_queries(self) -> List[str]:
        """Suggest relevant Claude queries based on current project state"""
        suggestions = []
        
        # Check recent PyTorch metrics
        try:
            from pytorch_daily_efficiency_v2 import PyTorchDailyEfficiencyReporter
            reporter = PyTorchDailyEfficiencyReporter()
            report = reporter.generate_daily_report()
            
            efficiency_score = report['overall_efficiency_score']
            pytorch_ops = report['pytorch_performance']['total_operations']
            neural_engine_usage = report['pytorch_performance']['neural_engine_utilization_percent']
            
            # Generate context-aware suggestions
            if efficiency_score < 70:
                suggestions.append("How can I optimize my PyTorch code for better performance on Apple M4?")
            
            if neural_engine_usage < 50:
                suggestions.append("What's the best way to leverage MPS acceleration in PyTorch for my workload?")
            
            if pytorch_ops < 10:
                suggestions.append("What are some good PyTorch experiments I can run to test my M4 setup?")
            
        except Exception:
            # Fallback suggestions
            suggestions = [
                "How do I optimize PyTorch performance on Apple Silicon?",
                "What are best practices for PyTorch + tinygrad development?",
                "How can I benchmark my neural network training efficiency?"
            ]
        
        # Add general development suggestions
        suggestions.extend([
            "Help me debug a PyTorch tensor shape mismatch",
            "Create a neural network architecture for my use case",
            "Optimize my PyTorch data loading pipeline",
            "How do I implement custom loss functions in PyTorch?",
            "Best practices for PyTorch model deployment"
        ])
        
        return suggestions[:5]  # Return top 5 suggestions
    
    def create_claude_prompt_template(self, context: str = "pytorch_development") -> str:
        """Create optimized prompt template for Claude interactions"""
        
        # Get current system state
        try:
            import psutil
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            system_info = f"System: Apple M4, CPU {cpu:.1f}%, Memory {memory.percent:.1f}%"
        except:
            system_info = "System: Apple M4"
        
        # Get PyTorch environment info
        try:
            import torch
            pytorch_info = f"PyTorch {torch.__version__}, MPS {'Available' if torch.backends.mps.is_available() else 'Not Available'}"
        except:
            pytorch_info = "PyTorch: Not loaded"
        
        template = f"""
Context: {context.title()} Session
Environment: {system_info}, {pytorch_info}
Project: PyTorch-tinygrad Development

Please provide concise, actionable responses optimized for:
- Apple M4 Neural Engine acceleration
- PyTorch best practices
- Performance optimization
- Practical implementation

Query: """
        
        return template
    
    def generate_efficiency_report_for_claude(self) -> str:
        """Generate a report to share with Claude for optimization suggestions"""
        try:
            from pytorch_daily_efficiency_v2 import PyTorchDailyEfficiencyReporter
            reporter = PyTorchDailyEfficiencyReporter()
            report = reporter.generate_daily_report()
            
            claude_report = f"""
PyTorch Development Efficiency Report for Claude Analysis:

PERFORMANCE METRICS:
- Overall Efficiency: {report['overall_efficiency_score']:.1f}/100
- Neural Engine Utilization: {report['pytorch_performance']['neural_engine_utilization_percent']:.1f}%
- PyTorch Operations Today: {report['pytorch_performance']['total_operations']}
- Average Execution Time: {report['pytorch_performance']['avg_execution_time_ms']:.2f}ms

SYSTEM STATUS:
- CPU Usage: {report['system_performance']['avg_cpu_percent']:.1f}%
- Memory Usage: {report['system_performance']['avg_memory_percent']:.1f}%
- Thermal Issues: {'Yes' if report['system_performance']['thermal_issues'] else 'No'}

CURRENT SUGGESTIONS:
{chr(10).join('- ' + s for s in report['optimization_suggestions'])}

Please analyze this data and provide specific optimization recommendations for my PyTorch development workflow on Apple M4.
"""
            
            return claude_report
            
        except Exception as e:
            return f"Error generating efficiency report: {e}"
    
    def end_claude_session(self):
        """End current Claude session and log results"""
        session_file = self.project_root / "current_claude_session.json"
        
        if not session_file.exists():
            print("❌ No active Claude session found")
            return
        
        with open(session_file, 'r') as f:
            session_data = json.load(f)
        
        session_end = datetime.now()
        session_start = datetime.fromisoformat(session_data['start_time'])
        duration_minutes = (session_end - session_start).total_seconds() / 60
        
        # Log to database
        conn = sqlite3.connect(self.integration_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO claude_sessions
            (session_start, session_end, queries_count, code_generations,
             pytorch_related, session_type)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            session_start, session_end,
            session_data['queries_count'],
            session_data['code_generations'],
            session_data['pytorch_related'],
            session_data['session_type']
        ))
        
        conn.commit()
        conn.close()
        
        # Clean up session file
        session_file.unlink()
        
        # Log session end
        with open(self.session_log, 'a') as f:
            f.write(f"[{session_end}] Claude session ended: {duration_minutes:.1f} minutes, {session_data['queries_count']} queries\n")
        
        print(f"✅ Claude session ended:")
        print(f"  Duration: {duration_minutes:.1f} minutes")
        print(f"  Queries: {session_data['queries_count']}")
        print(f"  Code generations: {session_data['code_generations']}")
        
        return {
            'duration_minutes': duration_minutes,
            'queries_count': session_data['queries_count'],
            'code_generations': session_data['code_generations']
        }
    
    def get_claude_integration_stats(self) -> Dict:
        """Get statistics about Claude integration usage"""
        conn = sqlite3.connect(self.integration_db)
        cursor = conn.cursor()
        
        # Session statistics
        cursor.execute('''
            SELECT COUNT(*) as total_sessions,
                   AVG((julianday(session_end) - julianday(session_start)) * 24 * 60) as avg_duration_minutes,
                   SUM(queries_count) as total_queries,
                   SUM(code_generations) as total_code_generations
            FROM claude_sessions
            WHERE session_end IS NOT NULL
        ''')
        
        session_stats = cursor.fetchone()
        
        # Recent suggestions
        cursor.execute('''
            SELECT suggestion_type, COUNT(*) as count
            FROM claude_code_suggestions
            WHERE DATE(timestamp) = DATE('now')
            GROUP BY suggestion_type
            ORDER BY count DESC
        ''')
        
        today_suggestions = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_sessions': session_stats[0] or 0,
            'avg_session_duration_minutes': session_stats[1] or 0,
            'total_queries': session_stats[2] or 0,
            'total_code_generations': session_stats[3] or 0,
            'today_suggestions': [
                {'type': row[0], 'count': row[1]} for row in today_suggestions
            ]
        }


def main():
    """CLI interface for Claude integration"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Claude Integration System')
    parser.add_argument('--start-session', type=str, help='Start Claude session with type')
    parser.add_argument('--end-session', action='store_true', help='End current Claude session')
    parser.add_argument('--log-query', type=str, help='Log a query to Claude')
    parser.add_argument('--suggestions', action='store_true', help='Get suggested Claude queries')
    parser.add_argument('--report', action='store_true', help='Generate efficiency report for Claude')
    parser.add_argument('--stats', action='store_true', help='Show Claude integration statistics')
    parser.add_argument('--template', type=str, help='Generate prompt template for context')
    
    args = parser.parse_args()
    
    integration = ClaudeIntegration()
    
    if args.start_session:
        integration.start_claude_session(args.start_session)
    
    elif args.end_session:
        result = integration.end_claude_session()
        
    elif args.log_query:
        integration.log_claude_interaction(args.log_query)
        print("✅ Query logged to Claude integration system")
    
    elif args.suggestions:
        suggestions = integration.suggest_claude_queries()
        print("\n💡 Suggested Claude Queries:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. {suggestion}")
    
    elif args.report:
        report = integration.generate_efficiency_report_for_claude()
        print("\n📊 Efficiency Report for Claude Analysis:")
        print(report)
    
    elif args.stats:
        stats = integration.get_claude_integration_stats()
        print("\n📈 Claude Integration Statistics:")
        print(f"  Total Sessions: {stats['total_sessions']}")
        print(f"  Total Queries: {stats['total_queries']}")
        print(f"  Code Generations: {stats['total_code_generations']}")
        print(f"  Avg Session Duration: {stats['avg_session_duration_minutes']:.1f} minutes")
        
        if stats['today_suggestions']:
            print("\n  Today's Query Types:")
            for suggestion in stats['today_suggestions']:
                print(f"    {suggestion['type']}: {suggestion['count']}")
    
    elif args.template:
        template = integration.create_claude_prompt_template(args.template)
        print("\n📝 Optimized Claude Prompt Template:")
        print(template)
    
    else:
        print("🤖 Claude Integration System")
        print("Commands available:")
        print("  --start-session <type>  - Start tracking Claude session")
        print("  --end-session          - End current session")
        print("  --suggestions          - Get suggested queries")
        print("  --report              - Generate efficiency report")
        print("  --stats               - Show integration statistics")


if __name__ == "__main__":
    main()