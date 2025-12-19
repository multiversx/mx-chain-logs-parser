import os
from datetime import datetime, timedelta

from multiversx_cross_shard_analysis.headers_timeline_report import \
    build_nonce_timeline_pdf
from multiversx_cross_shard_analysis.miniblock_data import MiniblockData
from multiversx_cross_shard_analysis.miniblocks_round_report import \
    build_report
from multiversx_cross_shard_analysis.miniblocks_timeline_report import \
    build_pdf_from_miniblocks

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

    # Generate reports
    mb_data = MiniblockData(handler.shard_data.miniblocks).get_data_for_round_report()
    out_folder = os.path.join(handler.run_name, "MiniblocksShardTimeline")
    out_folder = os.path.join('Reports', out_folder)
    os.makedirs(out_folder, exist_ok=True)

    # generate PDFs per epoch
    for epoch in sorted(mb_data.keys()):
        print(f"Epoch: {epoch}")
        report_dict = mb_data[epoch]
        outfile = os.path.join(out_folder, f"shards_timeline_report_{epoch}.pdf")
        build_report(int(epoch), report_dict, shards=[0, 1, 2, 4294967295], outname=outfile)
        print("→", outfile)

    mb_data = MiniblockData(handler.shard_data.miniblocks).get_data_for_detail_report()
    out_folder = os.path.join(handler.run_name, "MiniblocksTimelineDetail")
    out_folder = os.path.join('Reports', out_folder)
    os.makedirs(out_folder, exist_ok=True)

    for epoch in sorted(mb_data.keys()):
        print(f"Epoch: {epoch}")
        outfile = os.path.join(out_folder, f"miniblock_timeline_report_epoch_{epoch}.pdf")
        build_pdf_from_miniblocks(int(epoch), mb_data[epoch], outname=outfile)
        print("→", outfile)

    input_data = handler.shard_data.get_data_for_header_horizontal_report()
    out_folder = os.path.join(handler.run_name, "NonceTimeline")
    out_folder = os.path.join('Reports', out_folder)
    os.makedirs(out_folder, exist_ok=True)

    for epoch in sorted(input_data.keys()):
        print(f"Epoch: {epoch}")
        outfile = os.path.join(out_folder, f"nonce_timeline_report_{epoch}.pdf")
        build_nonce_timeline_pdf(input_data[epoch], outname=outfile)
        print("→", outfile)


if __name__ == "__main__":
    gather_data()
