from collections import Counter
from typing import Iterator, Dict, Any, List

class LogStatsCollector:
    """Collects and aggregates statistics from parsed log lines."""
    
    def __init__(self):
        self.total_requests = 0
        self.status_codes = Counter()
        self.ip_addresses = Counter()
        self.methods = Counter()

    def process_stream(self, data: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        """
        Processes a stream of log dictionaries, updating stats,
        and yielding the item back so it can be passed to exporters.
        """
        for item in data:
            self.total_requests += 1
            
            # These assume Nginx/Apache format fields are present.
            # A more generic version might require specifying which fields to track.
            if 'status' in item:
                self.status_codes[item['status']] += 1
            if 'ip' in item:
                self.ip_addresses[item['ip']] += 1
            if 'method' in item:
                self.methods[item['method']] += 1
                
            yield item

    def print_report(self):
        """Prints a human-readable summary report to stdout."""
        print(f"--- Log Statistics Report ---")
        print(f"Total Requests Processed: {self.total_requests}")
        
        print("\nTop 5 IP Addresses:")
        for ip, count in self.ip_addresses.most_common(5):
            print(f"  {ip}: {count}")
            
        print("\nStatus Codes:")
        for status, count in self.status_codes.most_common():
            print(f"  {status}: {count}")
            
        print("\nHTTP Methods:")
        for method, count in self.methods.most_common():
            print(f"  {method}: {count}")

        print("-----------------------------")
