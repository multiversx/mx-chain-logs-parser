from typing import Any


class HeaderData:
    def __init__(self):
        self.header_dictionary = {
            'proposed_headers': [],
            'commited_headers': []
        }

    def reset(self):
        self.header_dictionary = {
            'proposed_headers': [],
            'commited_headers': []
        }

    def add_proposed_header(self, header: dict[str, Any]):
        self.header_dictionary['proposed_headers'].append(header)

    def add_commited_header(self, header: dict[str, Any]):
        self.header_dictionary['commited_headers'].append(header)
