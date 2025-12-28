import argparse
import sys
import time
from src.utils.logger import get_logger
from src.utils.config_loader import ConfigLoader
from src.engine import MonitorEngine
from src.reporting.console_report import ConsoleReporter
from src.reporting.json_report import JsonReporter
from src.reporting.html_report import HtmlReporter

def main():
    logger = get_logger("Main")
    
    # 1. Parse Arguments
    parser = argparse.ArgumentParser(description="Middleware Health & Integration Monitor")
    parser.add_argument('--config', default='config/services.yaml', help='Path to configuration file')
    parser.add_argument('--no-html', action='store_true', help='Disable HTML report generation')
    parser.add_argument('--web', action='store_true', help='Run in Web Server mode')
    args = parser.parse_args()

    logger.info("Starting Middleware Health Monitor...")

    # 2. Load Configuration
    try:
        loader = ConfigLoader(args.config)
        config = loader.load_config()
    except Exception as e:
        logger.critical(f"Failed to load configuration: {e}")
        sys.exit(1)

    # 3. Web Mode
    if args.web:
        try:
            # Lazy import to avoid installing flask if not using web mode (optional, but good practice)
            # though we put it in requirements, so standard import is fine.
            from src.web_server import run_server
            run_server(config)
            return # Exit after server stops
        except ImportError:
            logger.critical("Flask module not found. Please run 'pip install flask' to use --web mode.")
            sys.exit(1)

    # 4. CLI Mode - Execution
    engine = MonitorEngine()
    results = engine.run_checks(config.get('services', []))

    # 5. Reporting
    
    # Console
    ConsoleReporter.generate_report(results)

    # JSON
    json_reporter = JsonReporter()
    json_path = json_reporter.generate_report(results)
    logger.info(f"JSON report saved to: {json_path}")

    # HTML
    if not args.no_html:
        try:
            html_reporter = HtmlReporter()
            html_path = html_reporter.generate_report(results)
            logger.info(f"HTML dashboard saved to: {html_path}")
        except Exception as e:
            logger.error(f"Failed to generate HTML report: {e}")

    logger.info("Health check completed.")

if __name__ == "__main__":
    main()
