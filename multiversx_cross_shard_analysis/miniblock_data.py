from enum import Enum
from typing import Any

from multiversx_cross_shard_analysis.constants import COLORS_MAPPING, TYPE_NAMES, Colors
from multiversx_cross_shard_analysis.decode_reserved import \
    get_default_decoded_data


class MiniblockData:

    def __init__(self, miniblocks: dict[str, dict[str, Any]]):
        self.miniblocks = miniblocks
        self.verify_miniblocks()

    def verify_miniblocks(self) -> None:
        for mb_hash, mb_info in self.miniblocks.items():
            mb_info['hasAlarm'] = False
            mb_info['mentioned'] = sorted(mb_info.get('mentioned', []), key=lambda x: (x[1].get('epoch', 0), x[1].get('round', 0)))
            last_round = -1
            for mention_type, header in mb_info.get('mentioned', []):
                if last_round == -1:
                    mb_info['first_seen_round'] = header.get('round')
                    mb_info['last_seen_round'] = header.get('round')
                    mb_info['first_seen_epoch'] = header.get('epoch')
                    mb_info['nonce'] = header.get('nonce')
                    mb_info['senderShardID'] = header.get('shard_id')
                elif header.get('round') - last_round > 1:
                    mb_info['hasAlarm'] = True
                last_round = header.get('round')
                mb_info['last_seen_round'] = last_round

    def get_color_for_state(self, mention_type: str, tx_count: int, header: dict[str, Any]) -> Colors:
        reserved = header.get('reserved', {})
        if reserved == {}:
            reserved = get_default_decoded_data(tx_count=tx_count)
            if "meta" in mention_type:
                if 'exec' in mention_type:
                    color = Colors.meta_origin_exec_committed if mention_type.startswith('meta_origin') else Colors.meta_dest_exec_committed
                else:
                    color = Colors.meta_origin_committed if mention_type.startswith('meta_origin') else Colors.meta_dest_committed
            else:
                if 'exec' in mention_type:
                    color = Colors.origin_exec_final if mention_type.startswith('origin') else Colors.dest_exec_final
                else:
                    color = Colors.origin_final if mention_type.startswith('origin') else Colors.dest_final
        else:
            # execution_type = header.get('reserved', {}).get('ExecutionType', '')
            state = header.get('reserved', {}).get('State', '')
            if 'exec' in mention_type:
                if state == 'Proposed':
                    color = Colors.origin_exec_proposed if mention_type.startswith('origin') else Colors.dest_exec_proposed
                elif state == 'PartialExecuted':
                    color = Colors.origin_exec_partial_executed if mention_type.startswith('origin') else Colors.dest_exec_partial_executed
                else:
                    color = Colors.origin_exec_final if mention_type.startswith('origin') else Colors.dest_exec_final
            else:
                if state == 'Proposed':
                    color = Colors.origin_proposed if mention_type.startswith('origin') else Colors.dest_proposed
                elif state == 'PartialExecuted':
                    color = Colors.origin_partial_executed if mention_type.startswith('origin') else Colors.dest_partial_executed
                else:
                    color = Colors.origin_final if mention_type.startswith('origin') else Colors.dest_final
        return color

    def get_data_for_round_report(self) -> dict[str, Any]:
        report = {}
        for mb_hash, mb_info in self.miniblocks.items():
            for mention_type, header in mb_info.get('mentioned', []):
                if "proposed" in mention_type:
                    continue

                epoch = header.get('epoch')
                if epoch not in report:
                    report[epoch] = {}
                round_number = header.get('round')
                if round_number not in report[epoch]:
                    report[epoch][round_number] = {}
                shard = header.get('shard_id')
                if shard not in report[epoch][round_number]:
                    report[epoch][round_number][shard] = []

                color = COLORS_MAPPING[self.get_color_for_state(mention_type, mb_info['txCount'], header)]
                report[epoch][round_number][shard].append((mb_hash, color))
        return report

    def get_data_for_detail_report(self) -> dict[str, list[dict[str, Any]]]:
        report = {}
        for mb_hash, mb_info in self.miniblocks.items():
            origin_epoch = None

            mb_data = {
                "hash": mb_hash,
                "first_seen_round": None,
                "last_seen_round": None,
                "receiverShardID": mb_info['receiverShardID'],
                "senderShardID": mb_info['senderShardID'],
                "txCount": mb_info['txCount'],
                "type": mb_info['type'],
                "mentioned": {},
            }
            for mention_type, header in mb_info.get('mentioned', []):
                epoch = header.get('epoch')
                if epoch is not None and (origin_epoch is None or epoch < origin_epoch):
                    origin_epoch = epoch
                round_number = header.get('round')
                if mb_data['first_seen_round'] is None or round_number < mb_data['first_seen_round']:
                    mb_data['first_seen_round'] = round_number
                if mb_data['last_seen_round'] is None or round_number > mb_data['last_seen_round']:
                    mb_data['last_seen_round'] = round_number
                if round_number not in mb_data['mentioned']:
                    mb_data['mentioned'][round_number] = []

                color = COLORS_MAPPING[self.get_color_for_state(mention_type, mb_info['txCount'], header)]
                reserved = header.get('reserved')
                if reserved == {}:
                    reserved = get_default_decoded_data(tx_count=mb_info['txCount'])
                mb_data['mentioned'][round_number].append((mention_type, f"txs {reserved['IndexOfFirstTxProcessed']}–{reserved['IndexOfLastTxProcessed']} / {mb_info['txCount']}", color))

            if not origin_epoch:
                print(f"Warning: origin_epoch not found for miniblock {mb_hash}")
                continue
            if origin_epoch not in report:
                report[origin_epoch] = []
            report[origin_epoch].append(mb_data)

        for epoch, mb_list in report.items():
            mb_list.sort(key=lambda x: x['first_seen_round'])
        return report

    def get_data_for_header_report(self) -> dict[int, dict[int, Any]]:
        report: dict[int, dict[int, Any]] = {}

        for mb_hash, mb_info in self.miniblocks.items():
            nonce = mb_info['nonce']
            shard_id = mb_info['senderShardID']
            epoch = mb_info['first_seen_epoch']
            for mention_type, header in mb_info.get('mentioned', []):
                if "proposed" in mention_type:
                    continue

                if epoch not in report:
                    report[epoch] = {}

                if shard_id not in report[epoch]:
                    report[epoch][shard_id] = {}

                if nonce not in report[epoch][shard_id]:
                    report[epoch][shard_id][nonce] = {}

                round_number = header.get('round')
                if round_number not in report[epoch][shard_id][nonce]:
                    report[epoch][shard_id][nonce][round_number] = []

                color = COLORS_MAPPING[self.get_color_for_state(mention_type, mb_info['txCount'], header)]
                label = f'Shard {header["shard_id"]}' if header["shard_id"] != 4294967295 else "MetaShard"
                if mb_info['type'] != 0:
                    label += f' ({TYPE_NAMES[mb_info["type"]]})'

                report[epoch][shard_id][nonce][round_number].append((label, mb_hash[:15] + '...', color))

        return sort_report(report)


def sort_report(report: dict[int, dict[int, Any]]) -> dict[int, dict[int, Any]]:
    out: dict[int, dict[int, Any]] = {}

    for epoch in sorted(report.keys()):
        out[epoch] = {}

        # metas hard (4294967295) last
        shard_ids = sorted(
            report[epoch].keys(),
            key=lambda s: (s == 4294967295, s),
        )

        for shard_id in shard_ids:
            out[epoch][shard_id] = {}

            for nonce in sorted(report[epoch][shard_id].keys()):
                rounds = report[epoch][shard_id][nonce]

                out[epoch][shard_id][nonce] = {
                    r: rounds[r]
                    for r in sorted(rounds.keys())
                }

    return out
