import requests
import time
from .base import BaseMonitor

class RestMonitor(BaseMonitor):
    """
    Monitor for RESTful services.
    Checks HTTP status codes and response latency.
    """

    def check_health(self):
        url = self.service_config.get('url')
        timeout = self.service_config.get('timeout', 5)
        expected_status = self.service_config.get('expected_status', 200)
        verify_ssl = self.service_config.get('verify_ssl', True)

        start_time = time.time()
        try:
            self.logger.debug(f"Checking REST service: {url}")
            response = requests.get(url, timeout=timeout, verify=verify_ssl)
            elapsed = time.time() - start_time
            
            # Determine health based on status code
            # Allow for a range of 2xx success codes by default if just 200 is specified
            is_healthy = False
            msg = ""

            if response.status_code == expected_status:
                is_healthy = True
                msg = f"OK (Status: {response.status_code})"
            elif 200 <= response.status_code < 300 and expected_status == 200:
                # If we expected 200 but got another 2xx, we might consider it okay or strict.
                # For this monitor, let's be strict if the user specified a specific code, 
                # but generous if it matches general success.
                is_healthy = True
                msg = f"OK (Status: {response.status_code})"
            else:
                is_healthy = False
                msg = f"Failed. Expected {expected_status}, got {response.status_code}"

            return self._generate_result(is_healthy, elapsed, msg)

        except requests.exceptions.Timeout:
            elapsed = time.time() - start_time
            self.logger.warning(f"Timeout connecting to {url}")
            return self._generate_result(False, elapsed, f"Connection Timeout ({timeout}s)")
        except requests.exceptions.RequestException as e:
            elapsed = time.time() - start_time
            self.logger.error(f"Error connecting to {url}: {e}")
            return self._generate_result(False, elapsed, f"Connection Error: {str(e)}")
