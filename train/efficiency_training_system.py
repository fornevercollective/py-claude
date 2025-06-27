#!/usr/bin/env python3
"""
Claude Efficiency Training System
Integrates token usage tracking with word efficiency analysis for optimized AI interactions
"""

import os
import json
import sqlite3
import glob
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path
import sys

# Add the current directory to path to import word efficiency system
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), 'words'))

try:
    from word_efficiency_system import WordEfficiencyDB
    HAS_WORD_EFFICIENCY = True
except ImportError:
    HAS_WORD_EFFICIENCY = False

class ClaudeEfficiencyTrainer:
    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir or os.path.expanduser("~/.claude/projects/-Users-taderiscon/")
        self.word_db = WordEfficiencyDB() if HAS_WORD_EFFICIENCY else None
        self.training_db = "claude_training.db"
        self.init_training_database()
        
    def init_training_database(self):
        """Initialize training database"""
        conn = sqlite3.connect(self.training_db)
        cursor = conn.cursor()
        
        # Training sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS training_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                timestamp DATETIME,
                input_tokens INTEGER,
                output_tokens INTEGER,
                efficiency_score REAL,
                inefficient_words TEXT,
                suggestions TEXT,
                user_message TEXT,
                assistant_response TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Performance metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE,
                total_tokens INTEGER,
                avg_efficiency REAL,
                improvement_rate REAL,
                top_waste_factors TEXT,
                optimizations_applied TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Learning patterns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT,
                pattern_description TEXT,
                frequency INTEGER DEFAULT 1,
                efficiency_impact REAL,
                recommended_action TEXT,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def load_claude_sessions(self):
        """Load Claude Code session data"""
        session_files = glob.glob(os.path.join(self.data_dir, "*.jsonl"))
        all_messages = []
        
        for file_path in session_files:
            try:
                with open(file_path, 'r') as f:
                    for line in f:
                        if line.strip():
                            data = json.loads(line)
                            if 'message' in data:
                                data['message']['timestamp'] = data.get('timestamp')
                                data['message']['session_file'] = os.path.basename(file_path)
                                all_messages.append(data['message'])
            except (json.JSONDecodeError, FileNotFoundError):
                continue
        
        return sorted(all_messages, key=lambda x: x.get('timestamp', ''))
    
    def analyze_conversation_efficiency(self, user_message: str, assistant_response: str):
        """Analyze efficiency of a conversation pair"""
        if not self.word_db:
            return None
            
        # Analyze user message
        user_analysis = self.word_db.analyze_text_efficiency(user_message)
        
        # Analyze assistant response (first 500 chars to avoid overwhelming analysis)
        response_preview = assistant_response[:500] if len(assistant_response) > 500 else assistant_response
        assistant_analysis = self.word_db.analyze_text_efficiency(response_preview)
        
        # Combined efficiency score
        combined_score = (user_analysis['efficiency_score'] + assistant_analysis['efficiency_score']) / 2
        
        return {
            'user_efficiency': user_analysis['efficiency_percentage'],
            'assistant_efficiency': assistant_analysis['efficiency_percentage'],
            'combined_efficiency': combined_score * 100,
            'user_inefficient_words': user_analysis['inefficient_words'],
            'assistant_inefficient_words': assistant_analysis['inefficient_words'],
            'user_suggestions': user_analysis['suggestions'],
            'assistant_suggestions': assistant_analysis['suggestions']
        }
    
    def process_training_data(self):
        """Process Claude sessions for training insights"""
        messages = self.load_claude_sessions()
        training_data = []
        
        conn = sqlite3.connect(self.training_db)
        cursor = conn.cursor()
        
        # Process conversation pairs
        user_messages = [msg for msg in messages if msg.get('role') == 'user']
        assistant_messages = [msg for msg in messages if msg.get('role') == 'assistant']
        
        for i, user_msg in enumerate(user_messages):
            # Find corresponding assistant response
            user_time = datetime.fromisoformat(user_msg.get('timestamp', '').replace('Z', '+00:00'))
            
            # Find next assistant message after this user message
            assistant_msg = None
            for asst_msg in assistant_messages:
                asst_time = datetime.fromisoformat(asst_msg.get('timestamp', '').replace('Z', '+00:00'))
                if asst_time > user_time:
                    assistant_msg = asst_msg
                    break
            
            if not assistant_msg:
                continue
                
            # Extract text content
            user_text = self.extract_text_content(user_msg.get('content', []))
            assistant_text = self.extract_text_content(assistant_msg.get('content', []))
            
            if not user_text or not assistant_text:
                continue
            
            # Get token usage
            usage = assistant_msg.get('usage', {})
            input_tokens = usage.get('input_tokens', 0)
            output_tokens = usage.get('output_tokens', 0)
            
            # Analyze efficiency
            efficiency_analysis = self.analyze_conversation_efficiency(user_text, assistant_text)
            
            if efficiency_analysis:
                # Store training session
                cursor.execute('''
                    INSERT INTO training_sessions 
                    (session_id, timestamp, input_tokens, output_tokens, efficiency_score,
                     inefficient_words, suggestions, user_message, assistant_response)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_msg.get('session_file', 'unknown'),
                    user_msg.get('timestamp'),
                    input_tokens,
                    output_tokens,
                    efficiency_analysis['combined_efficiency'],
                    json.dumps(efficiency_analysis['user_inefficient_words']),
                    json.dumps(efficiency_analysis['user_suggestions']),
                    user_text[:1000],  # Limit stored text length
                    assistant_text[:1000]
                ))
        
        conn.commit()
        conn.close()
        
        return len(user_messages)
    
    def extract_text_content(self, content):
        """Extract text from Claude message content"""
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            text_parts = []
            for part in content:
                if isinstance(part, dict) and part.get('type') == 'text':
                    text_parts.append(part.get('text', ''))
            return ' '.join(text_parts)
        return ''
    
    def generate_efficiency_report(self):
        """Generate comprehensive efficiency training report"""
        conn = sqlite3.connect(self.training_db)
        cursor = conn.cursor()
        
        # Get basic stats
        cursor.execute('''
            SELECT COUNT(*), AVG(efficiency_score), AVG(input_tokens), AVG(output_tokens),
                   MIN(efficiency_score), MAX(efficiency_score)
            FROM training_sessions
        ''')
        
        stats = cursor.fetchone()
        
        if not stats or stats[0] == 0:
            return {"error": "No training data available"}
        
        # Get efficiency trends by date
        cursor.execute('''
            SELECT DATE(timestamp) as date, AVG(efficiency_score), COUNT(*)
            FROM training_sessions
            GROUP BY DATE(timestamp)
            ORDER BY date DESC
            LIMIT 7
        ''')
        
        daily_trends = cursor.fetchall()
        
        # Get most common inefficient words
        cursor.execute('SELECT inefficient_words FROM training_sessions WHERE inefficient_words IS NOT NULL')
        all_inefficient = cursor.fetchall()
        
        word_frequency = defaultdict(int)
        for row in all_inefficient:
            try:
                words = json.loads(row[0])
                for word_data in words:
                    if isinstance(word_data, list) and len(word_data) > 0:
                        word_frequency[word_data[0]] += 1
            except (json.JSONDecodeError, TypeError):
                continue
        
        top_problematic_words = sorted(word_frequency.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Calculate improvement potential
        avg_efficiency = stats[1] if stats[1] else 0
        improvement_potential = max(0, 85 - avg_efficiency)  # Target 85% efficiency
        
        conn.close()
        
        return {
            'sessions_analyzed': stats[0],
            'average_efficiency': round(stats[1], 2) if stats[1] else 0,
            'average_input_tokens': round(stats[2], 0) if stats[2] else 0,
            'average_output_tokens': round(stats[3], 0) if stats[3] else 0,
            'efficiency_range': {
                'min': round(stats[4], 2) if stats[4] else 0,
                'max': round(stats[5], 2) if stats[5] else 0
            },
            'daily_trends': [{'date': d[0], 'efficiency': round(d[1], 2), 'sessions': d[2]} for d in daily_trends],
            'top_problematic_words': top_problematic_words,
            'improvement_potential': round(improvement_potential, 2),
            'training_recommendations': self.generate_training_recommendations(avg_efficiency, top_problematic_words)
        }
    
    def generate_training_recommendations(self, current_efficiency: float, problematic_words: list):
        """Generate personalized training recommendations"""
        recommendations = []
        
        if current_efficiency < 60:
            recommendations.extend([
                "🔴 CRITICAL: Focus on reducing vague language in requests",
                "🔴 Replace context-dependent verbs with specific actions",
                "🔴 Use exact numbers instead of 'some', 'many', 'few'"
            ])
        elif current_efficiency < 75:
            recommendations.extend([
                "🟡 MODERATE: Fine-tune question specificity",
                "🟡 Reduce subjective qualifiers like 'good', 'bad', 'better'",
                "🟡 Use definitive time references instead of 'soon', 'later'"
            ])
        else:
            recommendations.extend([
                "🟢 GOOD: Maintain current efficiency standards",
                "🟢 Focus on advanced optimization techniques",
                "🟢 Experiment with batch requests for complex tasks"
            ])
        
        # Add word-specific recommendations
        for word, frequency in problematic_words[:5]:
            recommendations.append(f"• Reduce usage of '{word}' (used {frequency} times)")
        
        return recommendations
    
    def display_training_dashboard(self):
        """Display comprehensive training dashboard"""
        print("=" * 80)
        print("🎯 CLAUDE EFFICIENCY TRAINING DASHBOARD")
        print("=" * 80)
        
        # Process latest data
        processed_count = self.process_training_data()
        print(f"📊 Processed {processed_count} conversation pairs")
        
        # Generate report
        report = self.generate_efficiency_report()
        
        if "error" in report:
            print(f"❌ {report['error']}")
            return
        
        # Display key metrics
        print(f"\n📈 TRAINING METRICS")
        print(f"Sessions Analyzed: {report['sessions_analyzed']}")
        print(f"Average Efficiency: {report['average_efficiency']:.1f}%")
        print(f"Improvement Potential: {report['improvement_potential']:.1f}%")
        print(f"Avg Tokens/Session: {report['average_input_tokens']:.0f} in, {report['average_output_tokens']:.0f} out")
        
        # Efficiency range
        eff_range = report['efficiency_range']
        print(f"Efficiency Range: {eff_range['min']:.1f}% - {eff_range['max']:.1f}%")
        
        # Daily trends
        print(f"\n📊 RECENT EFFICIENCY TRENDS")
        print("-" * 50)
        for trend in report['daily_trends']:
            print(f"{trend['date']}: {trend['efficiency']:>5.1f}% ({trend['sessions']} sessions)")
        
        # Problematic words
        if report['top_problematic_words']:
            print(f"\n⚠️  MOST PROBLEMATIC WORDS")
            print("-" * 50)
            for word, count in report['top_problematic_words'][:5]:
                print(f"'{word}': used {count} times")
        
        # Training recommendations
        print(f"\n🎯 PERSONALIZED TRAINING RECOMMENDATIONS")
        print("-" * 50)
        for rec in report['training_recommendations']:
            print(f"{rec}")
        
        # Optimization strategies
        print(f"\n🚀 ADVANCED OPTIMIZATION STRATEGIES")
        print("-" * 50)
        print("• Use context-specific vocabulary from your domain")
        print("• Batch similar requests to reduce context switching")
        print("• Pre-define complex requirements in CLAUDE.md")
        print("• Use --continue to maintain conversation efficiency")
        print("• Apply word efficiency analysis before sending requests")
        
        print("=" * 80)

def main():
    trainer = ClaudeEfficiencyTrainer()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--init-word-db":
        if trainer.word_db:
            print("Initializing word efficiency database...")
            trainer.word_db.populate_initial_data()
            print("✅ Word efficiency database initialized!")
        else:
            print("❌ Word efficiency system not available")
        return
    
    trainer.display_training_dashboard()

if __name__ == "__main__":
    main()