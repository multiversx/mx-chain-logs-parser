
from typing import Any

from multiversx_cross_shard_analysis.constants import (COLORS_MAPPING,
                                                       TYPE_NAMES, Colors)
from multiversx_cross_shard_analysis.decode_reserved import \
    get_default_decoded_data
from multiversx_cross_shard_analysis.issues import Issues


class MiniblockData:

    def __init__(self, miniblocks: dict[str, dict[str, Any]]):
        self.miniblocks = miniblocks
        self.verify_miniblocks()

    def verify_miniblocks(self) -> None:
        for mb_hash, mb_info in self.miniblocks.items():
            mb_info['mentioned'] = sorted(mb_info.get('mentioned', []), key=lambda x: (x[1].get('epoch', 0), x[1].get('round', 0)))
            mentioning_header = mb_info['mentioned'][0][1] if mb_info['mentioned'] else None
            if mentioning_header:
                mb_info['first_seen_round'] = mentioning_header.get('round')
                mb_info['first_seen_epoch'] = mentioning_header.get('epoch')
                mb_info['nonce'] = mentioning_header.get('nonce')
                mb_info['senderShardID'] = mentioning_header.get('shard_id')
            mb_info['alarms'] = []

            # Perform the configurable checks
            for issue in Issues:
                if issue.run_check(issue, mb_info):
                    mb_info['alarms'].append(issue.name)

            # Set the general alarm flag if any issues were found
            mb_info['hasAlarm'] = len(mb_info['alarms']) > 0

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
                "hasAlarm": mb_info['hasAlarm'],
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

    def get_data_for_header_report(self) -> tuple[dict[int, dict[int, Any]], dict[int, set[int]]]:
        report: dict[int, dict[int, Any]] = {}

        nonce_alarms = dict[int, set[int]]()
        for mb_hash, mb_info in self.miniblocks.items():
            nonce = mb_info['nonce']
            shard_id = mb_info['senderShardID']
            epoch = mb_info['first_seen_epoch']
            hasAlarm = mb_info['hasAlarm']
            if hasAlarm:
                nonce_alarms.setdefault(shard_id, set()).add(nonce)

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
                else:
                    label += f' ({mb_info["senderShardID"]} -> {mb_info["receiverShardID"]})'

                report[epoch][shard_id][nonce][round_number].append((label, mb_hash[:15] + '...', color))

        return sort_any(report), nonce_alarms

    def get_data_for_header_alarms_report(self) -> dict[int, Any]:
        report: dict[int, Any] = {}
        nonce_alarms: dict[int, dict[int, set]] = {}

        seen_miniblocks = set[str]()

        for mb_hash, mb_info in [(hash, miniblock) for hash, miniblock in self.miniblocks.items() if miniblock['hasAlarm']]:
            nonce = mb_info['nonce']
            shard_id = mb_info['senderShardID']
            epoch = mb_info['first_seen_epoch']

            hasAlarm = mb_info['hasAlarm']
            alarms = mb_info['alarms']
            if hasAlarm:
                shard_map = nonce_alarms.setdefault(shard_id, {})
                shard_map.setdefault(nonce, set()).update(alarms)

            for mention_type, header in mb_info.get('mentioned', []):
                if "proposed" in mention_type:
                    continue

                # prepare epoch level
                if epoch not in report:
                    report[epoch] = {}
                    for issue in Issues:
                        report[epoch][issue.name] = {}

                color = COLORS_MAPPING[self.get_color_for_state(mention_type, mb_info['txCount'], header)]
                label = f'Shard {header["shard_id"]}' if header["shard_id"] != 4294967295 else "MetaShard"

                if mb_info['type'] != 0:
                    label += f' ({TYPE_NAMES[mb_info["type"]]})'
                else:
                    label += f' ({mb_info["senderShardID"]} -> {mb_info["receiverShardID"]})'

                for issue in mb_info['alarms']:
                    if shard_id not in report[epoch][issue]:
                        report[epoch][issue][shard_id] = {}

                    if nonce not in report[epoch][issue][shard_id]:
                        report[epoch][issue][shard_id][nonce] = {}

                    round_number = header.get('round')
                    if round_number not in report[epoch][issue][shard_id][nonce]:
                        report[epoch][issue][shard_id][nonce][round_number] = []

                    report[epoch][issue][shard_id][nonce][round_number].append((label, mb_hash[:15] + '...', color))
                    seen_miniblocks.add(mb_hash)

        for mb_hash in [item for item in self.miniblocks.keys() if item not in seen_miniblocks and self.miniblocks[item]['nonce'] in nonce_alarms.get(self.miniblocks[item]['senderShardID'], set())]:
            mb_info = self.miniblocks[mb_hash]
            nonce = mb_info['nonce']
            shard_id = mb_info['senderShardID']
            epoch = mb_info['first_seen_epoch']

            for mention_type, header in mb_info.get('mentioned', []):
                if "proposed" in mention_type:
                    continue

                # prepare epoch level
                if epoch not in report:
                    report[epoch] = {}
                    for issue in Issues:
                        report[epoch][issue.name] = {}

                color = COLORS_MAPPING[self.get_color_for_state(mention_type, mb_info['txCount'], header)]
                label = f'Shard {header["shard_id"]}' if header["shard_id"] != 4294967295 else "MetaShard"

                if mb_info['type'] != 0:
                    label += f' ({TYPE_NAMES[mb_info["type"]]})'
                else:
                    label += f' ({mb_info["senderShardID"]} -> {mb_info["receiverShardID"]})'

                for issue in nonce_alarms[shard_id][nonce]:
                    if shard_id not in report[epoch][issue]:
                        report[epoch][issue][shard_id] = {}

                    if nonce not in report[epoch][issue][shard_id]:
                        report[epoch][issue][shard_id][nonce] = {}

                    round_number = header.get('round')
                    if round_number not in report[epoch][issue][shard_id][nonce]:
                        report[epoch][issue][shard_id][nonce][round_number] = []

                    report[epoch][issue][shard_id][nonce][round_number].append((label, mb_hash[:15] + '...', color))

        return sort_any(report)


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


def sort_report1(report: dict[int, dict[int, Any]]) -> dict[int, dict[int, Any]]:
    out: dict[int, dict[int, Any]] = {}

    for epoch in sorted(report.keys()):
        out[epoch] = {}

        for issue in sorted(report[epoch].keys()):
            out[epoch][issue] = {}
            # metas hard (4294967295) last
            shard_ids = sorted(
                report[epoch][issue].keys(),
                key=lambda s: (s == 4294967295, s),
            )

            for shard_id in shard_ids:
                out[epoch][issue][shard_id] = {}

                for nonce in sorted(report[epoch][issue][shard_id].keys()):
                    rounds = report[epoch][issue][shard_id][nonce]

                    out[epoch][issue][shard_id][nonce] = {
                        r: rounds[r]
                        for r in sorted(rounds.keys())
                    }

    return out


META_SHARD_ID = 4294967295


def sort_any(data: Any) -> Any:
    """
    Recursively sorts dictionaries and lists.
    - Dictionaries: Sorted by keys (Meta Shard always last).
    - Lists: Elements are recursively sorted.
    - Others: Returned as is.
    """
    # Case 1: It's a Dictionary
    if isinstance(data, dict):
        # Determine the sorted order of keys
        sorted_keys = sorted(
            data.keys(),
            key=lambda k: (
                # Rule: If key is the Meta Shard ID, put it last
                (k == META_SHARD_ID) if isinstance(k, int) else False,
                # Otherwise, sort naturally by value/string
                k
            )
        )
        # Rebuild dictionary recursively
        return {k: sort_any(data[k]) for k in sorted_keys}

    # Case 2: It's a List/Array
    elif isinstance(data, list):
        # Sort each item inside the list first
        processed_list = [sort_any(item) for item in data]
        try:
            # Try to sort the list itself if elements are comparable
            return sorted(processed_list)
        except TypeError:
            # If elements are non-comparable (e.g., list of dicts), return as is
            return processed_list

    # Case 3: Primitive types (int, str, bool, None)
    return data
