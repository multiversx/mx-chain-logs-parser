from argparse import Namespace
from typing import Any

from multiversx_logs_parser_tools.node_logs_checker import NodeLogsChecker

from .counter_parser import CounterData, CounterParser


class CounterChecker(NodeLogsChecker):

    def __init__(self, parser_cls: type[CounterParser], args: Namespace):
        super().__init__(parser_cls, args)

    def initialize_checker(self, args):
        self.parsed = CounterData()
        return super().initialize_checker(args)

    def process_parsed_result(self):
        self.parsed.add_counted_messages(self.parser.counters)
        self.parser.initialize_checker()

    def post_process_node_logs(self):
        # Implement post-processing logic here
        self.write_node_json(path=f'./Reports/{self.run_name}/LogEntryCounter')

    def create_json_for_node(self) -> dict[str, Any]:
        for log_level, messages in self.parsed.counter_dictionary.items():
            messages_sorted = dict(sorted(messages.items(), key=lambda item: item[1], reverse=True))
            self.parsed.counter_dictionary[log_level] = messages_sorted
        return {
            "node_name": self.node_name,
            "run_name": self.run_name,
            "counter": self.parsed.counter_dictionary
        }

    def reset_node(self, args: Namespace):
        super().reset_node(args)
        self.parsed = CounterData()
