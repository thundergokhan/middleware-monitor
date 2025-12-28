from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash, Response
from src.utils.logger import get_logger
from src.engine import MonitorEngine
from functools import wraps
import time
import os
import csv
import io

app = Flask(__name__, template_folder='reporting/templates')
app.secret_key = 'enterprise_secret_key_v2'

# Global vars
monitor_engine = None
service_config = [] 

# --- Auth Decorator ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Routes ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'admin123':
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/')
@login_required # Secured
def dashboard():
    """
    Renders the HTML status dashboard.
    """
    # Reload services from DB to get latest updates
    current_services = monitor_engine.db.get_services()
    if not current_services:
        # Fallback to file config configuration if DB is empty
        current_services = service_config

    results = monitor_engine.run_checks(current_services)
    
    summary = {
        "total": len(results),
        "passed": sum(1 for r in results if r['status']),
        "failed": sum(1 for r in results if not r['status']),
        "status_class": "success" if all(r['status'] for r in results) else "danger"
    }

    return render_template('dashboard.html', 
                         results=results, 
                         summary=summary,
                         title="Enterprise Monitor v2.0",
                         generated_at=time.strftime("%Y-%m-%d %H:%M:%S"))

@app.route('/api/health')
def api_health():
    current_services = monitor_engine.db.get_services() or service_config
    results = monitor_engine.run_checks(current_services)
    return jsonify({
        "timestamp": time.time(),
        "services": len(results),
        "results": results
    })

@app.route('/api/history/<path:service_name>')
def api_history(service_name):
    history = monitor_engine.db.get_history(service_name, limit=20)
    return jsonify(history)

@app.route('/metrics')
def metrics():
    current_services = monitor_engine.db.get_services() or service_config
    results = monitor_engine.run_checks(current_services)
    lines = []
    lines.append("# HELP middleware_up Service Reachability Status (1=Up, 0=Down)")
    lines.append("# TYPE middleware_up gauge")
    lines.append("# HELP middleware_latency_seconds Service Response Time")
    lines.append("# TYPE middleware_latency_seconds gauge")
    
    for r in results:
        safe_name = r['name'].replace(' ', '_').replace('(', '').replace(')', '')
        s_type = r['type']
        val = 1 if r['status'] else 0
        lines.append(f'middleware_up{{service="{safe_name}", type="{s_type}"}} {val}')
        lines.append(f'middleware_latency_seconds{{service="{safe_name}", type="{s_type}"}} {r["response_time"]}')

    return "\n".join(lines), 200, {'Content-Type': 'text/plain; charset=utf-8'}

@app.route('/api/export')
@login_required
def export_data():
    """
    Exports current status to CSV.
    """
    current_services = monitor_engine.db.get_services() or service_config
    results = monitor_engine.run_checks(current_services)
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(['Service Name', 'Type', 'Status', 'Response Time (s)', 'SLA Status', 'Message', 'Timestamp'])
    
    # Data
    for r in results:
        writer.writerow([
            r['name'], 
            r['type'], 
            'UP' if r['status'] else 'DOWN', 
            r['response_time'], 
            r.get('sla_status', 'N/A'),
            r['message'],
            time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        ])
        
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=middleware_report.csv"}
    )

# --- Settings / Admin Routes ---

@app.route('/settings')
@login_required
def settings():
    services = monitor_engine.db.get_services()
    return render_template('settings.html', services=services)

@app.route('/settings/add', methods=['POST'])
@login_required
def settings_add():
    name = request.form['name']
    s_type = request.form['type']
    endpoint = request.form['endpoint']
    sla = float(request.form.get('sla', 1.0))
    monitor_engine.db.add_service(name, s_type, endpoint, sla)
    flash(f'Service {name} added.')
    return redirect(url_for('settings'))

@app.route('/settings/delete', methods=['POST'])
@login_required
def settings_delete():
    name = request.form['name']
    monitor_engine.db.delete_service(name)
    flash(f'Service {name} deleted.')
    return redirect(url_for('settings'))

# --- Main Runner ---

def configure_server(config):
    global monitor_engine, service_config, logger
    service_config = config.get('services', [])
    monitor_engine = MonitorEngine()
    logger = get_logger("WebServer")
    
    # Auto-Migration: If DB is empty, populate from YAML
    existing = monitor_engine.db.get_services()
    if not existing and service_config:
        logger.info("Migrating YAML config to Database...")
        for s in service_config:
            # Handle different keys for different types
            endpoint = s.get('url') or s.get('wsdl') or s.get('queue_name') or 'unknown'
            monitor_engine.db.add_service(s['name'], s['type'].upper(), endpoint, s.get('sla_threshold', 1.0))

app.secret_key = 'super_secret_key' # Required for flash messages

def run_server(config, host='0.0.0.0', port=5000):
    configure_server(config)
    logger.info(f"Starting Web Server at http://{host}:{port}")
    app.run(host=host, port=port, debug=False)
