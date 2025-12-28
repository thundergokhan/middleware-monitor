from concurrent.futures import ThreadPoolExecutor, as_completed
from src.utils.logger import get_logger
from src.monitor.rest_monitor import RestMonitor
from src.monitor.soap_monitor import SoapMonitor
from src.monitor.mq_monitor import MqMonitor
from src.db import Database

class MonitorEngine:
    """
    Encapsulates the logic to run health checks on a list of services.
    Supports Parallel Execution.
    """
    
    def __init__(self):
        self.logger = get_logger("MonitorEngine")
        self.db = Database()

    def check_service(self, service):
        """
        Helper method to check a single service. Designed for threading.
        """
        s_type = service.get('type').upper()
        monitor = None

        if s_type == 'REST':
            monitor = RestMonitor(service)
        elif s_type == 'SOAP':
            monitor = SoapMonitor(service)
        elif s_type == 'MQ':
            monitor = MqMonitor(service)
        else:
            self.logger.warning(f"Unknown service type '{s_type}' for service '{service.get('name')}'")
            return None

        if monitor:
            try:
                result = monitor.check_health()
                
                # SLA Grading Logic
                if result['status']:
                    sla_limit = service.get('sla_threshold', 1.0)
                    if result['response_time'] > sla_limit:
                        result['sla_status'] = 'DEGRADED'
                        result['message'] += f" (Slow: >{sla_limit}s)"
                    else:
                        result['sla_status'] = 'HEALTHY'
                else:
                    result['sla_status'] = 'DOWN'
                    self._trigger_alert(result) # Alert on DOWN

                self.db.save_result(result)
                return result
            except Exception as e:
                self.logger.error(f"Unexpected error checking {service.get('name')}: {e}")
                err_result = {
                    "name": service.get('name', 'Unknown'),
                    "type": s_type,
                    "status": False,
                    "response_time": 0,
                    "message": f"Unexpected Error: {str(e)}",
                    "timestamp": 0,
                    "config": service,
                    "sla_status": "DOWN"
                }
                self.db.save_result(err_result)
                self._trigger_alert(err_result)
                return err_result
        return None

    def _trigger_alert(self, result):
        """
        Simple alerting stub. In production, this would send an email/slack.
        """
        if not result['status']:
            self.logger.critical(f"ALERT: Service {result['name']} is DOWN! Msg: {result['message']}")

    def run_checks(self, services):
        """
        Runs health checks in PARALLEL.
        """
        results = []
        # Use ThreadPoolExecutor for I/O bound tasks
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_service = {executor.submit(self.check_service, s): s for s in services}
            
            for future in as_completed(future_to_service):
                try:
                    res = future.result()
                    if res:
                        results.append(res)
                except Exception as exc:
                    self.logger.error(f"Service check generated an exception: {exc}")
        
        return results
