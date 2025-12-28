from flask import Flask, render_template_string, jsonify
import time
from src.engine import MonitorEngine
from src.utils.logger import get_logger

# We reuse the existing Jinja2 template logic but serve it via Flask
# For simplicity in this structure, we'll read the template file manually 
# and pass it to render_template_string or configure Flask's template folder.
# Given the directory structure, let's configure Flask to use the existing templates dir.

app = Flask(__name__, template_folder='reporting/templates')
logger = get_logger("WebServer")

# Global variables to hold config
service_config = []
monitor_engine = MonitorEngine()

def configure_server(config):
    global service_config
    service_config = config.get('services', [])

@app.route('/')
def dashboard():
    """
    Simulates the HTML report generation but on-demand.
    """
    start_time = time.time()
    results = monitor_engine.run_checks(service_config)
    elapsed = time.time() - start_time
    logger.info(f"Web request processed in {elapsed:.4f}s")

    # Reuse the same template context structure as the HtmlReporter
    total = len(results)
    passed = sum(1 for r in results if r['status'])
    failed = total - passed

    context = {
        "title": "Middleware Monitor - Live Dashboard",
        "generated_at": time.ctime(),
        "results": results,
        "summary": {
            "total": total,
            "passed": passed,
            "failed": failed,
            "status_class": "success" if failed == 0 else "danger"
        }
    }

    # We need to read the template file because Flask expects templates in a specific `templates` folder
    # relative to the app, but our structure is `src/reporting/templates`.
    # To avoid moving files, I will read the file content and use render_template_string.
    try:
        with open('src/reporting/templates/dashboard.html', 'r') as f:
            template_content = f.read()
        return render_template_string(template_content, **context)
    except Exception as e:
        return f"Error loading template: {e}", 500

@app.route('/api/health')
def api_health():
    """
    Returns JSON representation of the health.
    """
    results = monitor_engine.run_checks(service_config)
    return jsonify({
        "timestamp": time.time(),
        "services": len(results),
        "results": results
    })

@app.route('/api/history/<path:service_name>')
def api_history(service_name):
    """
    Returns historical data for a specific service.
    """
    history = monitor_engine.db.get_history(service_name, limit=20)
    return jsonify(history)

@app.route('/metrics')
def metrics():
    """
    Prometheus metrics exporter.
    """
    results = monitor_engine.run_checks(service_config)
    lines = []
    
    # Help and Type definitions
    lines.append("# HELP middleware_up Service Reachability Status (1=Up, 0=Down)")
    lines.append("# TYPE middleware_up gauge")
    lines.append("# HELP middleware_latency_seconds Service Response Time")
    lines.append("# TYPE middleware_latency_seconds gauge")
    
    for r in results:
        # Prometheus labels need to be clean
        safe_name = r['name'].replace(' ', '_').replace('(', '').replace(')', '')
        s_type = r['type']
        
        # Metric: Up/Down
        val = 1 if r['status'] else 0
        lines.append(f'middleware_up{{service="{safe_name}", type="{s_type}"}} {val}')
        
        # Metric: Latency
        lines.append(f'middleware_latency_seconds{{service="{safe_name}", type="{s_type}"}} {r["response_time"]}')

    return "\n".join(lines), 200, {'Content-Type': 'text/plain; charset=utf-8'}

def run_server(config, host='0.0.0.0', port=5000):
    configure_server(config)
    logger.info(f"Starting Web Server at http://{host}:{port}")
    app.run(host=host, port=port, debug=False)
