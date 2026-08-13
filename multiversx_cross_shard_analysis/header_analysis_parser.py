import json
from re import Pattern
import re
from typing import Any

from multiversx_logs_parser_tools.aho_corasick_parser import AhoCorasickParser

from .header_structures import HeaderData


class HeaderAnalysisParser(AhoCorasickParser):
    def __init__(self):
        self.parsed_headers = HeaderData()
        super().__init__()

    def get_patterns(self) -> list[tuple[Pattern[str], int]]:
        patterns = []
        patterns.append(('Proposed header received', 0))
        patterns.append(('Proposed header sent', 1))
        patterns.append(('Proposed header committed', 2))
        patterns.append(('meta block has been committed successfully', 3))
        return patterns

    def initialize_checker(self) -> None:
        # Initialize any required state or variables for the checker
        self.parsed_headers.reset()

    def process_match(self, line: str, end_index: int, pattern_idx: int, args: dict[str, str]) -> dict[str, Any]:
        parsed = super().process_match(line, end_index, pattern_idx, args)

        # Additional processing specific to header checking can be added here
        if pattern_idx < 3 and 'parameters' in parsed:
            parts = parsed.pop('parameters').split(' = ', 1)
            if len(parts) < 2 or not parts[1]:
                print("    Warning: could not parse header parameters from line:", line.strip())
                return {}
            try:
                header = json.loads(parts[1])
            except json.JSONDecodeError:
                print("    Warning: could not decode header JSON from line:", line.strip())
                return {}
            if pattern_idx < 2:
                self.parsed_headers.add_proposed_header(header)
            elif pattern_idx == 2:
                self.parsed_headers.add_committed_header(header)
        elif pattern_idx == 3:
            parameter = parsed.pop('parameters')
            match = re.search(r'shard\s*=\s*(?P<shard>\d+)\s+round\s*=\s*(?P<round>\d+)\s+nonce\s*=\s*(?P<nonce>\d+)\s+hash\s*=\s*(?P<hash>[0-9a-fA-F]{64})', parameter)
            if not match:
                print("    Warning: could not parse meta block commit info from parameters:", parameter)
                return {}
            metaBlockInfo = match.groupdict()
            self.parsed_headers.metaheaders[metaBlockInfo['hash']] = int(metaBlockInfo['nonce'])
        return {}

    def process_parsed_entry(self, parsed_entry: dict[str, Any], args: dict[str, str]) -> None:
        # Process the parsed log entry specific to header checking
        pass

    def should_parse_line(self, pattern: Pattern[str]) -> bool:
        # Determine if the line should be parsed based on the pattern
        return True
