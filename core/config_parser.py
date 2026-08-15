import json

# Ensure minimal memory overhead for parsing config
def load_config(file_path="shard_profile.json"):
    """
    Loads the JSON profile from the filesystem.
    """
    try:
        with open(file_path, "r") as f:
            config_data = f.read()
            config = json.loads(config_data)
            
            # Use tuple for required keys to avoid heap allocation
            REQUIRED_KEYS = ("shard_id", "role_class", "board_type", "active_modules")
            for key in REQUIRED_KEYS:
                if key not in config:
                    print("[WARNING] Missing key in profile:", key)
                    
            return config
            
    except OSError:
        print("[ERROR] shard_profile.json not found.")
        return {}
    except ValueError:
        print("[ERROR] shard_profile.json contains invalid JSON.")
        return {}
