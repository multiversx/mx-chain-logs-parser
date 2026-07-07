
import argparse
import os
import tarfile
import zipfile
from typing import TypeVar

from .aho_corasik_parser import AhoCorasickParser
from .helpers import validate_file_path
from .node_logs_checker import NodeLogsChecker

P = TypeVar("P", bound=AhoCorasickParser)


class ArchiveHandler:
    def __init__(self, checker: NodeLogsChecker[P], logs_path: str):
        self.logs_path = logs_path
        self.run_name = self._extract_run_name(logs_path)
        self.checker = checker

    @staticmethod
    def _extract_run_name(path: str) -> str:
        name = os.path.basename(path)
        for ext in ['.tar.gz', '.tgz', '.zip', '.tar']:
            if name.endswith(ext):
                return name[:-len(ext)]
        return name

    def handle_logs(self):
        """Loop through nodes in the archive and process logs for each node."""
        path = self.logs_path

        if path.endswith('.zip'):
            self._handle_zip(path)
        elif path.endswith(('.tar', '.tar.gz', '.tgz')):
            self._handle_tar(path)
        else:
            raise ValueError(f"Unsupported archive format: {path}")

        self.process_run_data()

    def _handle_zip(self, path: str):
        with zipfile.ZipFile(path, 'r') as zip_file:
            for file_name in zip_file.namelist():
                if file_name.endswith(".tar.gz") and not file_name.startswith("__MACOSX/"):
                    node_name = file_name.replace(".tar.gz", "").rsplit("--", 1)[1]
                    print(f"Processing node {node_name}")
                    with zip_file.open(file_name) as tar_file_io:
                        self._process_node(tar_file_io, node_name)

    def _handle_tar(self, path: str):
        with tarfile.open(path, 'r:*') as tar_file:
            for member in tar_file.getmembers():
                if member.isfile() and member.name.endswith(".tar.gz") and not member.name.startswith("__MACOSX/"):
                    node_name = member.name.replace(".tar.gz", "").rsplit("--", 1)[1]
                    print(f"Processing node {node_name}")
                    tar_gz_io = tar_file.extractfile(member)
                    if tar_gz_io is None:
                        continue
                    self._process_node(tar_gz_io, node_name)

    def _process_node(self, fileobj, node_name: str):
        args = argparse.Namespace(
            node_name=node_name,
            run_name=self.run_name,
        )
        self.checker.reset_node(args)
        self.checker.handle_node_from_archive(fileobj)
        self.checker.post_process_node_logs()
        self.process_node_data()

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
