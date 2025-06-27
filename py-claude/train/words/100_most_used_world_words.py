#!/usr/bin/env python3
"""
100 Most Used Words in the World
Based on comprehensive corpus analysis of English language usage
"""

# Top 100 most frequently used words in English worldwide
MOST_USED_WORDS = [
    'the', 'of', 'and', 'a', 'to', 'in', 'is', 'you', 'that', 'it',
    'he', 'was', 'for', 'on', 'are', 'as', 'with', 'his', 'they', 'i',
    'at', 'be', 'this', 'have', 'from', 'or', 'one', 'had', 'by', 'word',
    'but', 'not', 'what', 'all', 'were', 'we', 'when', 'your', 'can', 'said',
    'there', 'each', 'which', 'she', 'do', 'how', 'their', 'if', 'will', 'up',
    'other', 'about', 'out', 'many', 'then', 'them', 'these', 'so', 'some', 'her',
    'would', 'make', 'like', 'into', 'him', 'has', 'two', 'more', 'very', 'what',
    'know', 'just', 'first', 'get', 'over', 'think', 'also', 'your', 'work', 'life',
    'only', 'new', 'years', 'way', 'may', 'say', 'come', 'its', 'now', 'long',
    'find', 'here', 'between', 'name', 'should', 'home', 'big', 'give', 'air', 'line'
]

# Categorized analysis of the top 100 words
WORD_CATEGORIES = {
    'articles': ['the', 'a'],
    'prepositions': ['of', 'to', 'in', 'for', 'on', 'as', 'with', 'at', 'from', 'by', 'about', 'out', 'into', 'over', 'between'],
    'pronouns': ['you', 'that', 'it', 'he', 'his', 'they', 'i', 'this', 'we', 'your', 'she', 'their', 'them', 'these', 'her', 'him', 'its'],
    'conjunctions': ['and', 'or', 'but'],
    'verbs': ['is', 'was', 'are', 'be', 'have', 'had', 'can', 'said', 'do', 'will', 'would', 'make', 'has', 'get', 'think', 'work', 'may', 'say', 'come', 'find', 'should', 'give'],
    'adjectives': ['all', 'other', 'many', 'some', 'two', 'more', 'very', 'first', 'only', 'new', 'long', 'big'],
    'adverbs': ['when', 'how', 'then', 'so', 'just', 'also', 'now', 'here'],
    'nouns': ['word', 'years', 'way', 'life', 'name', 'home', 'air', 'line'],
    'question_words': ['what', 'which', 'how', 'when'],
    'negation': ['not'],
    'particles': ['up']
}

# Efficiency impact analysis
EFFICIENCY_IMPACT = {
    'high_inefficiency': {
        'words': ['some', 'many', 'very', 'big', 'get', 'make', 'do', 'work', 'way', 'thing', 'good', 'bad'],
        'impact_score': -0.8,
        'reason': 'Vague, context-dependent, or subjective'
    },
    'medium_inefficiency': {
        'words': ['it', 'this', 'that', 'they', 'them', 'these', 'other', 'all', 'more', 'think', 'know', 'like'],
        'impact_score': -0.5,
        'reason': 'Ambiguous references or require clarification'
    },
    'neutral': {
        'words': ['the', 'of', 'and', 'a', 'to', 'in', 'is', 'you', 'he', 'was', 'for', 'on', 'are', 'as', 'with'],
        'impact_score': 0.0,
        'reason': 'Necessary function words'
    },
    'low_inefficiency': {
        'words': ['when', 'where', 'how', 'what', 'which', 'who', 'why', 'first', 'new', 'long', 'two'],
        'impact_score': -0.2,
        'reason': 'Can be made more specific but generally acceptable'
    }
}

# Efficient alternatives for high-impact inefficient words
EFFICIENT_ALTERNATIVES = {
    'some': ['47', 'multiple', 'several', 'numerous', 'specific_quantity'],
    'many': ['127', 'numerous', 'multiple', 'substantial_number'],
    'very': ['extremely', 'significantly', 'substantially', 'remarkably'],
    'big': ['large', 'enormous', 'massive', '50_meters', 'substantial'],
    'get': ['obtain', 'acquire', 'retrieve', 'download', 'receive'],
    'make': ['create', 'manufacture', 'produce', 'construct', 'generate'],
    'do': ['execute', 'perform', 'complete', 'accomplish', 'implement'],
    'work': ['function', 'operate', 'employment', 'task', 'project'],
    'way': ['method', 'approach', 'technique', 'procedure', 'strategy'],
    'thing': ['object', 'item', 'component', 'element', 'device'],
    'good': ['excellent', 'optimal', 'superior', 'effective', 'high_quality'],
    'bad': ['defective', 'suboptimal', 'ineffective', 'poor_quality', 'malfunctioning']
}

class WordFrequencyAnalyzer:
    def __init__(self):
        self.most_used = MOST_USED_WORDS
        self.categories = WORD_CATEGORIES
        self.efficiency_impact = EFFICIENCY_IMPACT
        self.alternatives = EFFICIENT_ALTERNATIVES
    
    def get_word_rank(self, word: str) -> int:
        """Get the frequency rank of a word (1-100, or 0 if not in top 100)"""
        word_lower = word.lower()
        try:
            return self.most_used.index(word_lower) + 1
        except ValueError:
            return 0
    
    def get_word_category(self, word: str) -> str:
        """Get the grammatical category of a word"""
        word_lower = word.lower()
        for category, words in self.categories.items():
            if word_lower in words:
                return category
        return 'unknown'
    
    def get_efficiency_impact(self, word: str) -> dict:
        """Get the efficiency impact of a word"""
        word_lower = word.lower()
        for impact_level, data in self.efficiency_impact.items():
            if word_lower in data['words']:
                return {
                    'level': impact_level,
                    'score': data['impact_score'],
                    'reason': data['reason']
                }
        return {
            'level': 'neutral',
            'score': 0.0,
            'reason': 'Standard function word'
        }
    
    def get_efficient_alternatives(self, word: str) -> list:
        """Get efficient alternatives for inefficient words"""
        word_lower = word.lower()
        return self.alternatives.get(word_lower, [])
    
    def analyze_text(self, text: str) -> dict:
        """Analyze text for high-frequency word usage and efficiency"""
        words = text.lower().split()
        
        analysis = {
            'total_words': len(words),
            'top_100_words': 0,
            'high_inefficiency_words': [],
            'medium_inefficiency_words': [],
            'efficiency_score': 0,
            'suggestions': []
        }
        
        inefficiency_penalty = 0
        
        for word in words:
            # Clean word (remove punctuation)
            clean_word = ''.join(c for c in word if c.isalpha())
            
            if clean_word in self.most_used:
                analysis['top_100_words'] += 1
                
                impact = self.get_efficiency_impact(clean_word)
                
                if impact['level'] == 'high_inefficiency':
                    analysis['high_inefficiency_words'].append(clean_word)
                    inefficiency_penalty += 0.8
                    
                    alternatives = self.get_efficient_alternatives(clean_word)
                    if alternatives:
                        analysis['suggestions'].append(f"Replace '{clean_word}' with: {', '.join(alternatives[:3])}")
                
                elif impact['level'] == 'medium_inefficiency':
                    analysis['medium_inefficiency_words'].append(clean_word)
                    inefficiency_penalty += 0.5
        
        # Calculate efficiency score (0-100)
        if analysis['total_words'] > 0:
            base_score = 70  # Base score for using common words
            penalty = (inefficiency_penalty / analysis['total_words']) * 100
            analysis['efficiency_score'] = max(0, base_score - penalty)
        
        return analysis
    
    def get_statistics(self) -> dict:
        """Get statistics about the word categories"""
        stats = {
            'total_words': len(self.most_used),
            'category_breakdown': {},
            'efficiency_breakdown': {}
        }
        
        # Category breakdown
        for category, words in self.categories.items():
            stats['category_breakdown'][category] = len(words)
        
        # Efficiency breakdown
        for level, data in self.efficiency_impact.items():
            stats['efficiency_breakdown'][level] = len(data['words'])
        
        return stats
    
    def print_analysis_report(self, text: str):
        """Print a comprehensive analysis report"""
        print("WORD FREQUENCY ANALYSIS REPORT")
        print("=" * 50)
        
        analysis = self.analyze_text(text)
        
        print(f"Text: '{text}'")
        print(f"Total words: {analysis['total_words']}")
        print(f"Top-100 words used: {analysis['top_100_words']} ({analysis['top_100_words']/analysis['total_words']*100:.1f}%)")
        print(f"Efficiency score: {analysis['efficiency_score']:.1f}/100")
        
        if analysis['high_inefficiency_words']:
            print(f"\n⚠️  High inefficiency words: {set(analysis['high_inefficiency_words'])}")
        
        if analysis['medium_inefficiency_words']:
            print(f"⚡ Medium inefficiency words: {set(analysis['medium_inefficiency_words'])}")
        
        if analysis['suggestions']:
            print(f"\n💡 Suggestions:")
            for suggestion in analysis['suggestions']:
                print(f"  • {suggestion}")
        
        if analysis['efficiency_score'] >= 80:
            print(f"\n✅ Excellent efficiency! Text is optimized for AI responses.")
        elif analysis['efficiency_score'] >= 60:
            print(f"\n⚠️  Good efficiency. Consider implementing suggestions for improvement.")
        else:
            print(f"\n❌ Low efficiency. Significant improvements needed for optimal AI responses.")

def print_word_categories():
    """Print categorized breakdown of top 100 words"""
    print("TOP 100 WORDS BY CATEGORY")
    print("=" * 50)
    
    for category, words in WORD_CATEGORIES.items():
        print(f"\n{category.upper().replace('_', ' ')} ({len(words)} words):")
        print(", ".join(words))

def print_efficiency_analysis():
    """Print efficiency impact analysis"""
    print("\nEFFICIENCY IMPACT ANALYSIS")
    print("=" * 50)
    
    for level, data in EFFICIENCY_IMPACT.items():
        print(f"\n{level.upper().replace('_', ' ')} (Impact: {data['impact_score']})")
        print(f"Reason: {data['reason']}")
        print(f"Words: {', '.join(data['words'])}")

def main():
    """Main function for testing and demonstration"""
    analyzer = WordFrequencyAnalyzer()
    
    # Print basic information
    print("100 MOST USED WORDS IN THE WORLD")
    print("=" * 50)
    print(f"Total words: {len(MOST_USED_WORDS)}")
    print(f"Words: {', '.join(MOST_USED_WORDS)}")
    
    # Print categorized breakdown
    print_word_categories()
    
    # Print efficiency analysis
    print_efficiency_analysis()
    
    # Test text analysis
    test_texts = [
        "I think we should probably try to do some good work on this big thing soon.",
        "Execute the algorithm to calculate precise measurements using calibrated instruments.",
        "The quick brown fox jumps over the lazy dog.",
        "Please provide specific documentation for the authentication protocol implementation."
    ]
    
    print("\n" + "=" * 70)
    print("TEXT ANALYSIS EXAMPLES")
    print("=" * 70)
    
    for i, text in enumerate(test_texts, 1):
        print(f"\nEXAMPLE {i}:")
        print("-" * 20)
        analyzer.print_analysis_report(text)
    
    # Print overall statistics
    print("\n" + "=" * 70)
    print("OVERALL STATISTICS")
    print("=" * 70)
    stats = analyzer.get_statistics()
    
    print(f"Total top-100 words: {stats['total_words']}")
    print(f"\nCategory breakdown:")
    for category, count in stats['category_breakdown'].items():
        print(f"  {category.replace('_', ' ').title()}: {count} words")
    
    print(f"\nEfficiency breakdown:")
    for level, count in stats['efficiency_breakdown'].items():
        print(f"  {level.replace('_', ' ').title()}: {count} words")

if __name__ == "__main__":
    main()
