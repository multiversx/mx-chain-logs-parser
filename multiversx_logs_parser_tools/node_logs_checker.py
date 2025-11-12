

from helpers import validate_folder_path

from typing import IO, Any
import tarfile
from pathlib import Path
import os
import json
import argparse
from abc import ABC, abstractmethod


"""Abstract Base Class for Node Logs Checker."""


class NodeLogsChecker(ABC):
    def __init__(self, args: dict[str, Any]):
        self.report_name = ''
        self.node_name = args.get('node_name', 'unknown-node')
        self.run_name = args.get('run_name', 'unknown-run')

        self.initialize_checker(args)

    """ Parses a .log file for the given node. """
    @abstractmethod
    def process_log_file(self, log_lines: list[str]):
        pass

    """ Post-process the node logs after all log files have been parsed. """
    @abstractmethod
    def post_process_node_logs(self):
        pass

    @abstractmethod
    def initialize_checker(self, args: dict[str, Any]):
        pass

    @abstractmethod
    def create_json_for_node(self) -> dict[str, Any]:
        pass

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
                    raw_data = logs_archive.extractfile(member)
                    if not raw_data:
                        continue

                    with raw_data as f:
                        # Decode and pass an iterable (a list of lines)
                        log_lines = (line.decode("utf-8") for line in f)  # Generator expression
                        self.process_log_file(log_lines)

    def handle_node_from_folder(self, node_logs_path: str):
        files = sorted(Path(node_logs_path).glob('*.log'))
        for file in files:
            with open(file, 'r') as f:
                log_lines = f.readlines()
                self.process_log_file(log_lines)

    def write_node_json(self, path=''):
        if not path:
            node_reports_path = './Reports/Nodes'
            output_file = Path(f'{node_reports_path}/{self.run_name}/{self.node_name}_report.json')
            directory = os.path.dirname(output_file)
            Path(directory).mkdir(parents=True, exist_ok=True)
        else:
            output_file = Path(path + f'/{self.node_name}_report.json')
        with open(output_file, "w") as json_file:
            json.dump(self.create_json_for_node(), json_file, indent=4)


if __name__ == "__main__":
    # Should be run either from node logs folder or with [path] parameter

    parser = argparse.ArgumentParser(
        description='''
            Runs logs check for the selected node. Example script:

                python ansible/templates/logs-checker/node_logs_checker.py --path=logsPath/node_logs_folder/logs
            ''',
        epilog='!!! Location should be in the node\'s LOGS folder !!!\n',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '--path',
        required=False,
        type=validate_folder_path,
        help='Path to the logs folder.'
    )
    args = parser.parse_args()

    if args.path:
        current_folder = args.path
    else:
        current_folder = os.getcwd()

    try:
        node_name = current_folder.rsplit('--', 1)[1].replace('/logs', '')
    except IndexError:
        node_name = ''

    if ('validator' in node_name or 'observer' in node_name) and current_folder.endswith('/logs'):
        selected_folder = current_folder
        node_logs_checker: NodeLogsChecker = NodeLogsChecker.from_node_logs(node_name, 'test_run', selected_folder)
        node_logs_checker.write_node_report_json(selected_folder)
    else:
        print('Invalid folder')
