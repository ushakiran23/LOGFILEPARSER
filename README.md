# Log File Parser

A robust, flexible, and performant Log File Parser built in Python. This tool ingests log files (like Nginx access logs), parses them into structured formats (CSV/JSON), and provides statistics.

## Project Structure

- `src/parser.py`: Contains the core parsing engine based on Regular Expressions. `NginxLogParser` handles standard combined log formats out-of-the-box.
- `src/exporters.py`: Handles exporting the parsed data stream to JSON or CSV.
- `src/stats.py`: Analyzes the flow of logs to count occurrences of IP addresses, HTTP status codes, and HTTP methods.
- `src/cli.py` & `main.py`: Command Line Interface for end-users.

## Installation

1. Requires Python 3.9+.
2. Clone this repository or copy the directory.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

The application uses a Command Line Interface (CLI):

```bash
python main.py {command} {input_file} [options]
```

### Commands
- `parse`: Just parse the logs and either print to stdout or output to a file.
- `analyze`: Parse the logs and generate/print an aggregate statistics report from the parsed data.

### Options
- `--format`: Specify `nginx` (default) or `regex`.
- `--regex`: If `--format regex`, provide the python re string here (must use named capturing groups, e.g., `(?P<ip>\S+)`).
- `--out`: Path to save the extracted data (e.g., `output.csv` or `output.json`).
- `--out-format`: Specifically set `csv` or `json`. If omitted, inferred from the `--out` file extension.

## Examples

### 1. View parsed Nginx logs on terminal
```bash
python main.py parse tests/sample_logs/test_nginx.log
```

### 2. Export parsed logs to CSV
```bash
python main.py parse tests/sample_logs/test_nginx.log --out output.csv
```

### 3. Analyze logs and view statistics
```bash
python main.py analyze tests/sample_logs/test_nginx.log --out parsed_logs.json
```

### 4. Custom Regex Parsing
Suppose you have a custom log: `[INFO] User logged in - 10:45 AM`
```bash
python main.py parse mylog.txt --format regex --regex "^\[(?P<level>\w+)\] (?P<msg>.+) - (?P<time>.+)$"
```

### 5. Launch Web Dashboard
View an interactive UI of your log statistics right in your browser!
```bash
python main.py serve
```
Then navigate to http://127.0.0.1:5000 in your browser.

## Running Tests
Run `pytest` in the project root:

```bash
pytest tests/
```
