#!/usr/bin/env python3
"""
Claude Efficiency Optimizer
Automatic spellcheck and question restaging for maximum efficiency and minimal token use
Uses training data to optimize every question before sending to Claude
"""

import re
import json
import sqlite3
import sys
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from difflib import SequenceMatcher
import argparse

# Add word efficiency system to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'words'))

try:
    from word_efficiency_system import WordEfficiencyDB
    HAS_WORD_EFFICIENCY = True
except ImportError:
    HAS_WORD_EFFICIENCY = False

class ClaudeEfficiencyOptimizer:
    def __init__(self):
        self.word_db = WordEfficiencyDB() if HAS_WORD_EFFICIENCY else None
        self.replacement_db = "efficiency_replacements.db"
        self.init_replacement_database()
        self.load_replacement_rules()
        
        # Efficiency targets
        self.target_efficiency = 85.0  # Target efficiency percentage
        self.max_tokens_per_message = 150  # Optimal token count for responses
        
    def init_replacement_database(self):
        """Initialize database for storing optimized replacements"""
        conn = sqlite3.connect(self.replacement_db)
        cursor = conn.cursor()
        
        # Replacement rules table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS replacement_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inefficient_phrase TEXT UNIQUE,
                efficient_replacement TEXT,
                category TEXT,
                token_savings INTEGER,
                efficiency_gain REAL,
                usage_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Spell corrections table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS spell_corrections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                misspelled_word TEXT UNIQUE,
                correct_word TEXT,
                frequency INTEGER DEFAULT 1,
                last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Optimization history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS optimization_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_text TEXT,
                optimized_text TEXT,
                efficiency_before REAL,
                efficiency_after REAL,
                token_savings INTEGER,
                optimizations_applied TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def load_replacement_rules(self):
        """Load and populate replacement rules for maximum efficiency"""
        replacement_rules = [
            # Context-dependent verbs → Specific actions
            ("can you help", "execute", "action_specific", 2, 0.3),
            ("could you", "please", "politeness_reduction", 1, 0.2),
            ("would you mind", "", "politeness_reduction", 3, 0.4),
            ("i need you to", "", "direct_command", 3, 0.3),
            ("please help me", "execute", "direct_command", 2, 0.3),
            ("i want you to", "", "direct_command", 3, 0.3),
            
            # Vague quantifiers → Specific numbers
            ("some files", "3-5 files", "quantifier_specific", 0, 0.4),
            ("many items", "15-20 items", "quantifier_specific", 0, 0.4),
            ("a few things", "2-3 items", "quantifier_specific", 1, 0.4),
            ("several options", "4-6 options", "quantifier_specific", 0, 0.4),
            ("lots of", "25+", "quantifier_specific", 1, 0.4),
            ("tons of", "50+", "quantifier_specific", 1, 0.4),
            
            # Temporal ambiguity → Specific times
            ("later", "by 5pm", "temporal_specific", 0, 0.3),
            ("soon", "within 2 hours", "temporal_specific", 0, 0.3),
            ("eventually", "by end of day", "temporal_specific", 1, 0.3),
            ("as soon as possible", "by 3pm today", "temporal_specific", 2, 0.4),
            ("when you get a chance", "immediately", "temporal_specific", 4, 0.5),
            ("sometime", "by noon", "temporal_specific", 0, 0.3),
            
            # Subjective qualifiers → Objective criteria
            ("good enough", "meets requirements", "objective_criteria", 0, 0.3),
            ("pretty good", "acceptable", "objective_criteria", 1, 0.3),
            ("really bad", "fails criteria", "objective_criteria", 1, 0.3),
            ("much better", "15% improvement", "objective_criteria", 0, 0.4),
            ("way worse", "50% degradation", "objective_criteria", 0, 0.4),
            
            # Modal uncertainty → Definitive statements
            ("might be able to", "will", "certainty_increase", 3, 0.4),
            ("could possibly", "will", "certainty_increase", 1, 0.3),
            ("should probably", "will", "certainty_increase", 1, 0.3),
            ("i think maybe", "confirm:", "certainty_increase", 2, 0.4),
            
            # Hedge words → Direct statements
            ("sort of", "", "hedge_removal", 2, 0.2),
            ("kind of", "", "hedge_removal", 2, 0.2),
            ("basically", "", "hedge_removal", 1, 0.2),
            ("essentially", "", "hedge_removal", 1, 0.2),
            ("generally", "", "hedge_removal", 1, 0.2),
            ("mostly", "", "hedge_removal", 1, 0.2),
            
            # Verbose phrases → Concise alternatives
            ("in order to", "to", "conciseness", 2, 0.2),
            ("for the purpose of", "to", "conciseness", 3, 0.3),
            ("with regard to", "regarding", "conciseness", 2, 0.2),
            ("in the event that", "if", "conciseness", 3, 0.3),
            ("due to the fact that", "because", "conciseness", 4, 0.4),
            ("at this point in time", "now", "conciseness", 4, 0.4),
            ("in the near future", "soon", "conciseness", 3, 0.3),
            
            # Question optimization
            ("how do i", "steps to", "question_optimization", 1, 0.2),
            ("what is the best way to", "optimal method:", "question_optimization", 4, 0.4),
            ("can you explain how", "explain:", "question_optimization", 2, 0.3),
            ("i was wondering if", "", "question_optimization", 3, 0.3),
            ("would it be possible to", "can", "question_optimization", 4, 0.4),
        ]
        
        conn = sqlite3.connect(self.replacement_db)
        cursor = conn.cursor()
        
        # Insert replacement rules
        cursor.executemany('''
            INSERT OR REPLACE INTO replacement_rules 
            (inefficient_phrase, efficient_replacement, category, token_savings, efficiency_gain)
            VALUES (?, ?, ?, ?, ?)
        ''', replacement_rules)
        
        conn.commit()
        conn.close()
    
    def check_spelling(self, text: str) -> Tuple[str, List[str]]:
        """Basic spell check with common programming/tech terms"""
        corrections = []
        corrected_text = text
        
        # Common misspellings in tech contexts
        spell_corrections = {
            'recieve': 'receive',
            'occured': 'occurred',
            'seperate': 'separate',
            'definately': 'definitely',
            'responsibilty': 'responsibility',
            'accessable': 'accessible',
            'sucessful': 'successful',
            'enviroment': 'environment',
            'developement': 'development',
            'maintainance': 'maintenance',
            'performace': 'performance',
            'implmentation': 'implementation',
            'configuation': 'configuration',
            'authentification': 'authentication',
            'documention': 'documentation',
            'alot': 'a lot',
            'loose': 'lose',  # when meaning to lose something
            'its': "it's",    # when meaning "it is"
            'wont': "won't",
            'cant': "can't",
            'dont': "don't",
            'efficency': 'efficiency',
            'efficent': 'efficient',
            'implament': 'implement',
            'implamentint': 'implementing'
        }
        
        words = re.findall(r'\b\w+\b', text.lower())
        for word in words:
            if word in spell_corrections:
                corrected_text = re.sub(rf'\b{re.escape(word)}\b', spell_corrections[word], 
                                      corrected_text, flags=re.IGNORECASE)
                corrections.append(f"'{word}' → '{spell_corrections[word]}'")
        
        return corrected_text, corrections
    
    def optimize_question(self, text: str) -> Dict:
        """Comprehensive question optimization for maximum efficiency"""
        original_text = text
        optimized_text = text
        applied_optimizations = []
        
        # Step 1: Spell check
        optimized_text, spell_corrections = self.check_spelling(optimized_text)
        if spell_corrections:
            applied_optimizations.extend([f"Spell: {corr}" for corr in spell_corrections])
        
        # Step 2: Apply replacement rules
        conn = sqlite3.connect(self.replacement_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT inefficient_phrase, efficient_replacement, category, token_savings, efficiency_gain
            FROM replacement_rules
            ORDER BY token_savings DESC, efficiency_gain DESC
        ''')
        
        rules = cursor.fetchall()
        total_token_savings = 0
        
        for inefficient, efficient, category, token_savings, efficiency_gain in rules:
            pattern = re.compile(re.escape(inefficient), re.IGNORECASE)
            if pattern.search(optimized_text):
                if efficient:  # If there's a replacement
                    optimized_text = pattern.sub(efficient, optimized_text)
                    applied_optimizations.append(f"{category}: '{inefficient}' → '{efficient}'")
                else:  # If it's removal
                    optimized_text = pattern.sub('', optimized_text)
                    applied_optimizations.append(f"{category}: removed '{inefficient}'")
                
                total_token_savings += token_savings
                
                # Update usage count
                cursor.execute('''
                    UPDATE replacement_rules 
                    SET usage_count = usage_count + 1 
                    WHERE inefficient_phrase = ?
                ''', (inefficient,))
        
        # Step 3: Remove redundant words and clean up
        optimized_text = self.clean_redundant_words(optimized_text)
        
        # Step 4: Analyze efficiency improvements
        efficiency_before = 0
        efficiency_after = 0
        
        if self.word_db:
            before_analysis = self.word_db.analyze_text_efficiency(original_text)
            after_analysis = self.word_db.analyze_text_efficiency(optimized_text)
            efficiency_before = before_analysis['efficiency_percentage']
            efficiency_after = after_analysis['efficiency_percentage']
        
        # Step 5: Add structure for complex requests
        optimized_text = self.add_structure_optimization(optimized_text)
        
        # Step 6: Store optimization history
        cursor.execute('''
            INSERT INTO optimization_history 
            (original_text, optimized_text, efficiency_before, efficiency_after, 
             token_savings, optimizations_applied)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (original_text, optimized_text, efficiency_before, efficiency_after,
              total_token_savings, json.dumps(applied_optimizations)))
        
        conn.commit()
        conn.close()
        
        return {
            'original': original_text,
            'optimized': optimized_text,
            'efficiency_before': efficiency_before,
            'efficiency_after': efficiency_after,
            'efficiency_improvement': efficiency_after - efficiency_before,
            'estimated_token_savings': total_token_savings,
            'optimizations_applied': applied_optimizations,
            'character_reduction': len(original_text) - len(optimized_text),
            'readability_score': self.calculate_readability_score(optimized_text)
        }
    
    def clean_redundant_words(self, text: str) -> str:
        """Remove redundant words and phrases"""
        # Remove double spaces and clean up
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\s*,\s*,\s*', ', ', text)  # Fix double commas
        text = re.sub(r'\s*\.\s*\.\s*', '. ', text)  # Fix double periods
        
        # Remove redundant phrases
        redundant_patterns = [
            r'\bplease\s+please\b',
            r'\bthe\s+the\b',
            r'\band\s+and\b',
            r'\bof\s+of\b',
            r'\bto\s+to\b',
            r'\bthat\s+that\b'
        ]
        
        for pattern in redundant_patterns:
            text = re.sub(pattern, lambda m: m.group().split()[0], text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def add_structure_optimization(self, text: str) -> str:
        """Add structure to optimize Claude's response"""
        # Count questions or tasks
        questions = len(re.findall(r'\?', text))
        tasks = len(re.findall(r'\b(analyze|create|build|implement|fix|debug|optimize)\b', text, re.IGNORECASE))
        
        # For multiple tasks, add structure
        if questions > 1 or tasks > 1:
            if not text.startswith(('1.', '•', '-')):
                # Add brief prefix for complex requests
                text = f"Brief response: {text}"
        
        # Add conciseness request for long inputs
        if len(text) > 200:
            if not any(word in text.lower() for word in ['brief', 'concise', 'summarize', 'list only']):
                text = f"Concisely: {text}"
        
        return text
    
    def calculate_readability_score(self, text: str) -> float:
        """Calculate readability score (higher = more readable)"""
        words = len(re.findall(r'\b\w+\b', text))
        sentences = max(1, len(re.findall(r'[.!?]+', text)))
        avg_sentence_length = words / sentences
        
        # Penalize very long sentences
        if avg_sentence_length > 20:
            return max(0, 100 - (avg_sentence_length - 20) * 5)
        else:
            return min(100, 80 + (20 - avg_sentence_length) * 2)
    
    def get_optimization_stats(self) -> Dict:
        """Get statistics about optimization performance"""
        conn = sqlite3.connect(self.replacement_db)
        cursor = conn.cursor()
        
        # Get overall stats
        cursor.execute('''
            SELECT COUNT(*), AVG(efficiency_after - efficiency_before), 
                   SUM(token_savings), AVG(efficiency_after)
            FROM optimization_history
        ''')
        
        overall_stats = cursor.fetchone()
        
        # Get most used optimizations
        cursor.execute('''
            SELECT inefficient_phrase, efficient_replacement, usage_count, category
            FROM replacement_rules
            WHERE usage_count > 0
            ORDER BY usage_count DESC
            LIMIT 10
        ''')
        
        top_optimizations = cursor.fetchall()
        
        # Get recent optimizations
        cursor.execute('''
            SELECT original_text, optimized_text, efficiency_after - efficiency_before
            FROM optimization_history
            ORDER BY timestamp DESC
            LIMIT 5
        ''')
        
        recent_optimizations = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_optimizations': overall_stats[0] if overall_stats[0] else 0,
            'avg_efficiency_improvement': overall_stats[1] if overall_stats[1] else 0,
            'total_token_savings': overall_stats[2] if overall_stats[2] else 0,
            'avg_final_efficiency': overall_stats[3] if overall_stats[3] else 0,
            'top_optimizations': [
                {'phrase': opt[0], 'replacement': opt[1], 'usage': opt[2], 'category': opt[3]}
                for opt in top_optimizations
            ],
            'recent_optimizations': [
                {'original': opt[0][:50] + '...', 'optimized': opt[1][:50] + '...', 'improvement': opt[2]}
                for opt in recent_optimizations
            ]
        }
    
    def interactive_optimizer(self):
        """Interactive mode for real-time optimization"""
        print("🚀 Claude Efficiency Optimizer - Interactive Mode")
        print("=" * 60)
        print("Type your questions/requests and get optimized versions")
        print("Commands: 'stats' for statistics, 'quit' to exit")
        print("=" * 60)
        
        while True:
            try:
                user_input = input("\n📝 Enter your question/request: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                elif user_input.lower() == 'stats':
                    self.display_stats()
                    continue
                elif not user_input:
                    continue
                
                # Optimize the input
                result = self.optimize_question(user_input)
                
                # Display results
                print(f"\n📊 OPTIMIZATION RESULTS")
                print("-" * 40)
                print(f"Original:    {result['original']}")
                print(f"Optimized:   {result['optimized']}")
                print(f"")
                print(f"Efficiency:  {result['efficiency_before']:.1f}% → {result['efficiency_after']:.1f}% "
                      f"(+{result['efficiency_improvement']:.1f}%)")
                print(f"Token Savings: ~{result['estimated_token_savings']}")
                print(f"Char Reduction: {result['character_reduction']}")
                print(f"Readability: {result['readability_score']:.1f}/100")
                
                if result['optimizations_applied']:
                    print(f"\n🔧 Optimizations Applied:")
                    for opt in result['optimizations_applied']:
                        print(f"  • {opt}")
                
                # Show copy-ready optimized version
                print(f"\n📋 COPY THIS OPTIMIZED VERSION:")
                print(f"🎯 {result['optimized']}")
                
            except KeyboardInterrupt:
                print(f"\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def display_stats(self):
        """Display optimization statistics"""
        stats = self.get_optimization_stats()
        
        print(f"\n📊 OPTIMIZATION STATISTICS")
        print("=" * 50)
        print(f"Total Optimizations: {stats['total_optimizations']}")
        print(f"Avg Efficiency Gain: +{stats['avg_efficiency_improvement']:.1f}%")
        print(f"Total Token Savings: {stats['total_token_savings']}")
        print(f"Avg Final Efficiency: {stats['avg_final_efficiency']:.1f}%")
        
        if stats['top_optimizations']:
            print(f"\n🏆 MOST USED OPTIMIZATIONS:")
            for opt in stats['top_optimizations'][:5]:
                print(f"  • {opt['phrase']} → {opt['replacement']} ({opt['usage']} uses)")

def main():
    parser = argparse.ArgumentParser(description='Claude Efficiency Optimizer')
    parser.add_argument('text', nargs='?', help='Text to optimize')
    parser.add_argument('--interactive', '-i', action='store_true', 
                       help='Run in interactive mode')
    parser.add_argument('--stats', '-s', action='store_true', 
                       help='Show optimization statistics')
    
    args = parser.parse_args()
    
    optimizer = ClaudeEfficiencyOptimizer()
    
    if args.interactive:
        optimizer.interactive_optimizer()
    elif args.stats:
        optimizer.display_stats()
    elif args.text:
        result = optimizer.optimize_question(args.text)
        print(f"Optimized: {result['optimized']}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()