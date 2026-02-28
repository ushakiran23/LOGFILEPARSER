import argparse
import sys
import threading
from src.parser import NginxLogParser, RegexLogParser
from src.exporters import export_to_csv, export_to_json
from src.stats import LogStatsCollector
from src.app import app

def create_parser():
    parser = argparse.ArgumentParser(description="Log File Parser and Analyzer")
    
    parser.add_argument("command", choices=["parse", "analyze", "serve"], help="Action to perform")
    
    # Make input_file optional when using "serve" command
    parser.add_argument("input_file", nargs="?", help="Path to the log file to parse (Not required for 'serve')")
    
    parser.add_argument("--format", choices=["nginx", "regex"], default="nginx", help="Log format to parse")
    parser.add_argument("--regex", help="Custom regex pattern (required if --format regex)")
    
    parser.add_argument("--out", help="Output file path (e.g., output.csv or output.json)")
    parser.add_argument("--out-format", choices=["csv", "json"], help="Output format if writing to a file (implied by extension if not provided)")
    
    return parser

def main():
    arg_parser = create_parser()
    args = arg_parser.parse_args()
    
    # 0. Handle 'serve' command
    if args.command == "serve":
        print("Starting Log Dashboard Web Server...")
        print("Available at: http://127.0.0.1:5000")
        app.run(debug=False, port=5000)
        sys.exit(0)

    # Validate input_file for other commands
    if not args.input_file:
         print(f"Error: the following arguments are required: input_file (Unless using 'serve' command)")
         sys.exit(1)

    # 1. Choose the parser
    if args.format == "nginx":
        log_parser = NginxLogParser()
    elif args.format == "regex":
        if not args.regex:
            print("Error: --regex must be provided when --format is 'regex'")
            sys.exit(1)
        log_parser = RegexLogParser(args.regex)
        
    # 2. Setup the stream
    stream = log_parser.parse_file(args.input_file)
    
    # 3. Apply stats if analyzing
    stats_collector = None
    if args.command == "analyze":
        stats_collector = LogStatsCollector()
        stream = stats_collector.process_stream(stream)
        
    # 4. Handle output processing
    if args.out:
        out_format = args.out_format
        if not out_format:
            if args.out.endswith(".csv"):
                out_format = "csv"
            elif args.out.endswith(".json"):
                out_format = "json"
            else:
                print("Error: Could not determine output format from extension. Please specify --out-format.")
                sys.exit(1)
                
        # Consume the stream by exporting
        if out_format == "csv":
            export_to_csv(stream, args.out)
            print(f"Data successfully exported to {args.out}")
        elif out_format == "json":
            export_to_json(stream, args.out)
            print(f"Data successfully exported to {args.out}")

    else:
        # If no output file...
        if args.command == "analyze":
            # Consume stream to count stats
            for _ in stream:
                pass
        else:
            # Just parsing and printing to stdout
            for item in stream:
                print(item)
                
    # 5. Print stats if requested
    if stats_collector:
        stats_collector.print_report()

if __name__ == "__main__":
    main()
