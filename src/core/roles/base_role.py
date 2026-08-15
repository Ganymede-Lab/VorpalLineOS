class BaseRole:
    """
    Base interface for all VorpaLine OS shard roles.
    """
    def __init__(self, config):
        self.config = config
        
    def handle_command(self, cmd_string, terminal):
        """
        Parses and executes a command string from the terminal.
        Must return True if the command was handled, False otherwise.
        """
        return False
        
    def standby_tick(self):
        """
        Called every iteration of the OS standby loop.
        Used for background autonomous tasks (e.g., publishing telemetry).
        """
        pass
