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
        
        # Ensure /home exists and set it as the working directory
        try:
            os.stat('/home')
        except OSError:
            os.mkdir('/home')
            
        try:
            os.chdir('/home')
        except OSError:
            pass
        
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
            path = parts[1] if len(parts) > 1 else "."
            try:
                files = os.listdir(path)
                if not files:
                    terminal.send_response("(empty directory)", color=ANSI_CYAN)
                else:
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
                
        elif cmd == "pwd":
            terminal.send_response(os.getcwd(), color=ANSI_CYAN)
            
        elif cmd == "cd":
            path = parts[1] if len(parts) > 1 else "/home"
            try:
                os.chdir(path)
                # We return an empty string because the terminal will automatically 
                # print the new prompt with the updated path.
                terminal.send_response("")
            except Exception as e:
                terminal.send_response(f"cd error: {str(e)}", color=ANSI_RED)
                
        elif cmd == "touch":
            if len(parts) > 1:
                try:
                    with open(parts[1], 'a'):
                        pass
                    terminal.send_response(f"Created {parts[1]}", color=ANSI_GREEN)
                except Exception as e:
                    terminal.send_response(f"touch error: {str(e)}", color=ANSI_RED)
            else:
                terminal.send_response("Usage: touch <filename>", color=ANSI_RED)
                
        elif cmd == "mkdir":
            if len(parts) > 1:
                try:
                    os.mkdir(parts[1])
                    terminal.send_response(f"Created directory {parts[1]}", color=ANSI_GREEN)
                except Exception as e:
                    terminal.send_response(f"mkdir error: {str(e)}", color=ANSI_RED)
            else:
                terminal.send_response("Usage: mkdir <directory>", color=ANSI_RED)
                
        elif cmd == "rm":
            if len(parts) > 1:
                try:
                    os.remove(parts[1])
                    terminal.send_response(f"Deleted file {parts[1]}", color=ANSI_GREEN)
                except OSError:
                    try:
                        os.rmdir(parts[1])
                        terminal.send_response(f"Deleted directory {parts[1]}", color=ANSI_GREEN)
                    except Exception as e:
                        terminal.send_response(f"rm error: {str(e)}", color=ANSI_RED)
            else:
                terminal.send_response("Usage: rm <file_or_directory>", color=ANSI_RED)
                
        elif cmd == "echo":
            if len(parts) > 2:
                filename = parts[1]
                content = " ".join(parts[2:])
                try:
                    with open(filename, 'w') as f:
                        f.write(content + "\n")
                    terminal.send_response(f"Written to {filename}", color=ANSI_GREEN)
                except Exception as e:
                    terminal.send_response(f"echo error: {str(e)}", color=ANSI_RED)
            else:
                terminal.send_response("Usage: echo <filename> <text...>", color=ANSI_RED)
                
        elif cmd == "append":
            if len(parts) > 2:
                filename = parts[1]
                content = " ".join(parts[2:])
                try:
                    with open(filename, 'a') as f:
                        f.write(content + "\n")
                    terminal.send_response(f"Appended to {filename}", color=ANSI_GREEN)
                except Exception as e:
                    terminal.send_response(f"append error: {str(e)}", color=ANSI_RED)
            else:
                terminal.send_response("Usage: append <filename> <text...>", color=ANSI_RED)
                
        else:
            terminal.send_response(f"Unknown command: {cmd}", color=ANSI_RED)
            
        return True
