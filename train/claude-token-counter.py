#!/usr/bin/env python3
"""
Interactive Claude Pro Token Counter
Tracks token usage and call history for Claude Pro plan users
"""

import os
import json
import time
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import tiktoken

class ClaudeTokenCounter:
    def __init__(self, data_file: str = "claude_usage.json"):
        self.data_file = data_file
        self.encoder = tiktoken.get_encoding("cl100k_base")  # GPT-4 encoding as approximation
        self.usage_data = self.load_usage_data()
        
        # Claude Pro limits (based on research)
        self.MESSAGE_LIMIT = 45  # messages per 5-hour window
        self.CONTEXT_WINDOW = 200000  # 200K tokens
        self.RESET_HOURS = 5
        
    def load_usage_data(self) -> Dict:
        """Load usage data from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        return {
            "total_tokens": 0,
            "message_count": 0,
            "last_reset": datetime.now().isoformat(),
            "call_history": [],
            "daily_usage": {}
        }
    
    def save_usage_data(self):
        """Save usage data to JSON file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.usage_data, f, indent=2)
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for given text"""
        return len(self.encoder.encode(text))
    
    def add_conversation(self, user_input: str, claude_response: str):
        """Add a new conversation to tracking"""
        now = datetime.now()
        user_tokens = self.estimate_tokens(user_input)
        response_tokens = self.estimate_tokens(claude_response)
        total_tokens = user_tokens + response_tokens
        
        # Check if we need to reset usage window
        last_reset = datetime.fromisoformat(self.usage_data["last_reset"])
        if now - last_reset > timedelta(hours=self.RESET_HOURS):
            self.reset_usage_window()
        
        # Add to call history
        call_data = {
            "timestamp": now.isoformat(),
            "user_tokens": user_tokens,
            "response_tokens": response_tokens,
            "total_tokens": total_tokens,
            "user_preview": user_input[:100] + "..." if len(user_input) > 100 else user_input,
            "response_preview": claude_response[:100] + "..." if len(claude_response) > 100 else claude_response
        }
        
        self.usage_data["call_history"].append(call_data)
        self.usage_data["total_tokens"] += total_tokens
        self.usage_data["message_count"] += 1
        
        # Track daily usage
        today = now.date().isoformat()
        if today not in self.usage_data["daily_usage"]:
            self.usage_data["daily_usage"][today] = {"tokens": 0, "messages": 0}
        
        self.usage_data["daily_usage"][today]["tokens"] += total_tokens
        self.usage_data["daily_usage"][today]["messages"] += 1
        
        # Keep only last 100 calls to prevent file bloat
        if len(self.usage_data["call_history"]) > 100:
            self.usage_data["call_history"] = self.usage_data["call_history"][-100:]
        
        self.save_usage_data()
    
    def reset_usage_window(self):
        """Reset the 5-hour usage window"""
        self.usage_data["total_tokens"] = 0
        self.usage_data["message_count"] = 0
        self.usage_data["last_reset"] = datetime.now().isoformat()
        self.save_usage_data()
    
    def get_time_until_reset(self) -> timedelta:
        """Get time remaining until next reset"""
        last_reset = datetime.fromisoformat(self.usage_data["last_reset"])
        next_reset = last_reset + timedelta(hours=self.RESET_HOURS)
        return max(timedelta(0), next_reset - datetime.now())
    
    def display_dashboard(self):
        """Display the interactive dashboard"""
        os.system('clear' if os.name == 'posix' else 'cls')
        
        print("=" * 80)
        print("🤖 CLAUDE PRO TOKEN COUNTER")
        print("=" * 80)
        
        # Current usage stats
        remaining_messages = max(0, self.MESSAGE_LIMIT - self.usage_data["message_count"])
        usage_percent = (self.usage_data["message_count"] / self.MESSAGE_LIMIT) * 100
        
        print(f"\n📊 CURRENT USAGE WINDOW")
        print(f"Messages Used: {self.usage_data['message_count']}/{self.MESSAGE_LIMIT} ({usage_percent:.1f}%)")
        print(f"Tokens Used: {self.usage_data['total_tokens']:,}")
        print(f"Messages Remaining: {remaining_messages}")
        
        # Progress bar
        bar_length = 40
        filled_length = int(bar_length * usage_percent / 100)
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        print(f"Progress: [{bar}] {usage_percent:.1f}%")
        
        # Time until reset
        time_until_reset = self.get_time_until_reset()
        hours, remainder = divmod(time_until_reset.total_seconds(), 3600)
        minutes, _ = divmod(remainder, 60)
        print(f"⏰ Next Reset: {int(hours)}h {int(minutes)}m")
        
        # Recent calls
        print(f"\n📞 RECENT CALLS (Last 10)")
        print("-" * 80)
        recent_calls = self.usage_data["call_history"][-10:]
        
        for call in reversed(recent_calls):
            timestamp = datetime.fromisoformat(call["timestamp"]).strftime("%H:%M:%S")
            print(f"[{timestamp}] {call['total_tokens']:>5} tokens | {call['user_preview']}")
        
        # Daily usage summary
        print(f"\n📈 DAILY SUMMARY")
        print("-" * 80)
        today = datetime.now().date().isoformat()
        if today in self.usage_data["daily_usage"]:
            daily = self.usage_data["daily_usage"][today]
            print(f"Today: {daily['messages']} messages, {daily['tokens']:,} tokens")
        else:
            print("Today: No usage yet")
        
        print(f"\n⌨️  COMMANDS")
        print("r - Reset usage window | c - Clear history | q - Quit")
        print("=" * 80)

def main():
    parser = argparse.ArgumentParser(description="Claude Pro Token Counter")
    parser.add_argument("--add", nargs=2, metavar=("USER_INPUT", "CLAUDE_RESPONSE"), 
                       help="Add a conversation (user input and Claude response)")
    parser.add_argument("--interactive", action="store_true", 
                       help="Run in interactive mode")
    parser.add_argument("--data-file", default="claude_usage.json",
                       help="Path to data file (default: claude_usage.json)")
    
    args = parser.parse_args()
    
    counter = ClaudeTokenCounter(args.data_file)
    
    if args.add:
        user_input, claude_response = args.add
        counter.add_conversation(user_input, claude_response)
        print(f"Added conversation: {counter.estimate_tokens(user_input + claude_response)} tokens")
        return
    
    if args.interactive:
        try:
            while True:
                counter.display_dashboard()
                command = input("\nEnter command: ").strip().lower()
                
                if command == 'q':
                    break
                elif command == 'r':
                    counter.reset_usage_window()
                    print("Usage window reset!")
                    time.sleep(1)
                elif command == 'c':
                    counter.usage_data["call_history"] = []
                    counter.save_usage_data()
                    print("Call history cleared!")
                    time.sleep(1)
                elif command == '':
                    time.sleep(1)  # Just refresh
                else:
                    print("Unknown command. Press Enter to refresh.")
                    time.sleep(1)
        except KeyboardInterrupt:
            print("\nExiting...")
    else:
        counter.display_dashboard()

if __name__ == "__main__":
    main()