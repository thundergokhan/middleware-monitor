import time
import random
from .base import BaseMonitor

class MqMonitor(BaseMonitor):
    """
    Monitor for Message Queues (IBM MQ / RabbitMQ style).
    Supports Simulation Mode.
    """

    def check_health(self):
        simulation_mode = self.service_config.get('simulation_mode', False)
        
        if simulation_mode:
            return self._run_simulation()
        else:
            return self._generate_result(False, 0, "Real MQ check not implemented in this demo (Requires pymqi/pika)")

    def _run_simulation(self):
        """
        Simulates MQ connectivity and Queue Depth check.
        """
        start_time = time.time()
        host = self.service_config.get('host', 'localhost')
        port = self.service_config.get('port', 1414)
        queue = self.service_config.get('queue_name', 'UNKNOWN.Q')
        
        self.logger.info(f"Simulating MQ check for {host}:{port} ({queue})")
        
        # Simulate latency
        time.sleep(0.05)
        elapsed = time.time() - start_time
        
        # Simulate dynamic queue depth
        # Most of the time it's healthy, sometimes it's "backed up"
        # For determinism in this demo, we'll keep it healthy unless specific config triggers failure
        # (or just random for 'aliveness')
        
        current_depth = random.randint(0, 50)
        
        # Arbitrary threshold for health in this simulation
        threshold = 1000 
        
        if current_depth < threshold:
            msg = f"OK (Connected, Depth: {current_depth})"
            return self._generate_result(True, elapsed, msg)
        else:
            msg = f"Warning (Depth High: {current_depth})"
            # In some systems high depth is failure, others warning. We'll mark as Unhealthy for demo if extremely high
            return self._generate_result(False, elapsed, msg)
