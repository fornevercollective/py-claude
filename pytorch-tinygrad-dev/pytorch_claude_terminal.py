#!/usr/bin/env python3
"""
PyTorch-Claude Side-by-Side Terminal Manager
Creates split terminal windows for PyTorch development and Claude interaction
"""

import os
import subprocess
import time
import json
from pathlib import Path


class PyTorchClaudeTerminal:
    """Manages side-by-side PyTorch and Claude terminal sessions"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.session_config_file = self.project_root / "terminal_session_config.json"
        
    def create_iterm_session(self):
        """Create iTerm2 session with PyTorch and Claude side by side"""
        
        applescript = '''
        tell application "iTerm2"
            create window with default profile
            
            tell current session of current window
                -- Left pane: PyTorch Development
                write text "echo '🔥 PyTorch Development Environment'"
                write text "cd /Users/taderiscon/PyCharmProjects/pytorch-tinygrad-dev"
                write text "source venv/bin/activate"
                write text "python3 pytorch_startup_banner.py"
                write text "echo '\\n💡 Ready for PyTorch development!'"
                write text "echo 'Commands: python3 pytorch_daily_efficiency_v2.py --status'"
                
                -- Split vertically for Claude
                split vertically with default profile
            end tell
            
            tell second session of current window
                -- Right pane: Claude Integration
                write text "echo '🤖 Claude Integration Terminal'"
                write text "cd /Users/taderiscon/PyCharmProjects/pytorch-tinygrad-dev"
                write text "python3 claude_integration.py --start-session pytorch_development"
                write text "echo '\\n💬 Claude Integration Active!'"
                write text "echo 'Commands:'"
                write text "echo '  claude --help'"
                write text "echo '  python3 claude_integration.py --suggestions'"
                write text "echo '  python3 claude_integration.py --report'"
            end tell
            
            -- Focus on PyTorch pane
            tell first session of current window
                select
            end tell
            
        end tell
        '''
        
        try:
            subprocess.run(['osascript', '-e', applescript], check=True)
            print("✅ iTerm2 session created with PyTorch and Claude side by side")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create iTerm2 session: {e}")
            return False
        except FileNotFoundError:
            print("❌ iTerm2 not found. Please install iTerm2 or use --terminal option")
            return False
    
    def create_terminal_session(self):
        """Create macOS Terminal session with tabs"""
        
        applescript = '''
        tell application "Terminal"
            activate
            
            -- Create new window for PyTorch
            do script "echo '🔥 PyTorch Development Environment'; cd /Users/taderiscon/PyCharmProjects/pytorch-tinygrad-dev; source venv/bin/activate; python3 pytorch_startup_banner.py; echo '\\n💡 Ready for PyTorch development!'"
            
            -- Create new tab for Claude
            tell application "System Events" to keystroke "t" using command down
            delay 1
            do script "echo '🤖 Claude Integration Terminal'; cd /Users/taderiscon/PyCharmProjects/pytorch-tinygrad-dev; python3 claude_integration.py --start-session pytorch_development; echo '\\n💬 Claude Integration Active!'" in front window
            
        end tell
        '''
        
        try:
            subprocess.run(['osascript', '-e', applescript], check=True)
            print("✅ Terminal session created with PyTorch and Claude tabs")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create Terminal session: {e}")
            return False
    
    def create_tmux_session(self):
        """Create tmux session with PyTorch and Claude panes"""
        
        session_name = "pytorch-claude"
        
        # Check if tmux is available
        try:
            subprocess.run(['tmux', '--version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ tmux not found. Install with: brew install tmux")
            return False
        
        commands = [
            # Kill existing session if it exists
            f"tmux kill-session -t {session_name} 2>/dev/null || true",
            
            # Create new session with PyTorch pane
            f"tmux new-session -d -s {session_name} -c '/Users/taderiscon/PyCharmProjects/pytorch-tinygrad-dev'",
            
            # Setup PyTorch pane
            f"tmux send-keys -t {session_name}:0 'source venv/bin/activate' Enter",
            f"tmux send-keys -t {session_name}:0 'python3 pytorch_startup_banner.py' Enter",
            f"tmux send-keys -t {session_name}:0 'echo \"💡 PyTorch Ready! Commands:\"' Enter",
            f"tmux send-keys -t {session_name}:0 'echo \"  python3 pytorch_daily_efficiency_v2.py --benchmark\"' Enter",
            f"tmux send-keys -t {session_name}:0 'echo \"  python3 pytorch_tinygrad_bridge.py\"' Enter",
            
            # Split window vertically for Claude
            f"tmux split-window -t {session_name}:0 -h -c '/Users/taderiscon/PyCharmProjects/pytorch-tinygrad-dev'",
            
            # Setup Claude pane
            f"tmux send-keys -t {session_name}:0.1 'python3 claude_integration.py --start-session pytorch_development' Enter",
            f"tmux send-keys -t {session_name}:0.1 'echo \"🤖 Claude Integration Ready!\"' Enter",
            f"tmux send-keys -t {session_name}:0.1 'echo \"Commands:\"' Enter",
            f"tmux send-keys -t {session_name}:0.1 'echo \"  python3 claude_integration.py --suggestions\"' Enter",
            f"tmux send-keys -t {session_name}:0.1 'echo \"  python3 claude_integration.py --report\"' Enter",
            
            # Set pane titles
            f"tmux select-pane -t {session_name}:0.0 -T 'PyTorch Development'",
            f"tmux select-pane -t {session_name}:0.1 -T 'Claude Integration'",
            
            # Focus on PyTorch pane
            f"tmux select-pane -t {session_name}:0.0",
            
            # Attach to session
            f"tmux attach-session -t {session_name}"
        ]
        
        try:
            for cmd in commands[:-1]:  # Execute all but the last command
                subprocess.run(cmd, shell=True, check=True)
            
            print(f"✅ tmux session '{session_name}' created")
            print("💡 Attaching to session...")
            
            # Execute the attach command in foreground
            os.system(commands[-1])
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create tmux session: {e}")
            return False
    
    def create_screen_session(self):
        """Create GNU Screen session with PyTorch and Claude"""
        
        session_name = "pytorch-claude"
        
        # Check if screen is available
        try:
            subprocess.run(['screen', '--version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ screen not found. Install with: brew install screen")
            return False
        
        # Create screen configuration
        screenrc_content = f'''
# PyTorch-Claude Screen Configuration
startup_message off
hardstatus alwayslastline
hardstatus string '%{{= kG}}[ %{{G}}%H %{{g}}][%= %{{= kw}}%?%-Lw%?%{{r}}(%{{W}}%n*%f%t%?(%u)%?%{{r}})%{{w}}%?%+Lw%?%?%= %{{g}}][%{{B}} %d/%m %{{W}}%c %{{g}}]'

# Create windows
screen -t "PyTorch" 0 bash -c 'cd /Users/taderiscon/PyCharmProjects/pytorch-tinygrad-dev && source venv/bin/activate && python3 pytorch_startup_banner.py && echo "💡 PyTorch Ready!" && bash'
screen -t "Claude" 1 bash -c 'cd /Users/taderiscon/PyCharmProjects/pytorch-tinygrad-dev && python3 claude_integration.py --start-session pytorch_development && echo "🤖 Claude Ready!" && bash'

# Start on PyTorch window
select 0
'''
        
        screenrc_file = self.project_root / ".screenrc_pytorch_claude"
        with open(screenrc_file, 'w') as f:
            f.write(screenrc_content)
        
        try:
            # Start screen session
            cmd = f"screen -c {screenrc_file} -S {session_name}"
            print(f"✅ Starting screen session '{session_name}'")
            print("💡 Use Ctrl+A then 0/1 to switch between PyTorch and Claude")
            print("💡 Use Ctrl+A then d to detach, 'screen -r pytorch-claude' to reattach")
            
            os.system(cmd)
            return True
            
        except Exception as e:
            print(f"❌ Failed to create screen session: {e}")
            return False
    
    def create_wezterm_session(self):
        """Create WezTerm session if available"""
        
        # Check if WezTerm is available
        wezterm_paths = [
            '/Applications/WezTerm.app/Contents/MacOS/wezterm',
            '/usr/local/bin/wezterm',
            '/opt/homebrew/bin/wezterm'
        ]
        
        wezterm_path = None
        for path in wezterm_paths:
            if os.path.exists(path):
                wezterm_path = path
                break
        
        if not wezterm_path:
            print("❌ WezTerm not found")
            return False
        
        # Create WezTerm configuration for split panes
        lua_script = f'''
local wezterm = require 'wezterm'

wezterm.on('gui-startup', function()
    local tab, pane, window = wezterm.mux.spawn_window{{
        cwd = "/Users/taderiscon/PyCharmProjects/pytorch-tinygrad-dev",
    }}
    
    -- Left pane: PyTorch
    pane:send_text("source venv/bin/activate\\n")
    pane:send_text("python3 pytorch_startup_banner.py\\n")
    
    -- Split for Claude pane
    local claude_pane = pane:split{{
        direction = 'Right',
        size = 0.5,
        cwd = "/Users/taderiscon/PyCharmProjects/pytorch-tinygrad-dev",
    }}
    
    -- Claude pane setup
    claude_pane:send_text("python3 claude_integration.py --start-session pytorch_development\\n")
    
    -- Focus on PyTorch pane
    pane:activate()
end)

return {{}}
'''
        
        try:
            config_file = Path.home() / ".config" / "wezterm" / "pytorch_claude.lua"
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_file, 'w') as f:
                f.write(lua_script)
            
            subprocess.run([wezterm_path, '--config-file', str(config_file)], check=True)
            print("✅ WezTerm session created with PyTorch and Claude")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create WezTerm session: {e}")
            return False
    
    def save_session_config(self, terminal_type: str, session_info: dict):
        """Save session configuration for later restoration"""
        config = {
            'terminal_type': terminal_type,
            'session_info': session_info,
            'created_at': time.time(),
            'project_root': str(self.project_root)
        }
        
        with open(self.session_config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def list_available_terminals(self):
        """List available terminal applications"""
        terminals = []
        
        # Check iTerm2
        if os.path.exists('/Applications/iTerm.app'):
            terminals.append(('iterm', 'iTerm2 (Recommended)', 'create_iterm_session'))
        
        # Check macOS Terminal
        if os.path.exists('/Applications/Utilities/Terminal.app'):
            terminals.append(('terminal', 'macOS Terminal', 'create_terminal_session'))
        
        # Check tmux
        try:
            subprocess.run(['tmux', '--version'], capture_output=True, check=True)
            terminals.append(('tmux', 'tmux (Terminal Multiplexer)', 'create_tmux_session'))
        except:
            pass
        
        # Check screen
        try:
            subprocess.run(['screen', '--version'], capture_output=True, check=True)
            terminals.append(('screen', 'GNU Screen', 'create_screen_session'))
        except:
            pass
        
        # Check WezTerm
        if any(os.path.exists(path) for path in ['/Applications/WezTerm.app', '/usr/local/bin/wezterm', '/opt/homebrew/bin/wezterm']):
            terminals.append(('wezterm', 'WezTerm', 'create_wezterm_session'))
        
        return terminals


def main():
    """Main CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='PyTorch-Claude Side-by-Side Terminal Manager')
    parser.add_argument('--terminal', choices=['iterm', 'terminal', 'tmux', 'screen', 'wezterm', 'auto'],
                       default='auto', help='Terminal application to use')
    parser.add_argument('--list', action='store_true', help='List available terminal applications')
    
    args = parser.parse_args()
    
    manager = PyTorchClaudeTerminal()
    
    if args.list:
        terminals = manager.list_available_terminals()
        print("🖥️  Available Terminal Applications:")
        for term_id, name, method in terminals:
            print(f"  {term_id}: {name}")
        return
    
    print("🚀 PyTorch-Claude Side-by-Side Terminal Manager")
    print("=" * 60)
    
    if args.terminal == 'auto':
        # Auto-detect best available terminal
        terminals = manager.list_available_terminals()
        if not terminals:
            print("❌ No suitable terminal applications found")
            return
        
        # Prefer iTerm2, then tmux, then others
        preferred_order = ['iterm', 'tmux', 'terminal', 'wezterm', 'screen']
        terminal_dict = {term[0]: term for term in terminals}
        
        selected_terminal = None
        for pref in preferred_order:
            if pref in terminal_dict:
                selected_terminal = terminal_dict[pref]
                break
        
        if not selected_terminal:
            selected_terminal = terminals[0]
        
        print(f"🎯 Auto-selected: {selected_terminal[1]}")
        method_name = selected_terminal[2]
        
    else:
        method_name = f"create_{args.terminal}_session"
        if not hasattr(manager, method_name):
            print(f"❌ Terminal type '{args.terminal}' not supported")
            return
    
    # Execute the selected method
    method = getattr(manager, method_name)
    success = method()
    
    if success:
        print("\n✅ Terminal session created successfully!")
        print("\n💡 Quick Tips:")
        print("  Left/Top pane: PyTorch Development Environment")
        print("  Right/Bottom pane: Claude Integration Terminal")
        print("\n🔧 PyTorch Commands:")
        print("  python3 pytorch_daily_efficiency_v2.py --benchmark")
        print("  python3 pytorch_tinygrad_bridge.py")
        print("\n🤖 Claude Commands:")
        print("  python3 claude_integration.py --suggestions")
        print("  python3 claude_integration.py --report")
    else:
        print("\n❌ Failed to create terminal session")
        print("💡 Try a different terminal with --terminal option")


if __name__ == "__main__":
    main()