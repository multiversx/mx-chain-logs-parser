from datetime import datetime, timedelta
from multiversx_logs_parser_tools.archive_handler import ArchiveHandler

from .counter_checker import CounterChecker, CounterParser


class CounterArchiveHandler(ArchiveHandler):
    def __init__(self, checker: CounterChecker, logs_path: str):
        self.checker = checker
        # self.shard_data = ShardData()
        super().__init__(checker, logs_path)

    def process_node_data(self):
        """Process the parsed data for a single node."""
        # node_data = HeaderData()
        # node_data.header_dictionary = self.checker.parsed
        # self.shard_data.add_node(node_data)
        pass


if __name__ == "__main__":
    time_started = datetime.now()
    print('Starting log entry analysis...')
    args = CounterArchiveHandler.get_path()
    counter_checker = CounterChecker(CounterParser, args)
    handler = CounterArchiveHandler(counter_checker, args.path)
    handler.handle_logs()
    print(f'Archive checked successfully: {timedelta(seconds=(datetime.now() - time_started).total_seconds())}s')
