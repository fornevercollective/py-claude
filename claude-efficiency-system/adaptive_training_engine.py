#!/usr/bin/env python3
"""
Adaptive Training Engine for Claude Efficiency
Continuously learns from Claude interactions to expand word dataset and improve response efficiency
"""

import os
import json
import sqlite3
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import defaultdict, Counter
import threading
import hashlib

class AdaptiveTrainingEngine:
    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir or str(Path.home() / ".claude" / "projects" / "-Users-taderiscon")
        self.training_db = "adaptive_training.db"
        self.learning_rate = 0.1
        self.efficiency_threshold = 75.0
        self.init_adaptive_database()
        
        # Real-time learning metrics
        self.pattern_cache = {}
        self.efficiency_history = []
        self.word_frequency_tracker = Counter()
        
    def init_adaptive_database(self):
        """Initialize adaptive learning database"""
        conn = sqlite3.connect(self.training_db)
        cursor = conn.cursor()
        
        # Adaptive word patterns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS adaptive_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_text TEXT UNIQUE,
                pattern_type TEXT,
                efficiency_impact REAL,
                frequency_count INTEGER DEFAULT 1,
                success_rate REAL DEFAULT 0.0,
                token_impact INTEGER DEFAULT 0,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                confidence_score REAL DEFAULT 0.5
            )
        ''')
        
        # Learning sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_hash TEXT UNIQUE,
                input_text TEXT,
                output_text TEXT,
                efficiency_score REAL,
                response_time REAL,
                token_count INTEGER,
                patterns_detected TEXT,
                improvements_applied TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Dynamic replacements table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dynamic_replacements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_phrase TEXT,
                optimized_phrase TEXT,
                context_category TEXT,
                efficiency_gain REAL,
                usage_frequency INTEGER DEFAULT 1,
                effectiveness_score REAL DEFAULT 0.0,
                auto_generated BOOLEAN DEFAULT 1,
                verified BOOLEAN DEFAULT 0
            )
        ''')
        
        # Performance metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_date DATE,
                avg_efficiency REAL,
                total_optimizations INTEGER,
                token_savings INTEGER,
                response_time_improvement REAL,
                new_patterns_learned INTEGER,
                accuracy_rate REAL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def analyze_conversation_patterns(self, user_input: str, claude_output: str, response_time: float = 0) -> Dict:
        """Analyze conversation for learning opportunities"""
        session_hash = hashlib.md5(f"{user_input}{claude_output}".encode()).hexdigest()
        
        # Extract patterns from user input
        input_patterns = self.extract_efficiency_patterns(user_input)
        
        # Analyze Claude's response for efficiency indicators
        output_analysis = self.analyze_response_efficiency(claude_output)
        
        # Calculate efficiency score
        efficiency_score = self.calculate_conversation_efficiency(user_input, claude_output)
        
        # Learn from this interaction
        learning_insights = self.generate_learning_insights(user_input, claude_output, efficiency_score)
        
        # Store learning session
        conn = sqlite3.connect(self.training_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO learning_sessions 
            (session_hash, input_text, output_text, efficiency_score, response_time, 
             token_count, patterns_detected, improvements_applied)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_hash,
            user_input[:500],  # Limit storage
            claude_output[:1000],
            efficiency_score,
            response_time,
            len(user_input.split()) + len(claude_output.split()),
            json.dumps(input_patterns),
            json.dumps(learning_insights['improvements'])
        ))
        
        conn.commit()
        conn.close()
        
        # Update adaptive patterns
        self.update_adaptive_patterns(input_patterns, efficiency_score)
        
        return {
            'session_hash': session_hash,
            'efficiency_score': efficiency_score,
            'patterns_found': input_patterns,
            'learning_insights': learning_insights,
            'response_analysis': output_analysis
        }
    
    def extract_efficiency_patterns(self, text: str) -> List[Dict]:
        """Extract patterns that impact efficiency"""
        patterns = []
        
        # Pattern categories to detect
        pattern_detectors = {
            'vague_quantifiers': r'\b(some|many|few|several|various|lots|tons)\b',
            'temporal_vague': r'\b(later|soon|eventually|sometime|when you can)\b',
            'uncertainty_markers': r'\b(might|could|would|possibly|maybe|perhaps)\b',
            'politeness_excess': r'\b(please|could you|would you mind|if you don\'t mind)\b',
            'hedge_words': r'\b(sort of|kind of|basically|essentially|generally)\b',
            'context_dependent': r'\b(help|get|make|do|run|set|take|give)\b',
            'verbose_phrases': r'\b(in order to|for the purpose of|due to the fact that)\b'
        }
        
        for category, pattern in pattern_detectors.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                patterns.append({
                    'category': category,
                    'text': match.lower(),
                    'position': text.lower().find(match.lower()),
                    'context': self.get_word_context(text, match)
                })
        
        return patterns
    
    def get_word_context(self, text: str, word: str, window: int = 3) -> str:
        """Get surrounding context for a word"""
        words = text.split()
        word_index = -1
        
        for i, w in enumerate(words):
            if word.lower() in w.lower():
                word_index = i
                break
        
        if word_index == -1:
            return ""
        
        start = max(0, word_index - window)
        end = min(len(words), word_index + window + 1)
        
        return ' '.join(words[start:end])
    
    def analyze_response_efficiency(self, response: str) -> Dict:
        """Analyze Claude's response for efficiency indicators"""
        word_count = len(response.split())
        char_count = len(response)
        
        # Detect response patterns
        has_examples = bool(re.search(r'(for example|such as|like|e\.g\.)', response, re.IGNORECASE))
        has_structure = bool(re.search(r'(1\.|•|-|\n)', response))
        has_code = bool(re.search(r'(```|`[^`]+`)', response))
        verbosity_score = word_count / max(1, response.count('.'))
        
        return {
            'word_count': word_count,
            'char_count': char_count,
            'has_examples': has_examples,
            'has_structure': has_structure,
            'has_code': has_code,
            'verbosity_score': verbosity_score,
            'estimated_tokens': word_count * 1.3  # Rough token estimation
        }
    
    def calculate_conversation_efficiency(self, user_input: str, claude_output: str) -> float:
        """Calculate overall conversation efficiency"""
        # Analyze input efficiency
        input_patterns = self.extract_efficiency_patterns(user_input)
        input_inefficiency = len(input_patterns) / max(1, len(user_input.split())) * 100
        
        # Analyze output efficiency
        output_analysis = self.analyze_response_efficiency(claude_output)
        output_efficiency = min(100, 200 / max(1, output_analysis['verbosity_score']))
        
        # Combined efficiency (weighted toward input since we control that)
        combined_efficiency = (70 * (100 - input_inefficiency) + 30 * output_efficiency) / 100
        
        return max(0, min(100, combined_efficiency))
    
    def generate_learning_insights(self, user_input: str, claude_output: str, efficiency_score: float) -> Dict:
        """Generate insights for improving future interactions"""
        insights = {
            'efficiency_score': efficiency_score,
            'improvements': [],
            'new_patterns': [],
            'recommendations': []
        }
        
        # Identify specific improvements
        if efficiency_score < self.efficiency_threshold:
            patterns = self.extract_efficiency_patterns(user_input)
            
            for pattern in patterns:
                improvement = self.suggest_pattern_improvement(pattern)
                if improvement:
                    insights['improvements'].append(improvement)
        
        # Analyze response for learning opportunities
        response_analysis = self.analyze_response_efficiency(claude_output)
        
        if response_analysis['verbosity_score'] > 15:
            insights['recommendations'].append("Request more concise responses")
        
        if not response_analysis['has_structure'] and response_analysis['word_count'] > 100:
            insights['recommendations'].append("Request structured responses")
        
        # Generate new patterns if efficiency is low
        if efficiency_score < 60:
            new_patterns = self.discover_new_patterns(user_input, claude_output)
            insights['new_patterns'] = new_patterns
        
        return insights
    
    def suggest_pattern_improvement(self, pattern: Dict) -> Optional[Dict]:
        """Suggest improvements for detected patterns"""
        improvements = {
            'vague_quantifiers': {
                'some': '2-3',
                'many': '15-20',
                'few': '2-4',
                'several': '3-5',
                'lots': '25+',
                'tons': '50+'
            },
            'temporal_vague': {
                'later': 'by 5pm',
                'soon': 'within 2 hours',
                'eventually': 'by end of day',
                'sometime': 'by noon'
            },
            'uncertainty_markers': {
                'might': 'will',
                'could': 'will',
                'possibly': '',
                'maybe': '',
                'perhaps': ''
            },
            'hedge_words': {
                'sort of': '',
                'kind of': '',
                'basically': '',
                'essentially': '',
                'generally': ''
            }
        }
        
        category = pattern['category']
        text = pattern['text']
        
        if category in improvements and text in improvements[category]:
            return {
                'original': text,
                'suggested': improvements[category][text],
                'category': category,
                'context': pattern['context'],
                'confidence': 0.8
            }
        
        return None
    
    def discover_new_patterns(self, user_input: str, claude_output: str) -> List[Dict]:
        """Discover new inefficiency patterns from conversations"""
        new_patterns = []
        
        # Look for repeated phrases that correlate with low efficiency
        phrases = re.findall(r'\b\w+\s+\w+\b', user_input.lower())
        
        for phrase in phrases:
            if phrase not in self.pattern_cache:
                # This is a new phrase - analyze its efficiency impact
                pattern_info = {
                    'phrase': phrase,
                    'discovered_at': datetime.now().isoformat(),
                    'context': user_input,
                    'initial_efficiency': self.calculate_conversation_efficiency(user_input, claude_output),
                    'needs_verification': True
                }
                new_patterns.append(pattern_info)
                self.pattern_cache[phrase] = pattern_info
        
        return new_patterns
    
    def update_adaptive_patterns(self, patterns: List[Dict], efficiency_score: float):
        """Update pattern database with new learning"""
        conn = sqlite3.connect(self.training_db)
        cursor = conn.cursor()
        
        for pattern in patterns:
            # Check if pattern exists
            cursor.execute('''
                SELECT id, frequency_count, efficiency_impact, confidence_score
                FROM adaptive_patterns
                WHERE pattern_text = ? AND pattern_type = ?
            ''', (pattern['text'], pattern['category']))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing pattern
                pattern_id, freq, old_impact, old_confidence = existing
                new_freq = freq + 1
                new_impact = (old_impact * freq + (100 - efficiency_score)) / new_freq
                new_confidence = min(1.0, old_confidence + self.learning_rate)
                
                cursor.execute('''
                    UPDATE adaptive_patterns
                    SET frequency_count = ?, efficiency_impact = ?, 
                        confidence_score = ?, last_seen = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (new_freq, new_impact, new_confidence, pattern_id))
            else:
                # Insert new pattern
                cursor.execute('''
                    INSERT INTO adaptive_patterns
                    (pattern_text, pattern_type, efficiency_impact, confidence_score)
                    VALUES (?, ?, ?, ?)
                ''', (pattern['text'], pattern['category'], 100 - efficiency_score, 0.5))
        
        conn.commit()
        conn.close()
    
    def get_adaptive_recommendations(self, text: str) -> List[Dict]:
        """Get real-time recommendations based on learned patterns"""
        conn = sqlite3.connect(self.training_db)
        cursor = conn.cursor()
        
        recommendations = []
        patterns = self.extract_efficiency_patterns(text)
        
        for pattern in patterns:
            # Look for learned patterns
            cursor.execute('''
                SELECT pattern_text, efficiency_impact, confidence_score, frequency_count
                FROM adaptive_patterns
                WHERE pattern_text = ? AND pattern_type = ?
                ORDER BY confidence_score DESC
            ''', (pattern['text'], pattern['category']))
            
            result = cursor.fetchone()
            
            if result and result[2] > 0.6:  # High confidence
                # Get dynamic replacement
                cursor.execute('''
                    SELECT optimized_phrase, efficiency_gain, effectiveness_score
                    FROM dynamic_replacements
                    WHERE original_phrase = ?
                    ORDER BY effectiveness_score DESC
                    LIMIT 1
                ''', (pattern['text'],))
                
                replacement = cursor.fetchone()
                
                if replacement:
                    recommendations.append({
                        'original': pattern['text'],
                        'suggested': replacement[0],
                        'category': pattern['category'],
                        'confidence': result[2],
                        'efficiency_gain': replacement[1],
                        'usage_count': result[3]
                    })
        
        conn.close()
        return recommendations
    
    def generate_performance_report(self) -> Dict:
        """Generate adaptive learning performance report"""
        conn = sqlite3.connect(self.training_db)
        cursor = conn.cursor()
        
        # Get recent learning stats
        cursor.execute('''
            SELECT AVG(efficiency_score), COUNT(*), AVG(token_count)
            FROM learning_sessions
            WHERE timestamp > datetime('now', '-7 days')
        ''')
        
        recent_stats = cursor.fetchone()
        
        # Get pattern learning progress
        cursor.execute('''
            SELECT pattern_type, COUNT(*), AVG(confidence_score), AVG(efficiency_impact)
            FROM adaptive_patterns
            WHERE confidence_score > 0.7
            GROUP BY pattern_type
        ''')
        
        pattern_stats = cursor.fetchall()
        
        # Get top performing patterns
        cursor.execute('''
            SELECT pattern_text, pattern_type, efficiency_impact, frequency_count
            FROM adaptive_patterns
            WHERE confidence_score > 0.8
            ORDER BY efficiency_impact DESC
            LIMIT 10
        ''')
        
        top_patterns = cursor.fetchall()
        
        conn.close()
        
        return {
            'learning_period': '7 days',
            'avg_efficiency': recent_stats[0] if recent_stats[0] else 0,
            'total_sessions': recent_stats[1] if recent_stats[1] else 0,
            'avg_tokens': recent_stats[2] if recent_stats[2] else 0,
            'pattern_categories': [
                {
                    'category': stat[0],
                    'patterns_learned': stat[1],
                    'avg_confidence': stat[2],
                    'avg_impact': stat[3]
                }
                for stat in pattern_stats
            ],
            'top_efficiency_patterns': [
                {
                    'pattern': pattern[0],
                    'category': pattern[1],
                    'impact': pattern[2],
                    'frequency': pattern[3]
                }
                for pattern in top_patterns
            ],
            'learning_rate': self.learning_rate,
            'efficiency_threshold': self.efficiency_threshold
        }
    
    def continuous_learning_mode(self, claude_sessions_dir: str = None):
        """Monitor Claude sessions for continuous learning"""
        sessions_dir = claude_sessions_dir or self.data_dir
        
        print(f"🧠 Starting adaptive learning mode...")
        print(f"📁 Monitoring: {sessions_dir}")
        
        processed_files = set()
        
        while True:
            try:
                # Check for new session files
                session_files = list(Path(sessions_dir).glob("*.jsonl"))
                
                for session_file in session_files:
                    if session_file.name not in processed_files:
                        self.process_session_file(session_file)
                        processed_files.add(session_file.name)
                
                # Generate daily performance report
                if datetime.now().hour == 0 and datetime.now().minute < 5:
                    self.generate_daily_report()
                
                time.sleep(30)  # Check every 30 seconds
                
            except KeyboardInterrupt:
                print("\n🛑 Stopping adaptive learning mode")
                break
            except Exception as e:
                print(f"❌ Learning error: {e}")
                time.sleep(60)
    
    def process_session_file(self, session_file: Path):
        """Process a Claude session file for learning"""
        try:
            with open(session_file, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        if 'message' in data:
                            message = data['message']
                            if message.get('role') == 'user':
                                # Find corresponding assistant response
                                user_content = self.extract_message_content(message.get('content', []))
                                # Process for learning (simplified for this example)
                                if user_content:
                                    self.analyze_conversation_patterns(user_content, "", 0)
        except Exception as e:
            print(f"❌ Error processing {session_file}: {e}")
    
    def extract_message_content(self, content):
        """Extract text content from Claude message format"""
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            text_parts = []
            for part in content:
                if isinstance(part, dict) and part.get('type') == 'text':
                    text_parts.append(part.get('text', ''))
            return ' '.join(text_parts)
        return ''

def main():
    engine = AdaptiveTrainingEngine()
    
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "--monitor":
            engine.continuous_learning_mode()
        elif sys.argv[1] == "--report":
            report = engine.generate_performance_report()
            print(json.dumps(report, indent=2))
        elif sys.argv[1] == "--analyze":
            if len(sys.argv) > 3:
                result = engine.analyze_conversation_patterns(sys.argv[2], sys.argv[3])
                print(json.dumps(result, indent=2))
    else:
        print("Adaptive Training Engine")
        print("Usage:")
        print("  --monitor     Start continuous learning mode")
        print("  --report      Generate performance report")
        print("  --analyze 'input' 'output'  Analyze conversation")

if __name__ == "__main__":
    main()