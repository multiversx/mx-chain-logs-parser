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

    def add_proposed_header(self, header: dict[str, Any]):
        nonce = get_value('nonce', header)
        if nonce in self.seen_headers['proposed_headers']:
            return
        self.header_dictionary['proposed_headers'].append(header)
        self.seen_headers['proposed_headers'].add(nonce)

    def add_commited_header(self, header: dict[str, Any]):
        nonce = get_value('nonce', header)
        if nonce in self.seen_headers['commited_headers']:
            return
        self.header_dictionary['commited_headers'].append(header)
        self.seen_headers['commited_headers'].add(nonce)


class ShardData:
    def __init__(self):
        self.parsed_headers = {0: HeaderData(), 1: HeaderData(), 2: HeaderData(), 4294967295: HeaderData()}

    def add_node(self, node_data: HeaderData):
        for header_status in node_data.header_dictionary.keys():
            for header in node_data.header_dictionary[header_status]:
                shard_id = get_shard_id(header)
                if header_status == 'commited_headers':
                    self.parsed_headers[shard_id].add_commited_header(header)
                elif header_status == 'proposed_headers':
                    self.parsed_headers[shard_id].add_proposed_header(header)
                else:
                    print(f"Warning: Unknown header status {header_status} in header: round = {get_value('round', header)}, nonce = {get_value('nonce', header)}")
