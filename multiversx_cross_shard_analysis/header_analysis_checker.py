from argparse import Namespace
from typing import Any
from multiversx_logs_parser_tools.node_logs_checker import NodeLogsChecker

from .header_analysis_parser import HeaderAnalysisParser


class HeaderAnalysisChecker(NodeLogsChecker):
    def __init__(self, parser_cls: type[HeaderAnalysisParser], args: Namespace):
        self.node_parsed_headers = {}
        super().__init__(parser_cls, args)

    def initialize_checker(self, args):
        self.node_parsed_headers = {}
        return super().initialize_checker(args)

    def process_parsed_result(self):
        self.parsed = self.parser.parsed_headers.header_dictionary.copy()
        self.parser.initialize_checker()

    def post_process_node_logs(self):
        # Implement post-processing logic here
        self.write_node_json()
        pass

    def create_json_for_node(self) -> dict[str, Any]:
        return {
            "node_name": self.node_name,
            "run_name": self.run_name,
            "header_analysis": self.parsed
        }

    def reset_node(self, args: Namespace):
        super().reset_node(args)
        self.parsed = {'proposed_header': [], 'commited_header': []}
