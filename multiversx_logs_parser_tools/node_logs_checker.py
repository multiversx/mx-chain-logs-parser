
try:
    # When this module is imported as part of a package
    from .aho_corasick_parser import AhoCorasickParser
except Exception:
    # Fallback when running the script directly (not as a package)
    from aho_corasick_parser import AhoCorasickParser

import argparse
import json
import os
import tarfile
from pathlib import Path
from typing import IO, Any, Generic, Type, TypeVar

"""Abstract Base Class for Node Logs Checker."""


P = TypeVar("P", bound=AhoCorasickParser)


class NodeLogsChecker(Generic[P]):
    def __init__(self, parser_cls: Type[P], args: argparse.Namespace):
        self.parser: P = parser_cls()
        self.initialize_checker(args)

    """ Parses a .log file for the given node. """

    def process_parsed_result(self):
        pass

    """ Post-process the node logs after all log files have been parsed. """

    def post_process_node_logs(self):
        pass

    def initialize_checker(self, args: argparse.Namespace):
        pass

    def create_json_for_node(self) -> dict[str, Any]:
        return {}

    def reset_node(self, args: argparse.Namespace):
        self.node_name = args.node_name if args.node_name else 'unknown-node'
        self.run_name = args.run_name if args.run_name else 'unknown-run'

    def handle_node_from_archive(self, tar_gz_contents: IO[bytes]):
        with tarfile.open(fileobj=tar_gz_contents, mode='r:gz') as logs_archive:
            # sort logs in alphabetic/chronological order
            sorted_members = sorted(
                logs_archive.getmembers(),
                key=lambda member: member.name
            )

            # process all log files for the node
            for member in sorted_members:
                if member.name.startswith('logs/logs/') and member.name.endswith('.log'):
                    print("    Processing log file:", member.name)
                    raw_data = logs_archive.extractfile(member)
                    if not raw_data:
                        continue

                    with raw_data as f:
                        # Decode and pass an iterable (a list of lines)
                        log_lines = [line.decode("utf-8") for line in f]
                        self.parser.parse(log_lines, {})
                        self.process_parsed_result()

    def handle_node_from_folder(self, node_logs_path: str):
        files = sorted(Path(node_logs_path).glob('*.log'))
        for file in files:
            with open(file, 'r') as f:
                log_lines = f.readlines()
                self.parser.parse(log_lines, {})
                self.process_parsed_result()

    def write_node_json(self, path=''):
        if not path:
            node_reports_path = f'./Reports/{self.run_name}/Nodes'
            output_file = Path(f'{node_reports_path}/{self.node_name}_report.json')
            directory = os.path.dirname(output_file)
            Path(directory).mkdir(parents=True, exist_ok=True)
        else:
            output_file = Path(path + f'/{self.node_name}_report.json')
        with open(output_file, "w") as json_file:
            json.dump(self.create_json_for_node(), json_file, indent=4)

    @classmethod
    def from_args(cls: Type['NodeLogsChecker[P]'], parser_cls: Type[P], args: argparse.Namespace) -> 'NodeLogsChecker[P]':
        instance = cls(parser_cls, args)
        return instance
