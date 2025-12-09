from re import Pattern
from typing import Any

from multiversx_logs_parser_tools.aho_corasik_parser import AhoCorasickParser

from .counter_structures import CounterData


class CounterParser(AhoCorasickParser):
    def __init__(self):
        super().__init__()
        self.counters = CounterData()

    def get_patterns(self) -> list[tuple[Pattern[str], int]]:
        patterns = []
        patterns.append(('INFO', 0))
        patterns.append(('TRACE', 1))
        patterns.append(('DEBUG', 2))
        patterns.append(('WARN', 3))
        patterns.append(('ERROR', 4))

        return patterns

    def initialize_checker(self) -> None:
        self.counters = CounterData()

    def process_match(self, line: str, end_index: int, pattern_idx: int, args: dict[str, str]) -> dict[str, Any]:
        parsed = super().process_match(line, end_index, pattern_idx, args)
        return parsed

    def process_parsed_entry(self, parsed_entry: dict[str, Any], args: dict[str, str]) -> None:
        level = parsed_entry.get('logger_level', 'UNKNOWN')
        message = parsed_entry.get('message', '')

        if message:
            self.counters.add_message(level, message)

    def should_parse_line(self, pattern: Pattern[str]) -> bool:
        return True
