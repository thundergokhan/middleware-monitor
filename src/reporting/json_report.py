import json
import os
import time

class JsonReporter:
    """
    Exports health check results to a JSON file.
    """

    def __init__(self, output_dir='reports'):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_report(self, results):
        """
        Writes results to results.json (overwriting previous by default for latest status,
        or unique name if preferred. For this tool, we keep a 'latest' file and a timestamped one).
        """
        report_data = {
            "timestamp": time.time(),
            "generated_at": time.ctime(),
            "services_checked": len(results),
            "results": results
        }

        # Save latest
        latest_path = os.path.join(self.output_dir, 'latest_health.json')
        with open(latest_path, 'w') as f:
            json.dump(report_data, f, indent=4)

        return latest_path
