import re
from typing import Iterator, Dict, Any, Optional
from abc import ABC, abstractmethod


class BaseLogParser(ABC):
    """Abstract base class for all log parsers."""
    
    @abstractmethod
    def parse_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Parses a single log line into a dictionary. Returns None if it fails to parse."""
        pass

    def parse_file(self, filepath: str) -> Iterator[Dict[str, Any]]:
        """Yields parsed log lines from a file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                parsed = self.parse_line(line.strip())
                if parsed:
                    yield parsed


class RegexLogParser(BaseLogParser):
    """A generic log parser that uses a regular expression with named groups."""
    
    def __init__(self, pattern: str):
        self.pattern = re.compile(pattern)

    def parse_line(self, line: str) -> Optional[Dict[str, Any]]:
        match = self.pattern.match(line)
        if match:
            return match.groupdict()
        return None


class NginxLogParser(RegexLogParser):
    """
    A specialized parser for standard Nginx/Apache access logs.
    Format typically resembles:
    127.0.0.1 - - [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326
    """
    
    # Common Log Format (CLF) + User Agent etc (Combined Log Format often used by Nginx)
    NGINX_PATTERN = r'^(?P<ip>\S+) \S+ \S+ \[(?P<time>.*?)\] "(?P<method>\S+) (?P<url>\S+) (?P<protocol>\S+)" (?P<status>\d{3}) (?P<size>\S+)(?: "(?P<referrer>.*?)" "(?P<user_agent>.*?)")?$'

    def __init__(self):
        super().__init__(self.NGINX_PATTERN)
