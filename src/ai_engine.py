import statistics
from collections import deque

class AnomalyDetector:
    def __init__(self, history_size=20):
        self.history_size = history_size
        self.history = {} # Key: ServiceName, Value: deque of floats

    def analyze(self, service_name, latency):
        """
        Analyzes the latency against historical data to detect anomalies.
        Returns: (is_anomaly, anomaly_score, message)
        """
        if service_name not in self.history:
            self.history[service_name] = deque(maxlen=self.history_size)
        
        data = self.history[service_name]
        
        # Need enough data points to be meaningful
        if len(data) < 5:
            data.append(latency)
            return False, 0.0, "Building Model"

        # Calculate Stats (Z-Score inspired)
        mean = statistics.mean(data)
        stdev = statistics.stdev(data) if len(data) > 1 else 0

        is_anomaly = False
        score = 0.0
        msg = "Optimal"

        # If stdev is tiny, even small deviations trigger alerts. 
        # So we enforce a minimum threshold of 0.1s deviation to be notable.
        if stdev < 0.05: 
            stdev = 0.05

        # Threshold: 2 Standard Deviations (95% confidence interval)
        threshold = mean + (2 * stdev)
        
        if latency > threshold:
            is_anomaly = True
            # Score: How many deviations away?
            score = (latency - mean) / stdev if stdev > 0 else 10.0
            msg = f"Latency spike detected (+{score:.1f}x deviation)"
        
        # Update history
        data.append(latency)
        
        return is_anomaly, score, msg
