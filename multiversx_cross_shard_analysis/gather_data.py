from datetime import datetime, timedelta
from multiversx_logs_parser_tools.archive_handler import ArchiveHandler

from .header_analysis_checker import HeaderAnalysisChecker

from .header_analysis_parser import HeaderAnalysisParser


def gather_data():
    time_started = datetime.now()
    print('Starting cross-shard analysis...')
    args = ArchiveHandler.get_path()
    header_checker = HeaderAnalysisChecker(HeaderAnalysisParser, args)
    handler = ArchiveHandler(header_checker, args.path)
    handler.handle_logs()
    print(f'Archive checked successfully: {timedelta(seconds=(datetime.now() - time_started).total_seconds())}s')


if __name__ == "__main__":
    gather_data()
