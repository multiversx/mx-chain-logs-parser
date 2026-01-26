import json
from pathlib import Path

from multiversx_logs_parser_tools.archive_handler import ArchiveHandler

from .header_analysis_checker import HeaderAnalysisChecker
from .header_structures import HeaderData, ShardData


class HeaderAnalysisArchiveHandler(ArchiveHandler):
    def __init__(self, checker: HeaderAnalysisChecker, logs_path: str):
        self.checker = checker
        self.shard_data = ShardData()

        super().__init__(checker, logs_path)

    def process_node_data(self):
        """Process the parsed data for a single node."""
        node_data = HeaderData()
        node_data.header_dictionary = self.checker.parsed
        node_data.metaheaders = self.checker.metaheaders
        self.shard_data.add_node(node_data)

    def process_run_data(self):
        """Process the parsed data for the entire run."""
        self.write_run_json()

    def write_run_json(self, path=''):
        for shard_id, header_data in self.shard_data.parsed_headers.items():
            run_data = {
                "run_name": self.run_name,
                "shard_id": shard_id,
                "shards": header_data.header_dictionary,
                "metablocks": self.shard_data.metablock_headers,
            }
            shard_reports_path = f'./Reports/{self.run_name}/Shards'
            output_file = Path(f'{shard_reports_path}/{shard_id}_report.json')
            directory = output_file.parent
            directory.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w') as f:
                json.dump(run_data, f, indent=4)
            print(f"Shard data for shard {shard_id} written to {output_file}")
        miniblocks_reports_path = f'./Reports/{self.run_name}/Miniblocks'
        output_file = Path(f'{miniblocks_reports_path}/miniblocks_report.json')
        directory = output_file.parent
        directory.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump({
                "run_name": self.run_name,
                "miniblocks": self.shard_data.miniblocks
            }, f, indent=4)
        print(f"Miniblock data written to {output_file}")
