#!/usr/bin/env python3
"""
Load inefficient words from the dont/ folder into the word efficiency database
"""

import os
import re
import sys
from pathlib import Path
from word_efficiency_system import WordEfficiencyDB

def extract_words_from_rtf(file_path):
    """Extract words from RTF file, removing RTF formatting"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Remove RTF formatting codes
        content = re.sub(r'\\[a-zA-Z]+\d*\s?', '', content)  # Remove RTF commands
        content = re.sub(r'[{}]', '', content)  # Remove braces
        content = re.sub(r'[;\d]+', '', content)  # Remove numbers and semicolons
        
        # Extract words (separated by commas, spaces, or newlines)
        words = re.findall(r'\b[a-zA-Z]+\b', content)
        
        # Filter out common RTF artifacts and single letters
        filtered_words = []
        rtf_artifacts = {'rtf', 'ansi', 'ansicpg', 'cocoartf', 'fonttbl', 'colortbl', 
                        'expandedcolortbl', 'margl', 'margr', 'vieww', 'viewh', 'viewkind',
                        'deftab', 'pard', 'pardeftab', 'partightenfactor', 'expnd', 
                        'expndtw', 'kerning', 'outl', 'strokewidth', 'strokec', 'cf',
                        'froman', 'fcharset', 'Times', 'Roman', 'red', 'green', 'blue',
                        'cssrgb', 'fs'}
        
        for word in words:
            word = word.lower().strip()
            if (len(word) > 1 and 
                word not in rtf_artifacts and 
                not word.isdigit() and
                word.isalpha()):
                filtered_words.append(word)
        
        return list(set(filtered_words))  # Remove duplicates
        
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []

def load_all_dont_words():
    """Load all words from the dont/ folder structure"""
    db = WordEfficiencyDB()
    
    dont_folder = Path(__file__).parent / "dont"
    total_words_loaded = 0
    
    # Category mappings
    category_mappings = {
        "0-words": ("general_inefficient", "General inefficient words", -0.7),
        "1-context-dependent-terms": ("context_dependent", "Context-dependent high-frequency verbs", -0.8),
        "2-ambiguous-pronouns-references": ("ambiguous_pronouns", "Ambiguous pronouns and references", -0.6),
        "3-vague-quantifiers": ("vague_quantifiers", "Vague quantity descriptors", -0.8),
        "4-subjective-qualifiers": ("subjective_qualifiers", "Opinion-based descriptors", -0.7),
        "5-temporal-ambiguity": ("temporal_ambiguity", "Unclear time references", -0.7),
        "6-modal-uncertainty": ("modal_uncertainty", "Uncertainty and modal expressions", -0.6),
        "7-hedge-words-uncertainty-markers": ("hedge_words", "Hedge words and uncertainty markers", -0.6),
        "ambiguous-polysemous": ("ambiguous_polysemous", "Words with multiple meanings", -0.8),
        "domain-specific-jargon": ("domain_jargon", "Domain-specific unclear jargon", -0.5),
        "homonyms-homophones": ("homonyms_homophones", "Sound-alike confusing words", -0.7),
        "idiomatic-expressions": ("idiomatic", "Non-literal expressions", -0.6),
        "negation-iIntensifiers": ("negation_intensifiers", "Negation and intensifier words", -0.5),
        "sarcasm-irony-markers": ("sarcasm_irony", "Sarcasm and irony markers", -0.8),
        "temporal-conditional-language": ("temporal_conditional", "Conditional temporal language", -0.7)
    }
    
    if not dont_folder.exists():
        print(f"❌ Dont folder not found: {dont_folder}")
        return
    
    print(f"🔍 Scanning for inefficient words in: {dont_folder}")
    
    for root, dirs, files in os.walk(dont_folder):
        for file in files:
            if file.endswith('.rtf'):
                file_path = Path(root) / file
                relative_path = file_path.relative_to(dont_folder)
                folder_name = relative_path.parts[0] if relative_path.parts else "unknown"
                
                # Get category info
                category_info = category_mappings.get(folder_name, 
                    ("general_inefficient", f"Words from {folder_name}", -0.5))
                
                category, description, impact = category_info
                
                print(f"📄 Processing: {file_path}")
                words = extract_words_from_rtf(file_path)
                
                if words:
                    # Add category if not exists
                    try:
                        db.bulk_insert_words(words, category, 
                                           is_efficient=False, 
                                           efficiency_impact=impact)
                        total_words_loaded += len(words)
                        print(f"   ✅ Loaded {len(words)} words into '{category}'")
                    except Exception as e:
                        print(f"   ❌ Error loading words: {e}")
                else:
                    print(f"   ⚠️  No words extracted")
    
    print(f"\n🎯 Summary:")
    print(f"Total words loaded: {total_words_loaded}")
    
    # Verify database
    print(f"\n📊 Database verification:")
    stats = db.get_category_stats()
    for stat in stats:
        print(f"  {stat['category']}: {stat['word_count']} words (impact: {stat['avg_impact']:.2f})")

if __name__ == "__main__":
    load_all_dont_words()