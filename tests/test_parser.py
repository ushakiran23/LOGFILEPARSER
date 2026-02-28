import pytest
import os
from src.parser import NginxLogParser, RegexLogParser
from src.stats import LogStatsCollector

def test_nginx_parser_valid_line():
    parser = NginxLogParser()
    line = '127.0.0.1 - - [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326'
    result = parser.parse_line(line)
    
    assert result is not None
    assert result['ip'] == '127.0.0.1'
    assert result['method'] == 'GET'
    assert result['url'] == '/apache_pb.gif'
    assert result['status'] == '200'
    assert result['size'] == '2326'

def test_nginx_parser_with_user_agent():
    parser = NginxLogParser()
    line = '192.168.1.1 - admin [10/Oct/2000:14:02:00 -0700] "POST /login HTTP/1.1" 401 128 "http://example.com/login" "Mozilla/5.0"'
    result = parser.parse_line(line)
    
    assert result is not None
    assert result['ip'] == '192.168.1.1'
    assert result['status'] == '401'
    assert result['referrer'] == 'http://example.com/login'
    assert result['user_agent'] == 'Mozilla/5.0'

def test_nginx_parser_invalid_line():
    parser = NginxLogParser()
    line = 'This is not a log line'
    result = parser.parse_line(line)
    assert result is None

def test_regex_parser():
    parser = RegexLogParser(r"^(?P<timestamp>\d+) \[(?P<level>\w+)\] (?P<msg>.*)$")
    line = "1674060800 [INFO] System started"
    result = parser.parse_line(line)
    
    assert result is not None
    assert result['timestamp'] == '1674060800'
    assert result['level'] == 'INFO'
    assert result['msg'] == 'System started'

def test_stats_collector():
    collector = LogStatsCollector()
    data = [
        {'ip': '1.1.1.1', 'status': '200', 'method': 'GET'},
        {'ip': '1.1.1.1', 'status': '404', 'method': 'GET'},
        {'ip': '2.2.2.2', 'status': '200', 'method': 'POST'},
    ]
    
    # Process stream converts to list to exhaust the generator
    list(collector.process_stream(iter(data)))
    
    assert collector.total_requests == 3
    assert collector.ip_addresses['1.1.1.1'] == 2
    assert collector.ip_addresses['2.2.2.2'] == 1
    assert collector.status_codes['200'] == 2
    assert collector.status_codes['404'] == 1
    assert collector.methods['GET'] == 2
    assert collector.methods['POST'] == 1
