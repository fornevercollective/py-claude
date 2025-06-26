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
    
    for msg in messages:
        if 'usage' in msg:
            usage = msg['usage']
            total_input += usage.get('input_tokens', 0)
            total_output += usage.get('output_tokens', 0)
            total_cache_creation += usage.get('cache_creation_input_tokens', 0)
            total_cache_read += usage.get('cache_read_input_tokens', 0)
            message_count += 1
            
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
        'daily_usage': dict(daily_usage)
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