import time
import gc
import micropython
from machine import Pin

try:
    from micropython import const
except ImportError:
    const = lambda x: x

from core.config_parser import load_config
from hal.tool_manager import load_modules, loaded_modules
from hal.pin_map import (
    ONBOARD_LED, 
    LED_PIN_MASK, 
    gpio_fast_toggle
)

STATE_BOOTING = const(0)
STATE_INIT_HAL = const(1)
STATE_OFFLINE_STANDBY = const(2)

class VorpaLineOS:
    def __init__(self):
        self.state = STATE_BOOTING
        self.config = {}
        self.role = None
        self.led = None
        self.use_viper_gpio = False

    def run(self):
        while True:
            if self.state == STATE_BOOTING:
                self.boot_sequence()
            elif self.state == STATE_INIT_HAL:
                self.init_hal()
            elif self.state == STATE_OFFLINE_STANDBY:
                self.standby_loop()
                
    def boot_sequence(self):
        print("[OS] VorpaLine Kernel Booting...")
        self.config = load_config()
        print("[OS] Config loaded for Shard:", self.config.get("shard_id"))
        self.state = STATE_INIT_HAL

    def init_hal(self):
        print("[OS] Initializing Hardware Abstraction Layer...")
        
        try:
            self.led = Pin(ONBOARD_LED, Pin.OUT)
            self.use_viper_gpio = True
        except Exception:
            pass
            
        active_modules = self.config.get("active_modules", [])
        if active_modules:
            load_modules(active_modules)
            
        # Dynamically load the Role class specified in config
        role_path = self.config.get("role_class")
        if role_path:
            try:
                print(f"[OS] Instantiating Shard Role: {role_path}")
                # e.g., role_path = "core.roles.host_shard.HostShard"
                module_name, class_name = role_path.rsplit('.', 1)
                mod = __import__(module_name)
                components = module_name.split('.')
                for comp in components[1:]:
                    mod = getattr(mod, comp)
                RoleClass = getattr(mod, class_name)
                self.role = RoleClass(self.config)
            except Exception as e:
                print(f"[OS] Failed to load role '{role_path}': {e}")
                
        self.state = STATE_OFFLINE_STANDBY
        print("[OS] HAL Initialized. Entering Standby.")
        gc.collect()

    @micropython.native
    def trigger_heartbeat(self):
        """Ultra-fast heartbeat toggle using Viper direct register access."""
        if self.use_viper_gpio:
            gpio_fast_toggle(LED_PIN_MASK)
        elif self.led:
            self.led.value(not self.led.value())

    @micropython.native
    def standby_loop(self):
        """Main non-blocking execution loop."""
        tick_count = 0
        
        # Check for terminal commands without blocking
        terminal = loaded_modules.get("hal.cyberdeck_bridge")
        
        while True:
            tick_count += 1
            if tick_count >= 20: # Approx 1 second
                self.trigger_heartbeat()
                tick_count = 0
                gc.collect()
                
            if terminal:
                cmd = terminal.check_for_commands()
                if cmd and self.role:
                    self.role.handle_command(cmd, terminal)
                    
            if self.role:
                self.role.standby_tick()
            
            # Small delay to prevent CPU thrashing
            time.sleep(0.05)
