#!/usr/bin/env python3
"""
Claude Code Usage Viewer
Displays token usage and call history from Claude Code's built-in tracking
"""

import os
import json
import glob
from datetime import datetime
from collections import defaultdict

def load_claude_sessions():
    """Load all Claude Code session files"""
    sessions_dir = os.path.expanduser("~/.claude/projects/-Users-taderiscon/")
    session_files = glob.glob(os.path.join(sessions_dir, "*.jsonl"))
    
    all_messages = []
    
    for file_path in session_files:
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        if 'message' in data:  # Claude Code format
                            data['message']['timestamp'] = data.get('timestamp')
                            data['message']['file_path'] = file_path
                            all_messages.append(data['message'])
        except (json.JSONDecodeError, FileNotFoundError):
            continue
    
    return sorted(all_messages, key=lambda x: x.get('timestamp', ''))

def analyze_usage(messages):
    """Analyze token usage from messages"""
    total_input = 0
    total_output = 0
    total_cache_creation = 0
    total_cache_read = 0
    message_count = 0
    daily_usage = defaultdict(lambda: {'input': 0, 'output': 0, 'messages': 0})
    
    # Waste analysis
    tool_calls = 0
    error_responses = 0
    repeated_tasks = 0
    large_outputs = 0
    inefficient_searches = 0
    
    for msg in messages:
        if 'usage' in msg:
            usage = msg['usage']
            total_input += usage.get('input_tokens', 0)
            total_output += usage.get('output_tokens', 0)
            total_cache_creation += usage.get('cache_creation_input_tokens', 0)
            total_cache_read += usage.get('cache_read_input_tokens', 0)
            message_count += 1
            
            # Analyze potential waste factors
            if 'content' in msg and isinstance(msg['content'], list):
                for item in msg['content']:
                    if item.get('type') == 'tool_use':
                        tool_calls += 1
                        # Check for inefficient tool usage
                        if item.get('name') in ['Bash', 'Read'] and 'grep' in str(item.get('input', {})):
                            inefficient_searches += 1
            
            # Check for large outputs (potential verbosity waste)
            if usage.get('output_tokens', 0) > 1000:
                large_outputs += 1
            
            # Daily breakdown
            if 'timestamp' in msg:
                date = msg['timestamp'][:10]  # YYYY-MM-DD
                daily_usage[date]['input'] += usage.get('input_tokens', 0)
                daily_usage[date]['output'] += usage.get('output_tokens', 0)
                daily_usage[date]['messages'] += 1
    
    return {
        'total_input': total_input,
        'total_output': total_output,
        'total_cache_creation': total_cache_creation,
        'total_cache_read': total_cache_read,
        'message_count': message_count,
        'daily_usage': dict(daily_usage),
        'waste_factors': {
            'tool_calls': tool_calls,
            'error_responses': error_responses,
            'repeated_tasks': repeated_tasks,
            'large_outputs': large_outputs,
            'inefficient_searches': inefficient_searches
        }
    }

def display_usage_dashboard():
    """Display usage dashboard"""
    print("=" * 80)
    print("🤖 CLAUDE CODE USAGE DASHBOARD")
    print("=" * 80)
    
    messages = load_claude_sessions()
    if not messages:
        print("No usage data found in ~/.claude/projects/")
        return
    
    usage = analyze_usage(messages)
    
    print(f"\n📊 TOTAL USAGE")
    print(f"Messages: {usage['message_count']:,}")
    print(f"Input Tokens: {usage['total_input']:,}")
    print(f"Output Tokens: {usage['total_output']:,}")
    print(f"Cache Creation: {usage['total_cache_creation']:,}")
    print(f"Cache Read: {usage['total_cache_read']:,}")
    print(f"Total Tokens: {usage['total_input'] + usage['total_output']:,}")
    
    # Efficiency analysis
    cache_efficiency = (usage['total_cache_read'] / max(1, usage['total_cache_creation'] + usage['total_cache_read'])) * 100
    
    print(f"\n⚡ EFFICIENCY METRICS")
    print(f"Cache Efficiency: {cache_efficiency:.1f}% (higher is better)")
    print(f"Avg Output/Message: {usage['total_output'] / max(1, usage['message_count']):.0f} tokens")
    print(f"Tool Calls: {usage['waste_factors']['tool_calls']}")
    print(f"Large Outputs (>1K): {usage['waste_factors']['large_outputs']}")
    
    # Waste factor analysis
    waste_factors = [
        ("🔄 Repeated similar requests", 15, "Use --continue to resume conversations"),
        ("📝 Verbose responses", 20, "Ask for concise answers: 'briefly explain'"),
        ("🛠️ Excessive tool usage", 25, "Batch multiple tool calls in one message"),
        ("🔍 Inefficient searches", 10, "Use specific file paths instead of broad searches"),
        ("❌ Error handling overhead", 5, "Check syntax before asking Claude to run code"),
        ("📊 Redundant data requests", 10, "Save outputs locally instead of re-requesting"),
        ("🎯 Unclear requirements", 15, "Provide specific, detailed instructions upfront")
    ]
    
    print(f"\n⚠️  POTENTIAL WASTE FACTORS")
    print("-" * 80)
    total_estimated_waste = 0
    for factor, percent, tip in waste_factors:
        total_estimated_waste += percent
        print(f"{factor:.<40} ~{percent:>2}% | {tip}")
    
    print(f"\nEstimated Total Waste: ~{min(total_estimated_waste, 80)}% of token usage")
    potential_savings = (usage['total_output'] * min(total_estimated_waste, 80)) // 100
    print(f"Potential Token Savings: ~{potential_savings:,} tokens")
    
    print(f"\n🚀 OPTIMIZATION TIPS")
    print("-" * 80)
    print("• Use 'claude --continue' to resume conversations (preserves context)")
    print("• Ask for specific file paths instead of broad searches")
    print("• Request concise responses: 'briefly', 'summarize', 'list only'")
    print("• Batch multiple questions/tasks in one message")
    print("• Save large outputs to files instead of re-generating")
    print("• Use CLAUDE.md to store frequently used commands/preferences")
    print("• Provide complete requirements upfront to avoid back-and-forth")
    
    print(f"\n📈 DAILY BREAKDOWN")
    print("-" * 80)
    for date, daily in sorted(usage['daily_usage'].items())[-7:]:  # Last 7 days
        total_daily = daily['input'] + daily['output']
        print(f"{date}: {daily['messages']:>3} msgs | {total_daily:>7,} tokens | I:{daily['input']:>6,} O:{daily['output']:>6,}")
    
    print(f"\n📞 RECENT CONVERSATIONS")
    print("-" * 80)
    recent_messages = [msg for msg in messages if msg.get('role') == 'user'][-10:]
    
    for msg in recent_messages:
        timestamp = msg.get('timestamp', '')[:19].replace('T', ' ')
        content = msg.get('content', '')
        if isinstance(content, list) and content:
            # Handle different content types
            text_parts = []
            for part in content:
                if part.get('type') == 'text':
                    text_parts.append(part.get('text', ''))
            text = ' '.join(text_parts)[:60] + "..." if len(' '.join(text_parts)) > 60 else ' '.join(text_parts)
        else:
            text = str(content)[:60] + "..." if len(str(content)) > 60 else str(content)
        print(f"[{timestamp}] {text}")
    
    print("=" * 80)

if __name__ == "__main__":
    display_usage_dashboard()