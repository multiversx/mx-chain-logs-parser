from abc import ABC, abstractmethod
from re import Pattern
from typing import Any

import ahocorasick
from ahocorasick import Automaton

from .entry_parser import EntryParser


class AhoCorasickParser(ABC):
    def __init__(self):
        self.initialize_checker()
        self.entry_parser = EntryParser(node_name='')
        # Create the automaton & add patterns
        self.automaton: Automaton = ahocorasick.Automaton()
        for pattern, index in self.get_patterns():
            self.automaton.add_word(pattern, index)
        self.automaton.make_automaton()

    @abstractmethod
    def get_patterns(self) -> list[tuple[Pattern[str], int]]:
        return []

    @abstractmethod
    def initialize_checker(self) -> None:
        pass

    @abstractmethod
    def process_match(self, line: str, end_index: int, pattern_idx: int, args: dict[str, str]) -> dict[str, Any]:
        result = {}
        if self.should_parse_line(self.get_patterns()[pattern_idx][0]):
            result = self.entry_parser.parse_log_entry(line)
        return result

    @abstractmethod
    def process_parsed_entry(self, parsed_entry: dict[str, Any], args: dict[str, str]) -> None:
        pass

    @abstractmethod
    def should_parse_line(self, pattern: Pattern[str]) -> bool:
        pass

    def parse(self, file: list[str], args: dict[str, str]):
        for line in file:
            matches: list[tuple[int, int]] = list(self.automaton.iter(line))
            for end_index, pattern_idx in matches:
                result = self.process_match(line, end_index, pattern_idx, args)
                if result:
                    self.process_parsed_entry(result, args)
