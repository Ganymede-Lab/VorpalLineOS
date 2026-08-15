import gc

# Store references to dynamically loaded modules
loaded_modules = {}

def load_modules(module_names):
    """
    Reads the active_modules array from the parsed config and 
    dynamically imports only those specified driver modules to save memory.
    """
    for mod_name in module_names:
        if mod_name not in loaded_modules:
            try:
                print("[HAL] Dynamically loading module: {}".format(mod_name))
                # Dynamic import
                mod = __import__(mod_name)
                components = mod_name.split('.')
                for comp in components[1:]:
                    mod = getattr(mod, comp)
                loaded_modules[mod_name] = mod
            except Exception as e:
                print("[HAL] Error loading module '{}': {}".format(mod_name, e))
    
    # Run garbage collection after dynamic imports
    gc.collect()
    print("[HAL] Module loading complete. Memory cleaned.")
