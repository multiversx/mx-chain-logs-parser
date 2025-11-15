from datetime import datetime, timedelta


from .header_analysis_archive_handler import HeaderAnalysisArchiveHandler

from .header_analysis_checker import HeaderAnalysisChecker
from .header_analysis_parser import HeaderAnalysisParser


def gather_data():
    time_started = datetime.now()
    print('Starting cross-shard analysis...')
    args = HeaderAnalysisArchiveHandler.get_path()
    header_checker = HeaderAnalysisChecker(HeaderAnalysisParser, args)
    handler = HeaderAnalysisArchiveHandler(header_checker, args.path)
    handler.handle_logs()
    print(f'Archive checked successfully: {timedelta(seconds=(datetime.now() - time_started).total_seconds())}s')


if __name__ == "__main__":
    gather_data()
