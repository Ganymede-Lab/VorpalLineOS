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
            
        parts = cmd_string.split()
        cmd = parts[0]
        
        if cmd == "ping":
            terminal.send_response({"status": "ok", "message": "pong"})
            
        elif cmd == "info":
            terminal.send_response({
                "shard_id": self.config.get("shard_id", "UNKNOWN"),
                "role": self.config.get("role_class", "UNKNOWN"),
                "free_ram": gc.mem_free(),
                "alloc_ram": gc.mem_alloc()
            })
            
        elif cmd == "ls":
            try:
                files = os.listdir()
                terminal.send_response({"files": files})
            except Exception as e:
                terminal.send_response({"error": str(e)})
                
        elif cmd == "read":
            if len(parts) > 1:
                try:
                    with open(parts[1], "r") as f:
                        terminal.send_response({"file": parts[1], "content": f.read()})
                except Exception as e:
                    terminal.send_response({"error": str(e)})
            else:
                terminal.send_response({"error": "Usage: read <filename>"})
                
        else:
            terminal.send_response({"error": "Unknown HostShard command", "cmd": cmd})
            
        return True
