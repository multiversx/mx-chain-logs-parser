from enum import Enum
from typing import Any


def get_value(variable_name: str, header: dict[str, Any]) -> str:
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


MiniBlockTypes = Enum("MiniBlockType", ['MiniBlockHeaders', 'ShardInfo', 'ExecutionResults'])


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
        header_struct = Header(header)
        for mb_type, miniblocks in header_struct.miniblocks.items():
            for mb in miniblocks:
                mb_hash = mb.get('hash')
                if mb_hash not in self.seen_miniblock_hashes:
                    self.seen_miniblock_hashes.add(mb_hash)
                    self.miniblocks[mb_hash] = mb.copy()
                    self.miniblocks[mb_hash]['mentioned'] = []
                mention_type = 'notarized' if mb_type == MiniBlockTypes.ShardInfo else status
                self.miniblocks[mb_hash]['mentioned'].append((mention_type, header_struct.metadata))


class Header:
    def __init__(self, header: dict[str, Any]):
        self.metadata: dict[str, Any] = self.get_header_metadata(header)
        self.miniblocks: dict[str, list[dict[str, Any]]] = self.get_miniblocks(header)

    def get_header_metadata(self, header: dict[str, Any]) -> dict[str, Any]:
        if Header.isHeaderV2(header):
            header = header['header']
        return {
            "nonce": header.get('nonce', 0),
            "round": header.get('round', 0),
            "epoch": header.get('epoch', 0),
            "shard_id": header.get('shardID', 4294967295),
        }

    def get_miniblocks(self, header: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
        miniblocks = {}
        if Header.isHeaderV2(header):
            header = header['header']
        miniblocks[MiniBlockTypes.MiniBlockHeaders] = header.get('miniBlockHeaders', [])
        if Header.isMetaHeader(header):
            miniblocks[MiniBlockTypes.ShardInfo] = []
            for shard_header in header['shardInfo']:
                miniblocks[MiniBlockTypes.ShardInfo].extend(shard_header.get('shardMiniBlockHeaders', []))
        return miniblocks

    @staticmethod
    def isHeaderV2(header: dict[str, Any]) -> bool:
        return 'header' in header

    @staticmethod
    def isMetaHeader(header: dict[str, Any]) -> bool:
        return 'shardInfo' in header
