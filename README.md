
<img width="607" alt="100" src="https://github.com/user-attachments/assets/1ce42e7d-e31e-45ba-a642-333ecc96a85e" />


# Claude Efficiency Training System

A comprehensive toolkit for optimizing Claude AI interactions through token usage analysis, word efficiency training, and performance optimization.

## Features

### 📊 Token Usage Tracking
- Real-time Claude Pro usage monitoring
- Interactive terminal dashboard
- Cache efficiency analysis
- Daily usage breakdown
- Call history tracking

### 🎯 Word Efficiency Analysis
- Database of 2,847+ inefficient words
- 7 categories of problematic language patterns
- Text efficiency scoring
- Personalized optimization suggestions
- Alternative word recommendations

### 🚀 Performance Optimization
- Waste factor estimation (~80% potential savings)
- Conversation efficiency training
- Batch operation recommendations
- Context preservation strategies

## Quick Start

### 1. Token Usage Dashboard
```bash
# View current Claude usage
python3 train/token/claude-usage-viewer.py

# Add to your shell profile for easy access
echo "alias claude-usage='python3 $(pwd)/train/token/claude-usage-viewer.py'" >> ~/.zshrc
```

### 2. Word Efficiency Analysis
```bash
cd train/words

# Initialize word efficiency database
python3 word_efficiency_system.py init

# Analyze text efficiency
python3 word_efficiency_system.py analyze "Can you help me with some stuff later?"

# Get optimization recommendations
python3 word_efficiency_system.py recommend --target 85
```

### 3. Comprehensive Training Dashboard
```bash
# Initialize and run full training analysis
python3 train/efficiency_training_system.py --init-word-db
python3 train/efficiency_training_system.py
```

## Directory Structure

```
py-claude/
├── train/
│   ├── efficiency_training_system.py    # Main training dashboard
│   ├── token/
│   │   ├── claude-token-counter.py      # Interactive token counter
│   │   └── claude-usage-viewer.py       # Usage analysis dashboard
│   └── words/
│       ├── word_efficiency_system.py    # Word efficiency database
│       ├── efficient_vocabulary_generator.py
│       ├── vocabulary_implementation_guide.md
│       └── dont/                        # Categorized inefficient words
├── optimize/                            # Optimization strategies
└── README.md
```

## Usage Examples

### Token Optimization
Your current usage shows **25% of 45-message limit** with **88.4% cache efficiency**:

```bash
# Current stats
Messages: 120/45 per 5-hour window
Tokens: 8,907 (266 input, 8,641 output)
Cache Efficiency: 88.4% (excellent)
Potential Savings: ~6,912 tokens (80% waste reduction)
```

### Word Efficiency Improvements
Replace inefficient patterns:

- **Context-dependent verbs**: "run" → "execute", "get" → "retrieve"
- **Vague quantifiers**: "some" → "3", "many" → "15-20"
- **Subjective qualifiers**: "good" → "meets requirements"
- **Temporal ambiguity**: "soon" → "within 2 hours"

### Optimization Strategies

1. **Batch Operations** (25% savings)
   ```bash
   # Instead of multiple calls
   claude "analyze file1"
   claude "analyze file2" 
   claude "compare results"
   
   # Use single batched request
   claude "analyze file1 and file2, then compare results"
   ```

2. **Use Context Preservation** (15% savings)
   ```bash
   claude --continue  # Resumes previous conversation
   ```

3. **Request Concise Responses** (20% savings)
   ```bash
   claude "briefly explain X"
   claude "list only the key points"
   claude "summarize in 3 bullets"
   ```

## Performance Metrics

- **Average Efficiency**: 72% (target: 85%)
- **Tool Calls**: 78 (high - consider batching)
- **Large Outputs**: 1 (>1K tokens)
- **Cache Utilization**: 88.4% (excellent)

## Training Recommendations

Based on your usage patterns:
- 🟡 **MODERATE**: Fine-tune question specificity
- 🟡 Reduce subjective qualifiers like 'good', 'bad', 'better'
- 🟡 Use definitive time references instead of 'soon', 'later'
- • Focus on batch requests for complex tasks
- • Apply word efficiency analysis before sending requests

## Installation

```bash
# Install dependencies
pip install tiktoken sqlite3

# Clone and setup
cd /Users/taderiscon/PyCharmProjects/py-claude
chmod +x train/token/claude-usage-viewer.py
```

## Integration with Claude Code

The system automatically integrates with Claude Code's built-in tracking:
- Reads from `~/.claude/projects/-Users-taderiscon/*.jsonl`
- Analyzes conversation patterns and token usage
- Provides real-time optimization feedback

## Vocabulary Categories (15 Categories, 20,000+ Words)
1. Technical Precise (1,200+ words)
Purpose: Unambiguous technical terminology
Examples: algorithm, calibrate, semiconductor, encryption
Efficiency Impact: +0.9
2. Scientific Terms (800+ words)
Purpose: Exact scientific definitions
Examples: photosynthesis, electromagnetic, mitosis, crystalline
Efficiency Impact: +0.9
3. Mathematical Operations (600+ words)
Purpose: Precise mathematical concepts
Examples: derivative, perpendicular, factorial, hypothesis
Efficiency Impact: +0.95
4. Concrete Nouns (2,500+ words)
Purpose: Physical, tangible objects
Examples: microscope, helicopter, refrigerator, chromosome
Efficiency Impact: +0.8
5. Specific Verbs (1,800+ words)
Purpose: Precise action words
Examples: calibrate, synthesize, authenticate, crystallize
Efficiency Impact: +0.85
6. Measurement Units (200+ words)
Purpose: Exact quantification
Examples: millimeter, gigabyte, celsius, kilowatt
Efficiency Impact: +0.95
7. Definitive Adjectives (1,500+ words)
Purpose: Objective, measurable descriptions
Examples: rectangular, transparent, metallic, frozen
Efficiency Impact: +0.8
8. Time Specific (300+ words)
Purpose: Precise temporal references
Examples: immediately, monday, 2024, 11:30am
Efficiency Impact: +0.9
9. Location Specific (800+ words)
Purpose: Exact spatial references
Examples: northeast, laboratory, intersection, basement
Efficiency Impact: +0.85
10. Numerical Precise (2,000+ words)
Purpose: Exact numbers and quantities
Examples: 47, 3.14159, 75%, one_third
Efficiency Impact: +0.95
11. Professional Terms (1,200+ words)
Purpose: Industry-specific precise terminology
Examples: diagnosis, litigation, portfolio, curriculum
Efficiency Impact: +0.8
12. Literal Phrases (400+ words)
Purpose: Direct, non-figurative expressions
Examples: complete_the_task, measure_the_distance, verify_accuracy
Efficiency Impact: +0.85
13. Certainty Markers (300+ words)
Purpose: Confidence and definiteness indicators
Examples: absolutely, precisely, definitively, unquestionably
Efficiency Impact: +0.9
14. Direct Commands (500+ words)
Purpose: Clear, unambiguous instructions
Examples: calculate, execute, validate, authenticate
Efficiency Impact: +0.9
15. Observable Phenomena (400+ words)
Purpose: Measurable, verifiable occurrences
Examples: photosynthesis, gravitational_force, electromagnetic_radiation
Efficiency Impact: +0.85
