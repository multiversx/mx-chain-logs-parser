
import argparse
import re
import zipfile
from typing import TypeVar

from .aho_corasik_parser import AhoCorasickParser
from .helpers import validate_file_path
from .node_logs_checker import NodeLogsChecker

P = TypeVar("P", bound=AhoCorasickParser)


class ArchiveHandler:
    def __init__(self, checker: NodeLogsChecker[P], logs_path: str):
        self.logs_path = logs_path
        zip_name_pattern = r'.*/(.*?).zip'
        match = re.match(zip_name_pattern, self.logs_path)
        self.run_name = match.group(1) if match else 'unknown-zip-name'
        self.checker = checker

    def handle_logs(self):
        """Loop through nodes in the zip file and process logs for each node."""
        # Open the zip file and process tar.gz files inside it that each correspond to a node

        with zipfile.ZipFile(self.logs_path, 'r') as zip_file:
            # List all files inside the zip
            file_list = zip_file.namelist()

            for file_name in file_list:
                if file_name.endswith(".tar.gz"):
                    node_name = file_name.replace(".tar.gz", "").rsplit("--", 1)[1]
                    print(f"Processing node {node_name}")

                    # Open the tar.gz file as bytes
                    with zip_file.open(file_name) as tar_file_io:
                        args = argparse.Namespace(
                            node_name=node_name,
                            run_name=self.run_name,
                        )
                        self.checker.reset_node(args)
                        self.checker.handle_node_from_archive(tar_file_io)
                    self.checker.post_process_node_logs()
                    self.process_node_data()
        self.process_run_data()

    def process_node_data(self):
        """Process the parsed data for a single node."""
        pass

    def process_run_data(self):
        """Process the parsed data for the entire run."""
        pass

    @staticmethod
    def get_path() -> argparse.Namespace:
        parser = argparse.ArgumentParser(
            description='''
        Runs node log checks. Example script:

            python ansible/templates/logs-checker/archive_handler.py --path=logsPath/logs_archive.zip
        ''',
            epilog='\n',
            formatter_class=argparse.RawTextHelpFormatter
        )

        parser.add_argument(
            '--path',
            required=True,
            type=validate_file_path,
            help='Path to the run zip file.'
        )

        return parser.parse_args()
