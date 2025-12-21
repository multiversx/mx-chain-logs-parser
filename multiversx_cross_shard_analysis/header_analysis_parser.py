import json
from re import Pattern
from typing import Any

from multiversx_logs_parser_tools.aho_corasik_parser import AhoCorasickParser

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
        return patterns

    def initialize_checker(self) -> None:
        # Initialize any required state or variables for the checker
        self.parsed_headers.reset()

    def process_match(self, line: str, end_index: int, pattern_idx: int, args: dict[str, str]) -> dict[str, Any]:
        parsed = super().process_match(line, end_index, pattern_idx, args)
        # Additional processing specific to header checking can be added here
        if pattern_idx < 3 and 'parameters' in parsed:
            parameter = parsed.pop('parameters').split(' = ', 1)[1]
            header = json.loads(parameter)
            if pattern_idx < 2:
                self.parsed_headers.add_proposed_header(header)
            elif pattern_idx == 2:
                self.parsed_headers.add_committed_header(header)

        return {}

    def process_parsed_entry(self, parsed_entry: dict[str, Any], args: dict[str, str]) -> None:
        # Process the parsed log entry specific to header checking
        pass

    def should_parse_line(self, pattern: Pattern[str]) -> bool:
        # Determine if the line should be parsed based on the pattern
        return True
