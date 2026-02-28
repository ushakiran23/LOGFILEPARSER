import csv
import json
from typing import Iterator, Dict, Any

def export_to_csv(data: Iterator[Dict[str, Any]], filepath: str):
    """Exports a stream of parsed log dictionaries to a CSV file."""
    # We need to figure out fieldnames from the first item
    try:
        first_item = next(data)
    except StopIteration:
        return # No data to write

    fieldnames = list(first_item.keys())
    
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(first_item)
        for item in data:
            writer.writerow(item)

def export_to_json(data: Iterator[Dict[str, Any]], filepath: str):
    """Exports a stream of parsed log dictionaries to a JSON file."""
    # To avoid loading everything into memory, we write a JSON array manually
    with open(filepath, 'w', encoding='utf-8') as jsonfile:
        jsonfile.write("[\n")
        first = True
        for item in data:
            if not first:
                jsonfile.write(",\n")
            json.dump(item, jsonfile)
            first = False
        jsonfile.write("\n]\n")
