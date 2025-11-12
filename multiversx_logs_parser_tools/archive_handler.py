
from pathlib import Path
from node_logs_checker import NodeLogsChecker
import argparse
from datetime import datetime, timedelta
import re
import zipfile
from aho_corasick_checker import AhoCorasickChecker
from helpers import validate_file_path
from master.master_report import Report


class ArchiveHandler:
    def __init__(self, checker: NodeLogsChecker, logs_path: str):
        self.logs_path = logs_path
        self.ahochorasick_checker = AhoCorasickChecker()
        zip_name_pattern = r'.*/(.*?).zip'
        match = re.match(zip_name_pattern, self.logs_path)
        self.run_name = match.group(1) if match else 'unknown-zip-name'

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
                        args = {
                            'node_name': node_name,
                            'run_name': self.run_name,
                        }
                        node_logs_checker = NodeLogsChecker(**args)
                        node_logs_checker.handle_node_from_archive(tar_file_io)
                    node_logs_checker.post_process_node_logs()


if __name__ == "__main__":
    time_started = datetime.now()
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

    args = parser.parse_args()

    handler = ArchiveHandler(args.path)
    handler.handle_logs()
    print(f'Archive checked succesfully: {timedelta(seconds=(datetime.now() - time_started).total_seconds())}s')

    report = Report(handler.run_name)
    report.gather_data()
    report_file = Path(f'./{report.get_name_of_the_report()}.txt')
    report.execute_report(report_file)
    print(f"\nReport generated: {report_file}")
