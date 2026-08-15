from core.roles.base_role import BaseRole
import json

class Ros2Shard(BaseRole):
    """
    Universal Pub/Sub Template for the ROS2 Bridge Shard.
    Acts as a message broker between the ESP32 hardware and the ROS2 Host Robot.
    """
    def __init__(self, config):
        super().__init__(config)
        self.terminal = None # Will store reference to the USB bridge
        self.tick_counter = 0
        
    def handle_command(self, payload_string, terminal):
        """
        Parses incoming JSON payloads from the ROS2 Host.
        Expected format: {"topic": "motor_cmd", "msg": {"left": 255}}
        """
        self.terminal = terminal # Store reference for future publishing
        
        if not payload_string:
            return False
            
        try:
            payload = json.loads(payload_string)
            topic = payload.get("topic")
            msg = payload.get("msg", {})
            
            # --- TOPIC ROUTER ---
            if topic == "ping":
                self.publish("pong", {"status": "online"})
                
            elif topic == "set_pwm":
                # Example: {"topic": "set_pwm", "msg": {"pin": 5, "duty": 512}}
                # TODO: Implement Viper PWM driver here
                pass
                
            else:
                self.publish("error", {"reason": "Unknown topic", "topic": topic})
                
        except ValueError:
            self.publish("error", {"reason": "Invalid JSON payload"})
            
        return True
        
    def publish(self, topic, msg_dict):
        """
        Helper method to push telemetry back to the ROS2 Host.
        """
        if self.terminal:
            self.terminal.send_response({"topic": topic, "msg": msg_dict})
        
    def standby_tick(self):
        """
        Autonomous loop for reading sensors and publishing telemetry.
        """
        self.tick_counter += 1
        
        # Publish generic heartbeat telemetry every ~1 second (20 ticks)
        # if self.tick_counter % 20 == 0:
        #     self.publish("telemetry", {"status": "ok", "battery": "100%"})
        pass
