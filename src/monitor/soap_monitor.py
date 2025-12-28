import time
import requests
from .base import BaseMonitor

class SoapMonitor(BaseMonitor):
    """
    Monitor for SOAP services.
    Supports Simulation Mode for demo purposes.
    Reference: For production, integrate with 'zeep' library.
    """

    def check_health(self):
        simulation_mode = self.service_config.get('simulation_mode', False)
        
        if simulation_mode:
            return self._run_simulation()
        else:
            return self._run_real_check()

    def _run_simulation(self):
        """
        Simulates a SOAP check logic.
        """
        start_time = time.time()
        # Simulate network latency
        time.sleep(0.12) 
        elapsed = time.time() - start_time
        
        self.logger.info(f"Simulating SOAP check for {self.name}")
        
        # Simulate success
        return self._generate_result(True, elapsed, "OK (Simulated WSDL Access)")

    def _run_real_check(self):
        """
        Performs a basic reachability check on the WSDL or Endpoint.
        In a full enterprise version, this would use the `zeep` client
        to actually call a 'ping' or 'echo' method.
        """
        url = self.service_config.get('url')
        wsdl = self.service_config.get('wsdl')
        target = wsdl if wsdl else url
        timeout = self.service_config.get('timeout', 10)

        start_time = time.time()
        try:
            self.logger.debug(f"Checking SOAP endpoint availability: {target}")
            # Simple GET on WSDL is often enough to prove the service is 'up' HTTP-wise
            response = requests.get(target, timeout=timeout)
            elapsed = time.time() - start_time

            if response.status_code == 200:
                 return self._generate_result(True, elapsed, f"OK (WSDL Reachable: {response.status_code})")
            else:
                 return self._generate_result(False, elapsed, f"Failed. Status: {response.status_code}")

        except requests.exceptions.RequestException as e:
            elapsed = time.time() - start_time
            return self._generate_result(False, elapsed, f"Connection Error: {str(e)}")
