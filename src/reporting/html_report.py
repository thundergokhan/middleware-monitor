import os
from jinja2 import Environment, FileSystemLoader
import time

class HtmlReporter:
    """
    Generates a rich HTML dasboard using Jinja2 templates.
    """

    def __init__(self, output_dir='reports', template_dir='src/reporting/templates'):
        self.output_dir = output_dir
        self.template_dir = template_dir
        os.makedirs(self.output_dir, exist_ok=True)
        # We assume the template exists.
        self.env = Environment(loader=FileSystemLoader(os.getcwd())) # Loading relative to CWD for simplicity

    def generate_report(self, results):
        template_path = os.path.join('src', 'reporting', 'templates', 'dashboard.html')
        
        # Calculate summary stats
        total = len(results)
        passed = sum(1 for r in results if r['status'])
        failed = total - passed
        
        context = {
            "title": "Middleware Health Monitor",
            "generated_at": time.ctime(),
            "results": results,
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "status_class": "success" if failed == 0 else "danger"
            }
        }

        # Load template
        # Note: FileSystemLoader root is cwd, so we pass the full relative path
        template = self.env.get_template(template_path.replace('\\', '/')) 
        
        html_content = template.render(context)
        
        output_file = os.path.join(self.output_dir, 'dashboard.html')
        with open(output_file, 'w') as f:
            f.write(html_content)
            
        return output_file
