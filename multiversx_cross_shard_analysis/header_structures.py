
from typing import Any

from multiversx_cross_shard_analysis.miniblock_data import MiniblockData
from multiversx_cross_shard_analysis.test_decode_reserved import \
    decode_reserved_field

from .constants import (COLORS_MAPPING, TYPE_NAMES, dest_shard, meta,
                        origin_shard)


def get_value(variable_name: str, header: dict[str, Any]) -> Any:
    return header['header'][variable_name] if 'header' in header else header[variable_name]


def get_shard_id(header: dict[str, Any]) -> int:
    return header['header']['shardID'] if 'header' in header else header.get('shardID', 4294967295)


class HeaderData:
    def __init__(self):
        self.header_dictionary = {
            'proposed_headers': [],
            'commited_headers': []
        }
        self.seen_headers: dict[str, set[str]] = {'proposed_headers': set(),
                                                  'commited_headers': set()}

    def reset(self):
        self.header_dictionary = {
            'proposed_headers': [],
            'commited_headers': []
        }
        self.seen_headers: dict[str, set[str]] = {'proposed_headers': set(),
                                                  'commited_headers': set()}

    def add_proposed_header(self, header: dict[str, Any]) -> bool:
        nonce = get_value('nonce', header)
        if nonce in self.seen_headers['proposed_headers']:
            return False
        self.header_dictionary['proposed_headers'].append(header)
        self.seen_headers['proposed_headers'].add(nonce)
        return True

    def add_commited_header(self, header: dict[str, Any]) -> bool:
        nonce = get_value('nonce', header)
        if nonce in self.seen_headers['commited_headers']:
            return False
        self.header_dictionary['commited_headers'].append(header)
        self.seen_headers['commited_headers'].add(nonce)
        return True


class ShardData:
    def __init__(self):
        self.parsed_headers = {0: HeaderData(), 1: HeaderData(), 2: HeaderData(), 4294967295: HeaderData()}
        self.miniblocks = {}
        self.seen_miniblock_hashes = set()

    def add_node(self, node_data: HeaderData):
        for header_status in node_data.header_dictionary.keys():
            for header in node_data.header_dictionary[header_status]:
                shard_id = get_shard_id(header)
                added = False
                if header_status == 'commited_headers':
                    added = self.parsed_headers[shard_id].add_commited_header(header)
                elif header_status == 'proposed_headers':
                    added = self.parsed_headers[shard_id].add_proposed_header(header)
                else:
                    print(f"Warning: Unknown header status {header_status} in header: round = {get_value('round', header)}, nonce = {get_value('nonce', header)}")
                if added:
                    self.add_miniblocks(header, header_status)

    def add_miniblocks(self, header: dict[str, Any], status: str):
        header_struct = Header(header, status)

        for mention_type, mb in header_struct.miniblocks:
            mb_hash = mb.get('hash')
            if mb_hash not in self.seen_miniblock_hashes:
                self.seen_miniblock_hashes.add(mb_hash)
                self.miniblocks[mb_hash] = mb.copy()
                self.miniblocks[mb_hash]['mentioned'] = []
            metadata = header_struct.metadata.copy()
            metadata["reserved"] = decode_reserved_field(mb.get("reserved", ""), mb.get("txCount", 0))
            self.miniblocks[mb_hash]['mentioned'].append((mention_type, metadata))

    def get_data_for_header_vertical_report(self) -> dict[str, dict[int, Any]]:
        miniblocks = MiniblockData(self.miniblocks)
        report: dict[str, dict[int, Any]] = {}
        last_epoch = None

        for shard_id, header_data in self.parsed_headers.items():
            header_group_count = 0
            header_count = 0
            header_group_name = ""
            last_epoch = None

            for header in sorted(header_data.header_dictionary['commited_headers'],
                                 key=lambda x: get_value('nonce', x)):

                epoch = get_value('epoch', header)

                # reset counters when epoch changes
                if epoch != last_epoch:
                    header_group_count = 0
                    header_count = 0
                    header_group_name = ""
                    last_epoch = epoch

                # ensure epoch entry exists and contains all shards as keys
                if epoch not in report:
                    report[epoch] = {sid: {} for sid in self.parsed_headers.keys()}

                if get_value('miniBlockHeaders', header) == []:
                    continue

                nonce = get_value('nonce', header)
                round_num = get_value('round', header)
                print(f"Processing header: epoch={epoch}, shard={shard_id}, nonce={nonce}, round={round_num}")

                # build result for this header (only cross-shard miniblocks)
                result: dict[int, list] = {}
                for miniblock in [mb for mb in get_value('miniBlockHeaders', header) if mb.get('senderShardID') == shard_id and mb.get('receiverShardID') != mb.get('senderShardID')]:
                    print(f"  Processing miniblock: hash={miniblock.get('hash')}, senderShardID={miniblock.get('senderShardID')}, receiverShardID={miniblock.get('receiverShardID')}")
                    mb_hash = miniblock.get('hash')
                    for mention_type, metadata in self.miniblocks[mb_hash]['mentioned']:
                        # skip proposed mentions
                        if 'proposed' in mention_type:
                            continue

                        rn = metadata['round']
                        color = miniblocks.get_color_for_state(mention_type, miniblock['txCount'], metadata)
                        shard_name = f'Shard {metadata["shard_id"]}' if metadata["shard_id"] != 4294967295 else "MetaShard"
                        # append tuple (label, info, color)
                        result.setdefault(rn, []).append((shard_name, mb_hash[:15] + '...', COLORS_MAPPING[color]))

                # if result empty -> we don't include this nonce at all, don't count it
                if not result:
                    continue

                # --- Add this nonce to the report and handle grouping ---
                # if group start (every 5 actual added nonces)
                group_size = 5
                if header_count % group_size == 0:
                    header_group_count += 1
                    header_group_name = f"Nonces {nonce}"
                    # initialize structure for this group
                    report[epoch][shard_id][header_group_count] = {
                        'group_name': header_group_name,
                        'rounds': (round_num, round_num),
                        'nonces': {}
                    }
                    print(f"Creating new header group: {header_group_name}")
                else:
                    # extend existing group's name
                    header_group_name += f" - {nonce}"
                    report[epoch][shard_id][header_group_count]['group_name'] = header_group_name

                # store the nonce's data
                report[epoch][shard_id][header_group_count]['nonces'][nonce] = result

                # update group's rounds min/max based on result keys
                min_r, max_r = report[epoch][shard_id][header_group_count]['rounds']
                actual_min = min(result.keys())
                actual_max = max(result.keys())
                report[epoch][shard_id][header_group_count]['rounds'] = (min(min_r, actual_min), max(max_r, actual_max))

                # increment header_count because we added this nonce
                header_count += 1

        return report

    def get_data_for_header_horizontal_report(self) -> dict[str, dict[int, Any]]:
        miniblocks = MiniblockData(self.miniblocks)
        report: dict[str, dict[int, Any]] = {}

        for shard_id, header_data in self.parsed_headers.items():

            for header in sorted(header_data.header_dictionary['commited_headers'],
                                 key=lambda x: get_value('nonce', x)):

                epoch = get_value('epoch', header)

                # ensure epoch entry exists and contains all shards as keys
                if epoch not in report:
                    report[epoch] = {sid: {} for sid in self.parsed_headers.keys()}

                if get_value('miniBlockHeaders', header) == []:
                    continue

                nonce = get_value('nonce', header)
                round_num = get_value('round', header)
                print(f"Processing header: epoch={epoch}, shard={shard_id}, nonce={nonce}, round={round_num}")

                # build result for this header (only cross-shard miniblocks)
                result: dict[int, list] = {}
                for miniblock in [mb for mb in get_value('miniBlockHeaders', header) if mb.get('senderShardID') == shard_id and mb.get('receiverShardID') != mb.get('senderShardID')]:
                    print(f"  Processing miniblock: hash={miniblock.get('hash')}, senderShardID={miniblock.get('senderShardID')}, receiverShardID={miniblock.get('receiverShardID')}")
                    mb_hash = miniblock.get('hash')
                    for mention_type, metadata in self.miniblocks[mb_hash]['mentioned']:
                        # skip proposed mentions
                        if 'proposed' in mention_type:
                            continue

                        rn = metadata['round']
                        color = miniblocks.get_color_for_state(mention_type, miniblock['txCount'], metadata)
                        label = f'Shard {metadata["shard_id"]}' if metadata["shard_id"] != 4294967295 else "MetaShard"
                        if miniblock['type'] != 0:
                            label += f' ({TYPE_NAMES[miniblock["type"]]})'
                        # append tuple (label, info, color)
                        result.setdefault(rn, []).append((label, mb_hash[:15] + '...', COLORS_MAPPING[color]))

                # if result empty -> we don't include this nonce at all, don't count it
                if not result:
                    continue

                # sort rounds in result
                result = dict(sorted(result.items()))

                # previous nonce round check - skip if miniblock from a previous nonce
                if list(result.keys())[0] < round_num:
                    continue

                # store the nonce's data
                report[epoch][shard_id][nonce] = result

        return report


class Header:
    def __init__(self, header: dict[str, Any], status: str):
        self.metadata: dict[str, Any] = self.get_header_metadata(header)
        self.miniblocks: list[tuple[str, dict[str, Any]]] = self.get_miniblocks(header, status)

    def get_header_metadata(self, header: dict[str, Any]) -> dict[str, Any]:
        if Header.isHeaderV2(header):
            header = header['header']
        return {
            "nonce": header.get('nonce', 0),
            "round": header.get('round', 0),
            "epoch": header.get('epoch', 0),
            "shard_id": header.get('shardID', 4294967295),
        }

    def get_miniblocks(self, header: dict[str, Any], status: str) -> list[tuple[str, dict[str, Any]]]:
        metadata = self.metadata
        miniblocks = []
        if Header.isHeaderV2(header):
            header = header['header']
        for miniblock in header.get('miniBlockHeaders', []):
            miniblock_mention = f'{origin_shard if metadata['shard_id'] == miniblock['senderShardID'] else dest_shard}_{status}'
            miniblocks.append((miniblock_mention, miniblock))
        if Header.isMetaHeader(header):
            for shard_header in header['shardInfo']:
                shard_metadata = self.get_header_metadata(shard_header)
                for miniblock in shard_header.get('shardMiniBlockHeaders', []):
                    miniblock_mention = f'{meta}_{origin_shard if shard_metadata['shard_id'] == miniblock['senderShardID'] else dest_shard}_{status}'
                    miniblocks.append((miniblock_mention, miniblock))
        return miniblocks

    @staticmethod
    def isHeaderV2(header: dict[str, Any]) -> bool:
        return 'header' in header

    @staticmethod
    def isMetaHeader(header: dict[str, Any]) -> bool:
        return 'shardInfo' in header

    @staticmethod
    def isHeaderV3(header: dict[str, Any]) -> bool:
        return 'executionResults' in header and 'shardInfoProposal' not in header

    @staticmethod
    def isMetaHeaderV3(header: dict[str, Any]) -> bool:
        return 'shardInfoProposal' in header
