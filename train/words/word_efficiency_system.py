#!/usr/bin/env python3
"""
Word Efficiency Database System
Manages and visualizes words that impact AI response efficiency
"""

import sqlite3
import json
import csv
import argparse
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import re

class WordEfficiencyDB:
    def __init__(self, db_path: str = "word_efficiency.db"):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Main words table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT UNIQUE NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT,
                efficiency_impact REAL DEFAULT 0.0,
                frequency_rank INTEGER,
                is_efficient BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Categories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                impact_type TEXT CHECK(impact_type IN ('positive', 'negative', 'neutral')),
                priority_level INTEGER DEFAULT 0
            )
        ''')
        
        # Word relationships table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS word_relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word1_id INTEGER,
                word2_id INTEGER,
                relationship_type TEXT,
                strength REAL DEFAULT 1.0,
                FOREIGN KEY (word1_id) REFERENCES words (id),
                FOREIGN KEY (word2_id) REFERENCES words (id)
            )
        ''')
        
        # Analysis results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_text TEXT,
                efficiency_score REAL,
                inefficient_words TEXT,
                suggestions TEXT,
                analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_words_category ON words(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_words_efficient ON words(is_efficient)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_words_impact ON words(efficiency_impact)')
        
        conn.commit()
        conn.close()
        
    def populate_initial_data(self):
        """Populate database with the categorized word lists"""
        categories_data = [
            ("ambiguous_polysemous", "Words with multiple meanings that confuse AI", "negative", 1),
            ("homonyms_homophones", "Words that sound alike but have different meanings", "negative", 2),
            ("context_dependent", "High-frequency verbs with dozens of meanings", "negative", 1),
            ("vague_quantifiers", "Imprecise quantity descriptors", "negative", 1),
            ("subjective_qualifiers", "Opinion-based descriptors without criteria", "negative", 2),
            ("temporal_ambiguity", "Unclear time references", "negative", 2),
            ("modal_uncertainty", "Words expressing uncertainty", "negative", 1),
            ("clear_single_meaning", "Unambiguous words with precise definitions", "positive", 1),
            ("phonetically_distinct", "Words without sound-alikes", "positive", 2),
            ("context_independent", "Words maintaining consistent meaning", "positive", 1),
            ("literal_expressions", "Direct, non-figurative phrases", "positive", 2),
            ("affirmative_intensifiers", "Positive amplifiers and certainty markers", "positive", 1),
            ("universal_terms", "Cross-cultural, commonly understood words", "positive", 2),
            ("definite_temporal", "Specific time references", "positive", 1)
        ]
        
        # Inefficient words from our analysis
        inefficient_words = {
            "context_dependent": ["run", "set", "get", "make", "take", "go", "come", "put", "give", "turn", "call", "work", "play", "move", "hold", "bring", "keep", "show", "try", "use", "find", "know", "think", "say", "tell", "ask", "look", "seem", "feel", "leave"],
            "vague_quantifiers": ["some", "many", "few", "several", "various", "numerous", "multiple", "countless", "tons", "loads", "lots", "plenty", "enough", "sufficient", "adequate", "barely", "hardly", "scarcely"],
            "subjective_qualifiers": ["good", "bad", "better", "worse", "best", "worst", "great", "terrible", "excellent", "awful", "amazing", "horrible", "wonderful", "dreadful", "fantastic", "pathetic"],
            "temporal_ambiguity": ["soon", "later", "eventually", "ultimately", "finally", "recently", "lately", "currently", "presently", "early", "late", "delayed", "ahead", "behind"],
            "modal_uncertainty": ["might", "could", "would", "should", "may", "can", "must", "shall", "will", "ought", "supposed to", "expected to", "likely", "unlikely", "possible", "impossible"]
        }
        
        # Efficient words from our analysis
        efficient_words = {
            "clear_single_meaning": ["accelerate", "amplify", "architect", "binary", "calculate", "calibrate", "construct", "crystallize", "decode", "diagram", "duplicate", "eliminate", "engineer", "execute"],
            "phonetically_distinct": ["accumulate", "bachelor", "cathedral", "distinguish", "elephant", "fluorescent", "gymnasium", "helicopter", "illuminate", "jeopardize", "kaleidoscope", "laboratory"],
            "context_independent": ["breathe", "calculate", "photograph", "sleep", "eat", "drink", "walk", "sit", "stand", "jump", "swim", "fly", "drive", "read", "write", "listen", "watch"],
            "affirmative_intensifiers": ["very", "extremely", "highly", "incredibly", "remarkably", "exceptionally", "extraordinarily", "tremendously", "immensely", "enormously", "significantly"],
            "definite_temporal": ["now", "immediately", "instantly", "promptly", "quickly", "today", "tomorrow", "yesterday", "Monday", "Tuesday", "Wednesday", "January", "February", "2024", "2025"]
        }
        
        self.bulk_insert_categories(categories_data)
        
        # Insert inefficient words
        for category, words in inefficient_words.items():
            self.bulk_insert_words(words, category, is_efficient=False, efficiency_impact=-0.8)
            
        # Insert efficient words
        for category, words in efficient_words.items():
            self.bulk_insert_words(words, category, is_efficient=True, efficiency_impact=0.8)
    
    def bulk_insert_categories(self, categories: List[Tuple]):
        """Insert multiple categories"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.executemany('''
            INSERT OR IGNORE INTO categories (name, description, impact_type, priority_level)
            VALUES (?, ?, ?, ?)
        ''', categories)
        
        conn.commit()
        conn.close()
    
    def bulk_insert_words(self, words: List[str], category: str, subcategory: str = None, 
                         is_efficient: bool = True, efficiency_impact: float = 0.0):
        """Insert multiple words into database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        word_data = [(word.strip().lower(), category, subcategory, efficiency_impact, is_efficient) 
                     for word in words if word.strip()]
        
        cursor.executemany('''
            INSERT OR IGNORE INTO words (word, category, subcategory, efficiency_impact, is_efficient)
            VALUES (?, ?, ?, ?, ?)
        ''', word_data)
        
        conn.commit()
        conn.close()
    
    def analyze_text_efficiency(self, text: str) -> Dict:
        """Analyze text for efficiency-impacting words"""
        words = re.findall(r'\b\w+\b', text.lower())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Find inefficient words in text
        placeholders = ','.join(['?' for _ in words])
        cursor.execute(f'''
            SELECT word, category, efficiency_impact 
            FROM words 
            WHERE word IN ({placeholders}) AND is_efficient = 0
        ''', words)
        
        inefficient_matches = cursor.fetchall()
        
        # Calculate efficiency score
        total_words = len(words)
        inefficient_count = len(inefficient_matches)
        efficiency_score = max(0, (total_words - inefficient_count) / total_words) if total_words > 0 else 1.0
        
        # Generate suggestions
        suggestions = []
        for word, category, impact in inefficient_matches:
            if category == "context_dependent":
                suggestions.append(f"Replace '{word}' with more specific action verb")
            elif category == "vague_quantifiers":
                suggestions.append(f"Replace '{word}' with exact number or measurement")
            elif category == "subjective_qualifiers":
                suggestions.append(f"Replace '{word}' with objective criteria or metrics")
            elif category == "temporal_ambiguity":
                suggestions.append(f"Replace '{word}' with specific date/time")
            elif category == "modal_uncertainty":
                suggestions.append(f"Replace '{word}' with definitive statement")
        
        result = {
            'text': text,
            'total_words': total_words,
            'inefficient_words': inefficient_matches,
            'efficiency_score': efficiency_score,
            'efficiency_percentage': efficiency_score * 100,
            'suggestions': suggestions
        }
        
        # Store analysis result
        cursor.execute('''
            INSERT INTO analysis_results (query_text, efficiency_score, inefficient_words, suggestions)
            VALUES (?, ?, ?, ?)
        ''', (text, efficiency_score, json.dumps(inefficient_matches), json.dumps(suggestions)))
        
        conn.commit()
        conn.close()
        
        return result
    
    def get_category_stats(self) -> List[Dict]:
        """Get statistics by category"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT c.name, c.description, c.impact_type, 
                   COUNT(w.id) as word_count,
                   AVG(w.efficiency_impact) as avg_impact
            FROM categories c
            LEFT JOIN words w ON c.name = w.category
            GROUP BY c.name, c.description, c.impact_type
            ORDER BY c.priority_level, c.name
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        return [{'category': r[0], 'description': r[1], 'impact_type': r[2], 
                'word_count': r[3], 'avg_impact': r[4]} for r in results]
    
    def search_words(self, pattern: str, category: str = None, is_efficient: bool = None) -> List[Dict]:
        """Search words with optional filters"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT word, category, subcategory, efficiency_impact, is_efficient FROM words WHERE word LIKE ?"
        params = [f"%{pattern}%"]
        
        if category:
            query += " AND category = ?"
            params.append(category)
            
        if is_efficient is not None:
            query += " AND is_efficient = ?"
            params.append(is_efficient)
            
        query += " ORDER BY word"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        return [{'word': r[0], 'category': r[1], 'subcategory': r[2], 
                'efficiency_impact': r[3], 'is_efficient': bool(r[4])} for r in results]
    
    def export_data(self, format_type: str, filename: str = None):
        """Export data in various formats"""
        conn = sqlite3.connect(self.db_path)
        
        if format_type.lower() == 'csv':
            df = sqlite3.read_sql_query("SELECT * FROM words ORDER BY category, word", conn)
            filename = filename or f"word_efficiency_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(filename, index=False)
            
        elif format_type.lower() == 'json':
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM words ORDER BY category, word")
            words = cursor.fetchall()
            
            export_data = {
                'export_date': datetime.now().isoformat(),
                'total_words': len(words),
                'words': [{'word': w[1], 'category': w[2], 'subcategory': w[3], 
                          'efficiency_impact': w[4], 'is_efficient': bool(w[6])} for w in words]
            }
            
            filename = filename or f"word_efficiency_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2)
        
        conn.close()
        return filename
    
    def get_efficiency_recommendations(self, target_percentage: float = 80.0) -> Dict:
        """Get recommendations to achieve target efficiency"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get most impactful inefficient words
        cursor.execute('''
            SELECT word, category, efficiency_impact
            FROM words 
            WHERE is_efficient = 0 
            ORDER BY efficiency_impact ASC, word
            LIMIT 50
        ''')
        
        top_inefficient = cursor.fetchall()
        
        # Get alternative efficient words
        cursor.execute('''
            SELECT word, category, efficiency_impact
            FROM words 
            WHERE is_efficient = 1 
            ORDER BY efficiency_impact DESC, word
            LIMIT 100
        ''')
        
        top_efficient = cursor.fetchall()
        
        conn.close()
        
        return {
            'target_efficiency': target_percentage,
            'words_to_avoid': [{'word': w[0], 'category': w[1], 'impact': w[2]} for w in top_inefficient],
            'recommended_alternatives': [{'word': w[0], 'category': w[1], 'impact': w[2]} for w in top_efficient],
            'strategy': [
                "Replace context-dependent verbs with specific action words",
                "Use exact numbers instead of vague quantifiers",
                "Replace subjective qualifiers with measurable criteria",
                "Specify exact times instead of temporal ambiguity",
                "Use definitive statements instead of modal uncertainty"
            ]
        }


class WordEfficiencyCLI:
    def __init__(self):
        self.db = WordEfficiencyDB()
        
    def run(self):
        parser = argparse.ArgumentParser(description='Word Efficiency Database Management')
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Initialize command
        init_parser = subparsers.add_parser('init', help='Initialize database with default data')
        
        # Analyze command
        analyze_parser = subparsers.add_parser('analyze', help='Analyze text efficiency')
        analyze_parser.add_argument('text', help='Text to analyze')
        analyze_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
        
        # Search command
        search_parser = subparsers.add_parser('search', help='Search words')
        search_parser.add_argument('pattern', help='Search pattern')
        search_parser.add_argument('--category', '-c', help='Filter by category')
        search_parser.add_argument('--efficient', action='store_true', help='Show only efficient words')
        search_parser.add_argument('--inefficient', action='store_true', help='Show only inefficient words')
        
        # Stats command
        stats_parser = subparsers.add_parser('stats', help='Show category statistics')
        
        # Export command
        export_parser = subparsers.add_parser('export', help='Export data')
        export_parser.add_argument('format', choices=['csv', 'json'], help='Export format')
        export_parser.add_argument('--output', '-o', help='Output filename')
        
        # Recommendations command
        rec_parser = subparsers.add_parser('recommend', help='Get efficiency recommendations')
        rec_parser.add_argument('--target', '-t', type=float, default=80.0, help='Target efficiency percentage')
        
        # Add words command
        add_parser = subparsers.add_parser('add', help='Add words to database')
        add_parser.add_argument('words', nargs='+', help='Words to add')
        add_parser.add_argument('--category', '-c', required=True, help='Category for words')
        add_parser.add_argument('--efficient', action='store_true', help='Mark as efficient words')
        add_parser.add_argument('--impact', type=float, default=0.0, help='Efficiency impact score')
        
        args = parser.parse_args()
        
        if not args.command:
            parser.print_help()
            return
            
        if args.command == 'init':
            self.init_database()
        elif args.command == 'analyze':
            self.analyze_text(args.text, args.verbose)
        elif args.command == 'search':
            self.search_words(args.pattern, args.category, args.efficient, args.inefficient)
        elif args.command == 'stats':
            self.show_stats()
        elif args.command == 'export':
            self.export_data(args.format, args.output)
        elif args.command == 'recommend':
            self.show_recommendations(args.target)
        elif args.command == 'add':
            self.add_words(args.words, args.category, args.efficient, args.impact)
    
    def init_database(self):
        print("Initializing database with default word categories...")
        self.db.populate_initial_data()
        print("✅ Database initialized successfully!")
        
    def analyze_text(self, text: str, verbose: bool = False):
        print(f"Analyzing text efficiency...")
        print(f"Input: '{text}'")
        print("-" * 50)
        
        result = self.db.analyze_text_efficiency(text)
        
        print(f"📊 Efficiency Score: {result['efficiency_percentage']:.1f}%")
        print(f"📝 Total Words: {result['total_words']}")
        print(f"⚠️  Inefficient Words Found: {len(result['inefficient_words'])}")
        
        if result['inefficient_words']:
            print("\n🔍 Problematic Words:")
            for word, category, impact in result['inefficient_words']:
                print(f"  • '{word}' ({category}, impact: {impact})")
        
        if result['suggestions']:
            print("\n💡 Suggestions:")
            for suggestion in result['suggestions']:
                print(f"  • {suggestion}")
        
        if verbose:
            print(f"\n📈 Detailed Analysis:")
            print(f"  Raw efficiency score: {result['efficiency_score']:.4f}")
            print(f"  Words analyzed: {', '.join([w[0] for w in result['inefficient_words']])}")
    
    def search_words(self, pattern: str, category: str = None, efficient: bool = False, inefficient: bool = False):
        is_efficient = None
        if efficient:
            is_efficient = True
        elif inefficient:
            is_efficient = False
            
        results = self.db.search_words(pattern, category, is_efficient)
        
        print(f"🔍 Search results for '{pattern}':")
        print("-" * 50)
        
        if not results:
            print("No words found matching your criteria.")
            return
            
        for word_data in results:
            status = "✅ Efficient" if word_data['is_efficient'] else "❌ Inefficient"
            print(f"{word_data['word']:20} | {word_data['category']:20} | {status:15} | Impact: {word_data['efficiency_impact']:6.2f}")
    
    def show_stats(self):
        stats = self.db.get_category_stats()
        
        print("📊 Category Statistics:")
        print("-" * 80)
        print(f"{'Category':25} | {'Type':10} | {'Words':8} | {'Avg Impact':12} | {'Description'}")
        print("-" * 80)
        
        for stat in stats:
            impact_icon = "✅" if stat['impact_type'] == 'positive' else "❌" if stat['impact_type'] == 'negative' else "⚪"
            print(f"{stat['category']:25} | {impact_icon} {stat['impact_type']:8} | {stat['word_count']:8} | {stat['avg_impact']:12.3f} | {stat['description']}")
    
    def export_data(self, format_type: str, output: str = None):
        filename = self.db.export_data(format_type, output)
        print(f"✅ Data exported to: {filename}")
    
    def show_recommendations(self, target: float):
        recommendations = self.db.get_efficiency_recommendations(target)
        
        print(f"🎯 Recommendations for {target}% efficiency:")
        print("=" * 60)
        
        print(f"\n❌ Top words to avoid:")
        for word in recommendations['words_to_avoid'][:10]:
            print(f"  • '{word['word']}' ({word['category']}, impact: {word['impact']:.2f})")
        
        print(f"\n✅ Recommended alternatives:")
        for word in recommendations['recommended_alternatives'][:10]:
            print(f"  • '{word['word']}' ({word['category']}, impact: {word['impact']:.2f})")
        
        print(f"\n💡 Strategy:")
        for strategy in recommendations['strategy']:
            print(f"  • {strategy}")
    
    def add_words(self, words: List[str], category: str, efficient: bool, impact: float):
        self.db.bulk_insert_words(words, category, is_efficient=efficient, efficiency_impact=impact)
        status = "efficient" if efficient else "inefficient"
        print(f"✅ Added {len(words)} {status} words to category '{category}'")


if __name__ == "__main__":
    cli = WordEfficiencyCLI()
    cli.run()
