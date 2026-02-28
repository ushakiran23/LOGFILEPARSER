import os
from flask import Flask, render_template, request, jsonify
from src.parser import NginxLogParser, RegexLogParser
from src.stats import LogStatsCollector

app = Flask(__name__)

# Directory where log files are stored
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests', 'sample_logs')

@app.route('/')
def index():
    """Render the main dashboard."""
    # Get available log files
    log_files = []
    if os.path.exists(LOG_DIR):
        log_files = [f for f in os.listdir(LOG_DIR) if f.endswith('.log')]
    
    return render_template('index.html', log_files=log_files)

@app.route('/api/analyze')
def analyze_log():
    """API endpoint to analyze a log file and return JSON stats."""
    filename = request.args.get('filename')
    
    if not filename:
        return jsonify({"error": "No filename provided"}), 400
        
    filepath = os.path.join(LOG_DIR, filename)
    if not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 404

    try:
        # Use our existing Nginx parser
        log_parser = NginxLogParser()
        stream = log_parser.parse_file(filepath)
        
        # Collect stats
        stats_collector = LogStatsCollector()
        list(stats_collector.process_stream(stream)) # Exhaust stream
        
        # Format the results for the frontend
        results = {
            "total_requests": stats_collector.total_requests,
            "ip_addresses": [{"ip": ip, "count": count} for ip, count in stats_collector.ip_addresses.most_common(10)],
            "status_codes": [{"status": status, "count": count} for status, count in stats_collector.status_codes.most_common()],
            "methods": [{"method": method, "count": count} for method, count in stats_collector.methods.most_common()]
        }
        
        return jsonify(results)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/logs')
def get_logs():
    """API endpoint to get parsed log lines."""
    filename = request.args.get('filename')
    limit = int(request.args.get('limit', 50))
    
    if not filename:
        return jsonify({"error": "No filename provided"}), 400
        
    filepath = os.path.join(LOG_DIR, filename)
    if not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 404
        
    try:
        log_parser = NginxLogParser()
        stream = log_parser.parse_file(filepath)
        
        # Grab the first 'limit' lines
        lines = []
        for i, item in enumerate(stream):
            if i >= limit:
                break
            lines.append(item)
            
        return jsonify(lines)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
