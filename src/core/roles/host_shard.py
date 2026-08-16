from core.roles.base_role import BaseRole
import gc
import sys
import os

class HostShard(BaseRole):
    """
    The standard terminal-based interaction shard for the Cyberdeck.
    Handles basic filesystem and system commands.
    """
    def __init__(self, config):
        super().__init__(config)
        
    def handle_command(self, cmd_string, terminal):
        if not cmd_string:
            return False
            
        ANSI_GREEN = getattr(terminal, 'ANSI_GREEN', '')
        ANSI_CYAN = getattr(terminal, 'ANSI_CYAN', '')
        ANSI_RED = getattr(terminal, 'ANSI_RED', '')
            
        parts = cmd_string.split()
        cmd = parts[0]
        
        if cmd == "ping":
            terminal.send_response("PONG // SYSTEM ACTIVE", color=ANSI_GREEN)
            
        elif cmd == "info":
            info_str = f"Shard: {self.config.get('shard_id', 'UNKNOWN')}\n"
            info_str += f"Role: {self.config.get('role_class', 'UNKNOWN')}\n"
            info_str += f"RAM Free: {gc.mem_free()} bytes\n"
            info_str += f"RAM Alloc: {gc.mem_alloc()} bytes"
            terminal.send_response(info_str, color=ANSI_CYAN)
            
        elif cmd == "ls":
            try:
                files = os.listdir()
                terminal.send_response("\n".join(files), color=ANSI_CYAN)
            except Exception as e:
                terminal.send_response(f"Error: {str(e)}", color=ANSI_RED)
                
        elif cmd == "read":
            if len(parts) > 1:
                try:
                    with open(parts[1], "r") as f:
                        terminal.send_response(f.read(), color=ANSI_CYAN)
                except Exception as e:
                    terminal.send_response(f"Error reading {parts[1]}: {str(e)}", color=ANSI_RED)
            else:
                terminal.send_response("Usage: read <filename>", color=ANSI_RED)
                
        else:
            terminal.send_response(f"Unknown command: {cmd}", color=ANSI_RED)
            
        return True
