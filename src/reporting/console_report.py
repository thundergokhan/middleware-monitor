from colorama import Fore, Style

class ConsoleReporter:
    """
    Generates a readable console summary of the health check results.
    """

    @staticmethod
    def generate_report(results):
        """
        Prints the results to stdout.
        
        Args:
            results (list): List of result dictionaries from monitors.
        """
        print(f"\n{Style.BRIGHT}Middleware Health Check Summary{Style.RESET_ALL}")
        print("=" * 60)
        print(f"{'Service Name':<30} | {'Type':<6} | {'Status':<10} | {'Time (s)':<8}")
        print("-" * 60)

        for res in results:
            status_color = Fore.GREEN if res['status'] else Fore.RED
            status_text = "PASS" if res['status'] else "FAIL"
            
            print(f"{res['name']:<30} | {res['type']:<6} | {status_color}{status_text:<10}{Style.RESET_ALL} | {res['response_time']:<8.4f}")
            if not res['status']:
                print(f"  {Fore.RED}Error: {res['message']}{Style.RESET_ALL}")

        print("-" * 60)
